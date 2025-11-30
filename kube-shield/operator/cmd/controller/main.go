package main

import (
	"flag"
	"os"

	"k8s.io/apimachinery/pkg/runtime"
	utilruntime "k8s.io/apimachinery/pkg/util/runtime"
	clientgoscheme "k8s.io/client-go/kubernetes/scheme"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/healthz"
	"sigs.k8s.io/controller-runtime/pkg/log/zap"
	metricsserver "sigs.k8s.io/controller-runtime/pkg/metrics/server"

	shieldv1alpha1 "github.com/kubeshield/operator/pkg/apis/shield/v1alpha1"
	"github.com/kubeshield/operator/pkg/config"
	"github.com/kubeshield/operator/pkg/controller"
)

var (
	scheme   = runtime.NewScheme()
	setupLog = ctrl.Log.WithName("setup")
)

func init() {
	utilruntime.Must(clientgoscheme.AddToScheme(scheme))
	utilruntime.Must(shieldv1alpha1.AddToScheme(scheme))
}

func main() {
	cfg := config.NewConfig()

	// Parse flags for override
	var metricsAddr string
	var probeAddr string
	var enableLeaderElection bool
	var auditServiceURL string

	flag.StringVar(&metricsAddr, "metrics-bind-address", cfg.MetricsAddr, "The address the metric endpoint binds to.")
	flag.StringVar(&probeAddr, "health-probe-bind-address", cfg.ProbeAddr, "The address the probe endpoint binds to.")
	flag.BoolVar(&enableLeaderElection, "leader-elect", cfg.EnableLeaderElection, "Enable leader election for controller manager.")
	flag.StringVar(&auditServiceURL, "audit-service-url", cfg.AuditServiceURL, "The URL of the audit service to send events to.")

	opts := zap.Options{
		Development: true,
	}
	opts.BindFlags(flag.CommandLine)
	flag.Parse()

	ctrl.SetLogger(zap.New(zap.UseFlagOptions(&opts)))

	setupLog.Info("Starting Kube-Shield Operator",
		"metricsAddr", metricsAddr,
		"probeAddr", probeAddr,
		"enableLeaderElection", enableLeaderElection,
		"auditServiceURL", auditServiceURL,
	)

	mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
		Scheme: scheme,
		Metrics: metricsserver.Options{
			BindAddress: metricsAddr,
		},
		HealthProbeBindAddress: probeAddr,
		LeaderElection:         enableLeaderElection,
		LeaderElectionID:       cfg.LeaderElectionID,
	})
	if err != nil {
		setupLog.Error(err, "unable to create manager")
		os.Exit(1)
	}

	// Create and register the Pod controller
	podReconciler := controller.NewPodReconciler(
		mgr.GetClient(),
		mgr.GetScheme(),
		auditServiceURL,
	)
	if err := podReconciler.SetupWithManager(mgr); err != nil {
		setupLog.Error(err, "unable to create Pod controller")
		os.Exit(1)
	}

	// Create and register the ShieldPolicy controller
	policyReconciler := controller.NewShieldPolicyReconciler(
		mgr.GetClient(),
		mgr.GetScheme(),
	)
	if err := policyReconciler.SetupWithManager(mgr); err != nil {
		setupLog.Error(err, "unable to create ShieldPolicy controller")
		os.Exit(1)
	}

	// Add health checks
	if err := mgr.AddHealthzCheck("healthz", healthz.Ping); err != nil {
		setupLog.Error(err, "unable to set up health check")
		os.Exit(1)
	}
	if err := mgr.AddReadyzCheck("readyz", healthz.Ping); err != nil {
		setupLog.Error(err, "unable to set up ready check")
		os.Exit(1)
	}

	setupLog.Info("Starting manager")
	if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {
		setupLog.Error(err, "problem running manager")
		os.Exit(1)
	}
}
