// Package v1alpha1 contains API Schema definitions for the shield v1alpha1 API group
// +kubebuilder:object:generate=true
// +groupName=shield.kubeshield.io
package v1alpha1

import (
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

// ShieldPolicySpec defines the desired state of ShieldPolicy
type ShieldPolicySpec struct {
	// BlockPrivileged indicates whether privileged containers should be blocked and terminated
	// +kubebuilder:validation:Required
	BlockPrivileged bool `json:"blockPrivileged"`

	// AllowedRegistries is a list of container registries that are allowed
	// +kubebuilder:validation:Optional
	AllowedRegistries []string `json:"allowedRegistries,omitempty"`

	// EnforcementMode specifies how the policy should be enforced
	// +kubebuilder:validation:Enum=Enforce;Audit;Disabled
	// +kubebuilder:default=Enforce
	EnforcementMode string `json:"enforcementMode,omitempty"`

	// TargetNamespaces limits policy enforcement to specific namespaces
	// If empty, applies to all namespaces except kube-system
	// +kubebuilder:validation:Optional
	TargetNamespaces []string `json:"targetNamespaces,omitempty"`
}

// ShieldPolicyStatus defines the observed state of ShieldPolicy
type ShieldPolicyStatus struct {
	// Phase represents the current phase of the ShieldPolicy
	// +kubebuilder:validation:Enum=Active;Inactive;Error
	Phase string `json:"phase,omitempty"`

	// LastEnforcementTime is the last time the policy was enforced
	LastEnforcementTime *metav1.Time `json:"lastEnforcementTime,omitempty"`

	// ViolationsCount is the total number of violations detected
	ViolationsCount int64 `json:"violationsCount,omitempty"`

	// TerminationsCount is the total number of pods terminated due to violations
	TerminationsCount int64 `json:"terminationsCount,omitempty"`

	// Conditions represent the latest available observations of the policy's current state
	Conditions []metav1.Condition `json:"conditions,omitempty"`

	// ObservedGeneration is the most recent generation observed for this ShieldPolicy
	ObservedGeneration int64 `json:"observedGeneration,omitempty"`

	// Message provides additional information about the current state
	Message string `json:"message,omitempty"`
}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:resource:shortName=sp;shieldpolicy
// +kubebuilder:printcolumn:name="Mode",type="string",JSONPath=".spec.enforcementMode"
// +kubebuilder:printcolumn:name="Block Privileged",type="boolean",JSONPath=".spec.blockPrivileged"
// +kubebuilder:printcolumn:name="Violations",type="integer",JSONPath=".status.violationsCount"
// +kubebuilder:printcolumn:name="Terminations",type="integer",JSONPath=".status.terminationsCount"
// +kubebuilder:printcolumn:name="Phase",type="string",JSONPath=".status.phase"
// +kubebuilder:printcolumn:name="Age",type="date",JSONPath=".metadata.creationTimestamp"

// ShieldPolicy is the Schema for the shieldpolicies API
type ShieldPolicy struct {
	metav1.TypeMeta   `json:",inline"`
	metav1.ObjectMeta `json:"metadata,omitempty"`

	Spec   ShieldPolicySpec   `json:"spec,omitempty"`
	Status ShieldPolicyStatus `json:"status,omitempty"`
}

// +kubebuilder:object:root=true

// ShieldPolicyList contains a list of ShieldPolicy
type ShieldPolicyList struct {
	metav1.TypeMeta `json:",inline"`
	metav1.ListMeta `json:"metadata,omitempty"`
	Items           []ShieldPolicy `json:"items"`
}

// IsEnforcing returns true if the policy is in enforcement mode
func (s *ShieldPolicy) IsEnforcing() bool {
	return s.Spec.EnforcementMode == "" || s.Spec.EnforcementMode == "Enforce"
}

// IsAuditing returns true if the policy is in audit mode
func (s *ShieldPolicy) IsAuditing() bool {
	return s.Spec.EnforcementMode == "Audit"
}

// IsDisabled returns true if the policy is disabled
func (s *ShieldPolicy) IsDisabled() bool {
	return s.Spec.EnforcementMode == "Disabled"
}

// ShouldBlockPrivileged returns true if privileged containers should be blocked
func (s *ShieldPolicy) ShouldBlockPrivileged() bool {
	return s.Spec.BlockPrivileged && !s.IsDisabled()
}

// IsRegistryAllowed checks if a registry is in the allowed list
func (s *ShieldPolicy) IsRegistryAllowed(registry string) bool {
	if len(s.Spec.AllowedRegistries) == 0 {
		return true // No restriction if list is empty
	}
	for _, allowed := range s.Spec.AllowedRegistries {
		if allowed == registry || allowed == "*" {
			return true
		}
	}
	return false
}

// ShouldApplyToNamespace checks if the policy should apply to a given namespace
func (s *ShieldPolicy) ShouldApplyToNamespace(namespace string) bool {
	// Never apply to kube-system
	if namespace == "kube-system" {
		return false
	}
	// If no target namespaces specified, apply to all (except kube-system)
	if len(s.Spec.TargetNamespaces) == 0 {
		return true
	}
	for _, ns := range s.Spec.TargetNamespaces {
		if ns == namespace {
			return true
		}
	}
	return false
}
