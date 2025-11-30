package controller

import (
	"context"
	"time"

	"k8s.io/apimachinery/pkg/api/errors"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
	"sigs.k8s.io/controller-runtime/pkg/log"

	shieldv1alpha1 "github.com/kubeshield/operator/pkg/apis/shield/v1alpha1"
)

// ShieldPolicyReconciler reconciles ShieldPolicy objects
type ShieldPolicyReconciler struct {
	client.Client
	Scheme *runtime.Scheme
}

// NewShieldPolicyReconciler creates a new ShieldPolicyReconciler
func NewShieldPolicyReconciler(
	client client.Client,
	scheme *runtime.Scheme,
) *ShieldPolicyReconciler {
	return &ShieldPolicyReconciler{
		Client: client,
		Scheme: scheme,
	}
}

// +kubebuilder:rbac:groups=shield.kubeshield.io,resources=shieldpolicies,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=shield.kubeshield.io,resources=shieldpolicies/status,verbs=get;update;patch
// +kubebuilder:rbac:groups=shield.kubeshield.io,resources=shieldpolicies/finalizers,verbs=update

// Reconcile handles the reconciliation loop for ShieldPolicy
func (r *ShieldPolicyReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	logger := log.FromContext(ctx).WithValues("shieldpolicy", req.NamespacedName)

	// Fetch the ShieldPolicy instance
	policy := &shieldv1alpha1.ShieldPolicy{}
	if err := r.Get(ctx, req.NamespacedName, policy); err != nil {
		if errors.IsNotFound(err) {
			// Policy was deleted
			logger.Info("ShieldPolicy resource not found, ignoring since object must be deleted")
			return ctrl.Result{}, nil
		}
		logger.Error(err, "Failed to fetch ShieldPolicy")
		return ctrl.Result{}, err
	}

	// Initialize status if not set
	if policy.Status.Phase == "" {
		policy.Status.Phase = "Active"
		policy.Status.ObservedGeneration = policy.Generation
		policy.Status.Message = "Policy is active and enforcing"

		// Set initial condition
		condition := metav1.Condition{
			Type:               "Ready",
			Status:             metav1.ConditionTrue,
			Reason:             "PolicyActive",
			Message:            "ShieldPolicy is active and monitoring pods",
			LastTransitionTime: metav1.Now(),
		}
		policy.Status.Conditions = []metav1.Condition{condition}

		if err := r.Status().Update(ctx, policy); err != nil {
			logger.Error(err, "Failed to update ShieldPolicy status")
			return ctrl.Result{}, err
		}

		logger.Info("Initialized ShieldPolicy status",
			"phase", policy.Status.Phase,
			"blockPrivileged", policy.Spec.BlockPrivileged,
			"enforcementMode", policy.Spec.EnforcementMode,
		)
	}

	// Check if generation changed
	if policy.Generation != policy.Status.ObservedGeneration {
		policy.Status.ObservedGeneration = policy.Generation
		policy.Status.Message = "Policy configuration updated"

		// Update condition
		condition := metav1.Condition{
			Type:               "Ready",
			Status:             metav1.ConditionTrue,
			Reason:             "PolicyUpdated",
			Message:            "ShieldPolicy configuration was updated",
			LastTransitionTime: metav1.Now(),
		}
		policy.Status.Conditions = []metav1.Condition{condition}

		if err := r.Status().Update(ctx, policy); err != nil {
			logger.Error(err, "Failed to update ShieldPolicy status after config change")
			return ctrl.Result{}, err
		}

		logger.Info("Updated ShieldPolicy status after configuration change")
	}

	// Requeue periodically to update status
	return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
}

// SetupWithManager sets up the controller with the Manager
func (r *ShieldPolicyReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&shieldv1alpha1.ShieldPolicy{}).
		Complete(r)
}
