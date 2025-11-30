# 🛡️ Kube-Shield

<div align="center">

![Kube-Shield Banner](https://img.shields.io/badge/Kube--Shield-Zero%20Trust%20Security-10b981?style=for-the-badge&logo=kubernetes&logoColor=white)

**Production-Grade Zero-Trust Kubernetes Security Operator**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Go Version](https://img.shields.io/badge/Go-1.21+-00ADD8?logo=go&logoColor=white)](https://golang.org)
[![Python Version](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js&logoColor=white)](https://nextjs.org)

</div>

---

## 📖 Overview

**Kube-Shield** is a comprehensive Kubernetes security solution that implements Zero-Trust principles to protect your cluster from security threats in real-time. It consists of three main components:

| Component | Technology | Description |
|-----------|------------|-------------|
| **Security Operator** | Go + Controller-Runtime | Kubernetes controller that enforces security policies |
| **Audit Service** | Python + FastAPI | Centralized logging and event processing service |
| **Dashboard** | Next.js + Tremor | Real-time visualization and monitoring interface |

---

## ✨ Features

### 🔐 Security Operator
- **Custom Resource Definition (CRD)**: `ShieldPolicy` for declarative security rules
- **Pod Security Enforcement**: Automatically terminates privileged containers
- **Registry Allowlisting**: Blocks images from untrusted registries
- **Real-time Monitoring**: Continuous surveillance of all pods in the cluster
- **Configurable Modes**: Enforce, Audit, or Disabled

### 📊 Audit Service
- **Centralized Logging**: Aggregates security events from the operator
- **In-Memory Storage**: Fast access to recent security events
- **Simulation Mode**: Generates realistic security events for demos
- **RESTful API**: Easy integration with external systems

### 🎛️ Dashboard
- **Cyber-Industrial Design**: Professional "Bloomberg Terminal" aesthetic
- **Real-time Updates**: Live streaming of security events
- **Interactive Charts**: Tremor-powered visualizations
- **Bento Box Layout**: High information density with clean organization

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐     ┌──────────────────┐    ┌──────────────┐   │
│  │                 │     │                  │    │              │   │
│  │  Kube-Shield    │────▶│  Audit Service   │◀───│  Dashboard  │    │
│  │   Operator      │     │   (FastAPI)      │    │  (Next.js)   │   │
│  │                 │     │                  │    │              │   │
│  └────────┬────────┘     └──────────────────┘    └──────────────┘   │
│           │                                                         │
│           │  Watches & Enforces                                     │
│           ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                         Pods                                │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │    │
│  │  │ Pod A   │  │ Pod B   │  │ Pod C   │  │ Pod D   │         │    │
│  │  │ ✓ Safe  │  │ ✗ Priv  │  │ ✓ Safe  │  │ ✗ Bad   │       │     │
│  │  │         │  │ KILLED  │  │         │  │ Registry│         │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** (v20.10+)
- **Kind** (v0.20+) - Kubernetes in Docker
- **kubectl** (v1.28+)

### One-Command Installation

```bash
./kube-shield/setup.sh
```

This script will:
1. ✅ Check prerequisites
2. ✅ Create a Kind cluster
3. ✅ Build all Docker images
4. ✅ Load images into Kind
5. ✅ Deploy all Kubernetes resources
6. ✅ Apply sample security policies

### Access the Dashboard

After installation, open your browser to:

```
http://localhost:30080
```

---

## 📁 Project Structure

```
kube-shield/
├── operator/                    # Go Kubernetes Operator
│   ├── cmd/controller/          # Main entry point
│   ├── pkg/
│   │   ├── apis/shield/v1alpha1/  # CRD types
│   │   ├── controller/          # Reconciliation logic
│   │   └── config/              # Configuration
│   ├── Dockerfile
│   └── go.mod
│
├── audit-service/               # Python FastAPI Service
│   ├── app/
│   │   ├── core/                # Configuration
│   │   ├── models/              # Pydantic models
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   └── main.py              # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
│
├── dashboard/                   # Next.js Dashboard
│   ├── app/                     # Next.js App Router
│   ├── components/              # React components
│   ├── lib/                     # Utilities
│   ├── types/                   # TypeScript types
│   ├── Dockerfile
│   └── package.json
│
├── k8s/                         # Kubernetes Manifests
│   ├── crds/                    # Custom Resource Definitions
│   ├── rbac/                    # RBAC configurations
│   ├── deployments/             # Deployment manifests
│   └── samples/                 # Example resources
│
└── setup.sh                     # Automation script
```

---

## 📋 ShieldPolicy CRD

### Specification

```yaml
apiVersion: shield.kubeshield.io/v1alpha1
kind: ShieldPolicy
metadata:
  name: production-security
spec:
  blockPrivileged: true          # Terminate privileged containers
  enforcementMode: Enforce       # Enforce | Audit | Disabled
  allowedRegistries:             # Trusted registries
    - docker.io
    - gcr.io
    - ghcr.io
  targetNamespaces:              # Empty = all except kube-system
    - production
    - staging
```

### Commands

```bash
# List all policies
kubectl get shieldpolicies

# Describe a policy
kubectl describe shieldpolicy default-security-policy

# Watch policy status
kubectl get shieldpolicies -w
```

---

## 🧪 Testing

### Create a Privileged Pod (Will Be Terminated)

```bash
kubectl apply -f k8s/samples/test-pods.yaml
```

### Watch the Operator Logs

```bash
kubectl logs -f -l app.kubernetes.io/component=operator -n kube-shield
```

### Check the Dashboard

The dashboard will show real-time events as pods are being evaluated and terminated.

---

## 🔧 Configuration

### Operator Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AUDIT_SERVICE_URL` | URL of the audit service | `http://audit-service:8000` |
| `METRICS_ADDR` | Metrics endpoint address | `:8080` |
| `PROBE_ADDR` | Health probe address | `:8081` |
| `ENABLE_LEADER_ELECTION` | Enable leader election | `false` |

### Audit Service Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Bind host | `0.0.0.0` |
| `PORT` | Bind port | `8000` |
| `MAX_LOGS` | Maximum logs to store | `100` |
| `SIMULATION_ENABLED` | Enable simulation mode | `true` |
| `SIMULATION_INTERVAL` | Simulation interval (seconds) | `5` |

### Dashboard Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_AUDIT_SERVICE_URL` | Audit service URL | `http://localhost:8000` |

---

## 🎨 Design Philosophy

### Cyber-Industrial Aesthetic

The dashboard follows a **"Bloomberg Terminal meets Vercel Dark Mode"** design philosophy:

- **Deep Slate Backgrounds**: `bg-slate-950`, `bg-slate-900`
- **Functional Accent Colors**:
  - 🟢 Emerald (`text-emerald-500`) - Secure, Healthy
  - 🔴 Rose (`text-rose-500`) - Critical, Threats
  - 🟡 Amber (`text-amber-500`) - Warnings, Drift
- **Typography**:
  - Sans-serif (Inter) for UI elements
  - Monospace (JetBrains Mono) for logs and data
- **Layout**: Bento box grid with high information density

---

## 🛠️ Development

### Local Development

```bash
# Start the audit service locally
cd audit-service
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Start the dashboard locally
cd dashboard
npm install
npm run dev

# Build the operator
cd operator
go build -o bin/operator ./cmd/controller
```

### Running Tests

```bash
# Go tests
cd operator && go test ./...

# Python tests
cd audit-service && pytest

# Dashboard linting
cd dashboard && npm run lint
```

---

## 📊 API Endpoints

### Audit Service

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ready` | GET | Readiness check |
| `/status` | GET | Service status |
| `/api/v1/logs` | GET | List security events |
| `/api/v1/logs` | POST | Create security event |
| `/api/v1/metrics` | GET | Aggregated metrics |
| `/api/v1/attack-volume` | GET | Attack volume time series |

---

## 🔒 Security Considerations

- **Non-root containers**: All components run as non-root users
- **Read-only filesystems**: Where possible
- **Network policies**: Recommended for production
- **RBAC**: Minimal permissions following least-privilege principle
- **Security contexts**: Proper seccomp profiles and capability dropping

---

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<div align="center">

**Built with ❤️ for Kubernetes Security**

[Report Bug](https://github.com/Anamitra-Sarkar/Kubeshield_CyberSecurity/issues) · [Request Feature](https://github.com/Anamitra-Sarkar/Kubeshield_CyberSecurity/issues)

</div>
