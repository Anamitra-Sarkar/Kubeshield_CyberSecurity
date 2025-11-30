#!/bin/bash

#===============================================================================
# Kube-Shield Setup Script
# Production-grade Zero-Trust Kubernetes Operator
#
# This script:
#   1. Checks prerequisites (kind, docker)
#   2. Creates a local Kind cluster
#   3. Builds Docker images for all components
#   4. Loads images into Kind
#   5. Deploys all Kubernetes resources
#===============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="${CLUSTER_NAME:-kube-shield}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

#-------------------------------------------------------------------------------
# Logging Functions
#-------------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

log_step() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

#-------------------------------------------------------------------------------
# Prerequisite Checks
#-------------------------------------------------------------------------------

check_prerequisites() {
    log_step "Step 1: Checking Prerequisites"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker."
    fi
    log_success "Docker is installed and running"

    # Check Kind
    if ! command -v kind &> /dev/null; then
        log_warning "Kind is not installed. Installing..."
        install_kind
    fi
    log_success "Kind is installed"

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_warning "kubectl is not installed. Installing..."
        install_kubectl
    fi
    log_success "kubectl is installed"

    log_success "All prerequisites satisfied"
}

install_kind() {
    local ARCH
    ARCH=$(uname -m)
    case $ARCH in
        x86_64) ARCH="amd64" ;;
        aarch64) ARCH="arm64" ;;
        *) log_error "Unsupported architecture: $ARCH" ;;
    esac

    curl -Lo ./kind "https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-${ARCH}"
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
    log_success "Kind installed successfully"
}

install_kubectl() {
    local ARCH
    ARCH=$(uname -m)
    case $ARCH in
        x86_64) ARCH="amd64" ;;
        aarch64) ARCH="arm64" ;;
        *) log_error "Unsupported architecture: $ARCH" ;;
    esac

    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/${ARCH}/kubectl"
    chmod +x kubectl
    sudo mv kubectl /usr/local/bin/kubectl
    log_success "kubectl installed successfully"
}

#-------------------------------------------------------------------------------
# Cluster Management
#-------------------------------------------------------------------------------

create_cluster() {
    log_step "Step 2: Creating Kind Cluster"

    # Check if cluster already exists
    if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
        log_warning "Cluster '${CLUSTER_NAME}' already exists"
        read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deleting existing cluster..."
            kind delete cluster --name "${CLUSTER_NAME}"
        else
            log_info "Using existing cluster"
            kubectl cluster-info --context "kind-${CLUSTER_NAME}"
            return
        fi
    fi

    # Create kind config with exposed ports
    cat > /tmp/kind-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${CLUSTER_NAME}
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: InitConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "ingress-ready=true"
    extraPortMappings:
      - containerPort: 30080
        hostPort: 30080
        protocol: TCP
      - containerPort: 30000
        hostPort: 30000
        protocol: TCP
  - role: worker
  - role: worker
EOF

    log_info "Creating Kind cluster '${CLUSTER_NAME}'..."
    kind create cluster --config /tmp/kind-config.yaml
    rm /tmp/kind-config.yaml

    log_success "Kind cluster created successfully"
    kubectl cluster-info --context "kind-${CLUSTER_NAME}"
}

#-------------------------------------------------------------------------------
# Docker Image Building
#-------------------------------------------------------------------------------

build_images() {
    log_step "Step 3: Building Docker Images"

    # Build Operator
    log_info "Building Go Operator image..."
    cd "${SCRIPT_DIR}/operator"
    docker build -t kubeshield-operator:latest .
    log_success "Operator image built"

    # Build Audit Service
    log_info "Building Python Audit Service image..."
    cd "${SCRIPT_DIR}/audit-service"
    docker build -t kubeshield-audit-service:latest .
    log_success "Audit Service image built"

    # Build Dashboard
    log_info "Building Next.js Dashboard image..."
    cd "${SCRIPT_DIR}/dashboard"
    docker build \
        --build-arg NEXT_PUBLIC_AUDIT_SERVICE_URL=http://audit-service.kube-shield.svc.cluster.local:8000 \
        -t kubeshield-dashboard:latest .
    log_success "Dashboard image built"

    cd "${SCRIPT_DIR}"
    log_success "All images built successfully"
}

#-------------------------------------------------------------------------------
# Load Images into Kind
#-------------------------------------------------------------------------------

load_images() {
    log_step "Step 4: Loading Images into Kind Cluster"

    log_info "Loading Operator image..."
    kind load docker-image kubeshield-operator:latest --name "${CLUSTER_NAME}"

    log_info "Loading Audit Service image..."
    kind load docker-image kubeshield-audit-service:latest --name "${CLUSTER_NAME}"

    log_info "Loading Dashboard image..."
    kind load docker-image kubeshield-dashboard:latest --name "${CLUSTER_NAME}"

    log_success "All images loaded into Kind cluster"
}

#-------------------------------------------------------------------------------
# Deploy Kubernetes Resources
#-------------------------------------------------------------------------------

deploy_resources() {
    log_step "Step 5: Deploying Kubernetes Resources"

    cd "${SCRIPT_DIR}/k8s"

    # Apply CRDs
    log_info "Applying Custom Resource Definitions..."
    kubectl apply -f crds/

    # Apply RBAC
    log_info "Applying RBAC configurations..."
    kubectl apply -f rbac/

    # Apply Deployments
    log_info "Applying Deployments..."
    kubectl apply -f deployments/

    # Wait for pods to be ready
    log_info "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kube-shield -n kube-shield --timeout=120s || true

    # Apply sample ShieldPolicy
    log_info "Applying sample ShieldPolicy..."
    kubectl apply -f samples/shieldpolicy-sample.yaml

    cd "${SCRIPT_DIR}"
    log_success "All resources deployed successfully"
}

#-------------------------------------------------------------------------------
# Status Check
#-------------------------------------------------------------------------------

show_status() {
    log_step "Step 6: Deployment Status"

    echo ""
    log_info "Pods in kube-shield namespace:"
    kubectl get pods -n kube-shield -o wide

    echo ""
    log_info "Services in kube-shield namespace:"
    kubectl get svc -n kube-shield

    echo ""
    log_info "ShieldPolicies:"
    kubectl get shieldpolicies

    echo ""
    log_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_success "Kube-Shield Deployment Complete!"
    log_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${GREEN}Dashboard URL:${NC} http://localhost:30080"
    echo -e "${GREEN}Audit Service:${NC} http://localhost:30000 (if exposed)"
    echo ""
    echo -e "${YELLOW}To test the operator, create a privileged pod:${NC}"
    echo "  kubectl apply -f k8s/samples/test-pods.yaml"
    echo ""
    echo -e "${YELLOW}To view operator logs:${NC}"
    echo "  kubectl logs -f -l app.kubernetes.io/component=operator -n kube-shield"
    echo ""
    echo -e "${YELLOW}To delete the cluster:${NC}"
    echo "  kind delete cluster --name ${CLUSTER_NAME}"
    echo ""
}

#-------------------------------------------------------------------------------
# Cleanup Function
#-------------------------------------------------------------------------------

cleanup() {
    log_step "Cleaning Up"
    
    log_info "Deleting Kind cluster..."
    kind delete cluster --name "${CLUSTER_NAME}" || true

    log_success "Cleanup complete"
}

#-------------------------------------------------------------------------------
# Help
#-------------------------------------------------------------------------------

show_help() {
    echo "Kube-Shield Setup Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install     Full installation (default)"
    echo "  build       Build Docker images only"
    echo "  deploy      Deploy to existing cluster"
    echo "  status      Show deployment status"
    echo "  cleanup     Delete the Kind cluster"
    echo "  help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  CLUSTER_NAME    Name of the Kind cluster (default: kube-shield)"
    echo ""
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

main() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                                                                       ║${NC}"
    echo -e "${CYAN}║   ${GREEN}██╗  ██╗██╗   ██╗██████╗ ███████╗    ███████╗██╗  ██╗██╗███████╗██╗     ██████╗${NC}  ${CYAN}║${NC}"
    echo -e "${CYAN}║   ${GREEN}██║ ██╔╝██║   ██║██╔══██╗██╔════╝    ██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗${NC} ${CYAN}║${NC}"
    echo -e "${CYAN}║   ${GREEN}█████╔╝ ██║   ██║██████╔╝█████╗█████╗███████╗███████║██║█████╗  ██║     ██║  ██║${NC} ${CYAN}║${NC}"
    echo -e "${CYAN}║   ${GREEN}██╔═██╗ ██║   ██║██╔══██╗██╔══╝╚════╝╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║${NC} ${CYAN}║${NC}"
    echo -e "${CYAN}║   ${GREEN}██║  ██╗╚██████╔╝██████╔╝███████╗    ███████║██║  ██║██║███████╗███████╗██████╔╝${NC} ${CYAN}║${NC}"
    echo -e "${CYAN}║   ${GREEN}╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝${NC}  ${CYAN}║${NC}"
    echo -e "${CYAN}║                                                                       ║${NC}"
    echo -e "${CYAN}║                    Zero-Trust Kubernetes Security                     ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    local command="${1:-install}"

    case "$command" in
        install)
            check_prerequisites
            create_cluster
            build_images
            load_images
            deploy_resources
            show_status
            ;;
        build)
            build_images
            ;;
        deploy)
            deploy_resources
            show_status
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command. Use '$0 help' for usage."
            ;;
    esac
}

# Run main
main "$@"
