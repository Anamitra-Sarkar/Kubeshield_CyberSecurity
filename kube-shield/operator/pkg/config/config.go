package config

import (
	"os"
	"strconv"
	"time"
)

// Config holds all configuration for the operator
type Config struct {
	// MetricsAddr is the address the metric endpoint binds to
	MetricsAddr string

	// ProbeAddr is the address the probe endpoint binds to
	ProbeAddr string

	// EnableLeaderElection enables leader election for controller manager
	EnableLeaderElection bool

	// LeaderElectionID is the name of the resource that leader election will use
	LeaderElectionID string

	// AuditServiceURL is the URL of the audit service to send events to
	AuditServiceURL string

	// SyncPeriod is how often the controller re-syncs all resources
	SyncPeriod time.Duration

	// Namespace limits the controller to a specific namespace (empty = all namespaces)
	Namespace string

	// LogLevel sets the log verbosity
	LogLevel int
}

// NewConfig creates a new Config with default values
func NewConfig() *Config {
	return &Config{
		MetricsAddr:          getEnvOrDefault("METRICS_ADDR", ":8080"),
		ProbeAddr:            getEnvOrDefault("PROBE_ADDR", ":8081"),
		EnableLeaderElection: getEnvBoolOrDefault("ENABLE_LEADER_ELECTION", false),
		LeaderElectionID:     getEnvOrDefault("LEADER_ELECTION_ID", "kubeshield-operator-lock"),
		AuditServiceURL:      getEnvOrDefault("AUDIT_SERVICE_URL", "http://audit-service:8000"),
		SyncPeriod:           getEnvDurationOrDefault("SYNC_PERIOD", 10*time.Minute),
		Namespace:            os.Getenv("WATCH_NAMESPACE"),
		LogLevel:             getEnvIntOrDefault("LOG_LEVEL", 0),
	}
}

// getEnvOrDefault returns the value of an environment variable or a default value
func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// getEnvBoolOrDefault returns the boolean value of an environment variable or a default
func getEnvBoolOrDefault(key string, defaultValue bool) bool {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	b, err := strconv.ParseBool(value)
	if err != nil {
		return defaultValue
	}
	return b
}

// getEnvIntOrDefault returns the integer value of an environment variable or a default
func getEnvIntOrDefault(key string, defaultValue int) int {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	i, err := strconv.Atoi(value)
	if err != nil {
		return defaultValue
	}
	return i
}

// getEnvDurationOrDefault returns the duration value of an environment variable or a default
func getEnvDurationOrDefault(key string, defaultValue time.Duration) time.Duration {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	d, err := time.ParseDuration(value)
	if err != nil {
		return defaultValue
	}
	return d
}
