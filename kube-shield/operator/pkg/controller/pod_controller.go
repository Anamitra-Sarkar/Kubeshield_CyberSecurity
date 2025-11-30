package controller

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/go-logr/logr"
	corev1 "k8s.io/api/core/v1"
	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	shieldv1alpha1 "github.com/kubeshield/operator/pkg/apis/shield/v1alpha1"
)

// PodReconciler reconciles Pod objects based on ShieldPolicy configurations
type PodReconciler struct {
	client.Client
	Scheme          *runtime.Scheme
	AuditServiceURL string
	HTTPClient      *http.Client
}

// SecurityEvent represents a security event to be sent to the audit service
type SecurityEvent struct {
	Timestamp   string `json:"timestamp"`
	EventType   string `json:"eventType"`
	Severity    string `json:"severity"`
	PodName     string `json:"podName"`
	Namespace   string `json:"namespace"`
	Container   string `json:"container,omitempty"`
	Image       string `json:"image,omitempty"`
	Reason      string `json:"reason"`
	Action      string `json:"action"`
	PolicyName  string `json:"policyName"`
	NodeName    string `json:"nodeName,omitempty"`
	Description string `json:"description"`
}

// NewPodReconciler creates a new PodReconciler with dependency injection
func NewPodReconciler(
	client client.Client,
	scheme *runtime.Scheme,
	auditServiceURL string,
) *PodReconciler {
	return &PodReconciler{
		Client:          client,
		Scheme:          scheme,
		AuditServiceURL: auditServiceURL,
		HTTPClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// +kubebuilder:rbac:groups="",resources=pods,verbs=get;list;watch;delete
// +kubebuilder:rbac:groups=shield.kubeshield.io,resources=shieldpolicies,verbs=get;list;watch;update;patch
// +kubebuilder:rbac:groups=shield.kubeshield.io,resources=shieldpolicies/status,verbs=get;update;patch

// Reconcile implements the reconciliation loop for Pods
func (r *PodReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx).WithValues("pod", req.NamespacedName)

	// Skip kube-system namespace
	if req.Namespace == "kube-system" {
		return ctrl.Result{}, nil
	}

	// Fetch the Pod instance
	pod := &corev1.Pod{}
	if err := r.Get(ctx, req.NamespacedName, pod); err != nil {
		if errors.IsNotFound(err) {
			// Pod was deleted, nothing to do
			return ctrl.Result{}, nil
		}
		logger.Error(err, "Failed to fetch Pod")
		return ctrl.Result{}, err
	}

	// Skip pods that are already terminating
	if pod.DeletionTimestamp != nil {
		return ctrl.Result{}, nil
	}

	// Skip pods in terminal phases
	if pod.Status.Phase == corev1.PodSucceeded || pod.Status.Phase == corev1.PodFailed {
		return ctrl.Result{}, nil
	}

	// Fetch all ShieldPolicies
	policies := &shieldv1alpha1.ShieldPolicyList{}
	if err := r.List(ctx, policies); err != nil {
		logger.Error(err, "Failed to list ShieldPolicies")
		return ctrl.Result{}, err
	}

	// Check pod against all applicable policies
	for _, policy := range policies.Items {
		if !policy.ShouldApplyToNamespace(pod.Namespace) {
			continue
		}

		if policy.IsDisabled() {
			continue
		}

		// Check for violations
		violations := r.checkPodViolations(ctx, logger, pod, &policy)

		for _, violation := range violations {
			// Send event to audit service
			r.sendSecurityEvent(ctx, logger, violation)

			// If enforcing, terminate the pod
			if policy.IsEnforcing() {
				logger.Info("Terminating pod due to policy violation",
					"pod", pod.Name,
					"namespace", pod.Namespace,
					"policy", policy.Name,
					"reason", violation.Reason,
				)

				// Delete the pod
				if err := r.Delete(ctx, pod, client.GracePeriodSeconds(0)); err != nil {
					if !errors.IsNotFound(err) {
						logger.Error(err, "Failed to delete violating pod")
						return ctrl.Result{}, err
					}
				}

				// Update policy status
				r.updatePolicyStatus(ctx, logger, &policy, true)

				return ctrl.Result{}, nil
			}

			// If auditing, just log and update status
			r.updatePolicyStatus(ctx, logger, &policy, false)
		}
	}

	return ctrl.Result{}, nil
}

// checkPodViolations checks a pod against a policy and returns any violations
func (r *PodReconciler) checkPodViolations(
	ctx context.Context,
	logger logr.Logger,
	pod *corev1.Pod,
	policy *shieldv1alpha1.ShieldPolicy,
) []SecurityEvent {
	var violations []SecurityEvent
	now := time.Now().UTC().Format(time.RFC3339)

	// Pod-level checks (host network)
	if pod.Spec.HostNetwork {
		violations = append(violations, SecurityEvent{
			Timestamp:   now,
			EventType:   "HOST_NETWORK",
			Severity:    "HIGH",
			PodName:     pod.Name,
			Namespace:   pod.Namespace,
			Reason:      "Pod using host network",
			Action:      "AUDIT",
			PolicyName:  policy.Name,
			NodeName:    pod.Spec.NodeName,
			Description: fmt.Sprintf("Pod '%s' is using host network which can bypass network policies", pod.Name),
		})
	}

	// Check all containers (including init containers)
	allContainers := append(pod.Spec.Containers, pod.Spec.InitContainers...)

	for _, container := range allContainers {
		// Check for privileged containers
		if policy.ShouldBlockPrivileged() {
			if container.SecurityContext != nil &&
				container.SecurityContext.Privileged != nil &&
				*container.SecurityContext.Privileged {

				violations = append(violations, SecurityEvent{
					Timestamp:   now,
					EventType:   "PRIVILEGED_CONTAINER",
					Severity:    "CRITICAL",
					PodName:     pod.Name,
					Namespace:   pod.Namespace,
					Container:   container.Name,
					Image:       container.Image,
					Reason:      "Privileged container detected",
					Action:      r.getActionString(policy),
					PolicyName:  policy.Name,
					NodeName:    pod.Spec.NodeName,
					Description: fmt.Sprintf("Container '%s' is running in privileged mode which violates policy '%s'", container.Name, policy.Name),
				})
			}
		}

		// Check for disallowed registries
		if len(policy.Spec.AllowedRegistries) > 0 {
			registry := extractRegistry(container.Image)
			if !policy.IsRegistryAllowed(registry) {
				violations = append(violations, SecurityEvent{
					Timestamp:   now,
					EventType:   "DISALLOWED_REGISTRY",
					Severity:    "HIGH",
					PodName:     pod.Name,
					Namespace:   pod.Namespace,
					Container:   container.Name,
					Image:       container.Image,
					Reason:      fmt.Sprintf("Image from disallowed registry: %s", registry),
					Action:      r.getActionString(policy),
					PolicyName:  policy.Name,
					NodeName:    pod.Spec.NodeName,
					Description: fmt.Sprintf("Container '%s' uses image from registry '%s' which is not in the allowed list", container.Name, registry),
				})
			}
		}

		// Check for root user
		if container.SecurityContext != nil {
			if container.SecurityContext.RunAsUser != nil && *container.SecurityContext.RunAsUser == 0 {
				violations = append(violations, SecurityEvent{
					Timestamp:   now,
					EventType:   "ROOT_USER",
					Severity:    "HIGH",
					PodName:     pod.Name,
					Namespace:   pod.Namespace,
					Container:   container.Name,
					Image:       container.Image,
					Reason:      "Container running as root user",
					Action:      "AUDIT",
					PolicyName:  policy.Name,
					NodeName:    pod.Spec.NodeName,
					Description: fmt.Sprintf("Container '%s' is configured to run as root (UID 0)", container.Name),
				})
			}
		}
	}

	return violations
}

// getActionString returns the action string based on policy mode
func (r *PodReconciler) getActionString(policy *shieldv1alpha1.ShieldPolicy) string {
	if policy.IsEnforcing() {
		return "TERMINATED"
	}
	return "AUDIT"
}

// sendSecurityEvent sends a security event to the audit service
func (r *PodReconciler) sendSecurityEvent(ctx context.Context, logger logr.Logger, event SecurityEvent) {
	if r.AuditServiceURL == "" {
		logger.V(1).Info("Audit service URL not configured, skipping event notification")
		return
	}

	payload, err := json.Marshal(event)
	if err != nil {
		logger.Error(err, "Failed to marshal security event")
		return
	}

	url := fmt.Sprintf("%s/log", r.AuditServiceURL)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewBuffer(payload))
	if err != nil {
		logger.Error(err, "Failed to create HTTP request")
		return
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := r.HTTPClient.Do(req)
	if err != nil {
		logger.V(1).Info("Failed to send event to audit service", "error", err.Error())
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		logger.Info("Audit service returned error", "status", resp.StatusCode)
	}
}

// updatePolicyStatus updates the status of a ShieldPolicy after an enforcement action
func (r *PodReconciler) updatePolicyStatus(
	ctx context.Context,
	logger logr.Logger,
	policy *shieldv1alpha1.ShieldPolicy,
	wasTerminated bool,
) {
	now := metav1.Now()
	policy.Status.LastEnforcementTime = &now
	policy.Status.ViolationsCount++
	policy.Status.Phase = "Active"

	if wasTerminated {
		policy.Status.TerminationsCount++
		policy.Status.Message = fmt.Sprintf("Last termination at %s", now.Format(time.RFC3339))
	}

	if err := r.Status().Update(ctx, policy); err != nil {
		logger.Error(err, "Failed to update ShieldPolicy status")
	}
}

// extractRegistry extracts the registry from a container image
func extractRegistry(image string) string {
	// Handle images without explicit registry (default to docker.io)
	if !strings.Contains(image, "/") {
		return "docker.io"
	}

	parts := strings.Split(image, "/")
	firstPart := parts[0]

	// Check if first part looks like a registry (contains . or :)
	if strings.Contains(firstPart, ".") || strings.Contains(firstPart, ":") {
		return firstPart
	}

	// Otherwise, it's a docker.io library image
	return "docker.io"
}

// SetupWithManager sets up the controller with the Manager
func (r *PodReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&corev1.Pod{}).
		Complete(r)
}
