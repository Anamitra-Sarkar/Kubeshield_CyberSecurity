# Kubeshield_CyberSecurity

## 🛡️ Kube-Shield: Zero-Trust Kubernetes Security Operator

A production-grade Zero-Trust Kubernetes security solution with real-time threat detection and visualization.

For full documentation, see [kube-shield/README.md](./kube-shield/README.md).

### Quick Start

```bash
cd kube-shield
./setup.sh
```

Dashboard will be available at: http://localhost:30080

### Components

| Component | Description |
|-----------|-------------|
| **Operator** | Go-based Kubernetes controller for security policy enforcement |
| **Audit Service** | Python FastAPI backend for event logging |
| **Dashboard** | Next.js visualization interface |

### License

Apache License 2.0