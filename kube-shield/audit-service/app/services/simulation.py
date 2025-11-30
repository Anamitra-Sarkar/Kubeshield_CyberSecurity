"""
Security event simulation service for demo purposes.
Generates realistic fake security logs at regular intervals.
"""
import random
import threading
import time
from datetime import datetime
from typing import Callable, Optional

from ..models import SecurityEvent


class SimulationService:
    """Background service that generates realistic security events."""
    
    # Realistic CVEs and security threats
    CVES = [
        "CVE-2024-3847",
        "CVE-2024-21626",
        "CVE-2024-0193",
        "CVE-2023-44487",
        "CVE-2023-42793",
        "CVE-2023-38545",
        "CVE-2023-32233",
        "CVE-2023-29491",
        "CVE-2023-20198",
        "CVE-2023-4911",
    ]
    
    # Suspicious IP ranges for egress attempts
    SUSPICIOUS_IPS = [
        "192.168.100.",
        "10.255.0.",
        "172.16.99.",
        "203.0.113.",
        "198.51.100.",
    ]
    
    # Realistic namespace names
    NAMESPACES = [
        "production",
        "staging",
        "development",
        "monitoring",
        "payments",
        "auth-service",
        "data-pipeline",
        "frontend",
        "backend-api",
        "ml-workloads",
    ]
    
    # Realistic pod name prefixes
    POD_PREFIXES = [
        "api-gateway",
        "user-service",
        "payment-processor",
        "data-worker",
        "auth-handler",
        "cache-manager",
        "queue-consumer",
        "web-frontend",
        "analytics-engine",
        "ml-inference",
    ]
    
    # Realistic container images
    IMAGES = [
        "gcr.io/production/api:v2.3.1",
        "docker.io/library/nginx:latest",
        "quay.io/prometheus/prometheus:v2.48.0",
        "registry.k8s.io/coredns:v1.11.1",
        "ghcr.io/internal/payment-service:1.4.2",
        "public.ecr.aws/bitnami/redis:7.2",
        "untrusted-registry.io/malicious:latest",
        "docker.io/library/alpine:3.19",
    ]
    
    # Node names
    NODES = [
        "worker-node-01",
        "worker-node-02", 
        "worker-node-03",
        "compute-large-01",
        "compute-large-02",
    ]
    
    # Policy names
    POLICIES = [
        "default-security-policy",
        "production-strict",
        "payment-pci-policy",
        "network-egress-policy",
        "registry-allowlist",
    ]
    
    def __init__(
        self,
        callback: Callable[[SecurityEvent], None],
        interval: int = 5,
        enabled: bool = True,
    ):
        self._callback = callback
        self._interval = interval
        self._enabled = enabled
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def _generate_random_event(self) -> SecurityEvent:
        """Generate a realistic random security event."""
        event_generators = [
            self._generate_cve_event,
            self._generate_egress_event,
            self._generate_privileged_event,
            self._generate_crypto_mining_event,
            self._generate_lateral_movement_event,
            self._generate_config_drift_event,
            self._generate_registry_violation_event,
            self._generate_privilege_escalation_event,
        ]
        
        # Weight towards more common events
        weights = [25, 20, 15, 10, 10, 10, 5, 5]
        generator = random.choices(event_generators, weights=weights)[0]
        
        return generator()
    
    def _random_pod_name(self) -> str:
        """Generate a realistic pod name."""
        prefix = random.choice(self.POD_PREFIXES)
        suffix = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=5))
        return f"{prefix}-{suffix}"
    
    def _generate_cve_event(self) -> SecurityEvent:
        """Generate a CVE detection event."""
        cve = random.choice(self.CVES)
        pod = self._random_pod_name()
        namespace = random.choice(self.NAMESPACES)
        image = random.choice(self.IMAGES)
        
        return SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            eventType="CVE_DETECTED",
            severity=random.choice(["CRITICAL", "HIGH", "MEDIUM"]),
            podName=pod,
            namespace=namespace,
            container="main",
            image=image,
            reason=f"{cve} detected in container image",
            action="AUDIT",
            policyName=random.choice(self.POLICIES),
            nodeName=random.choice(self.NODES),
            description=f"Container vulnerability scan detected {cve} in image {image}. CVSS score indicates potential remote code execution.",
        )
    
    def _generate_egress_event(self) -> SecurityEvent:
        """Generate an unauthorized egress event."""
        ip = random.choice(self.SUSPICIOUS_IPS) + str(random.randint(1, 254))
        port = random.choice([22, 23, 3389, 4444, 6666, 8080, 9001])
        pod = self._random_pod_name()
        
        return SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            eventType="UNAUTHORIZED_EGRESS",
            severity="HIGH",
            podName=pod,
            namespace=random.choice(self.NAMESPACES),
            container="main",
            image=random.choice(self.IMAGES),
            reason=f"Unauthorized egress to {ip}:{port}",
            action="AUDIT",
            policyName="network-egress-policy",
            nodeName=random.choice(self.NODES),
            description=f"Pod attempted outbound connection to {ip}:{port} which is not in the allowed egress list. This may indicate data exfiltration or C2 communication.",
        )
    
    def _generate_privileged_event(self) -> SecurityEvent:
        """Generate a privileged container detection event."""
        pod = self._random_pod_name()
        
        return SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            eventType="PRIVILEGED_CONTAINER",
            severity="CRITICAL",
            podName=pod,
            namespace=random.choice(self.NAMESPACES),
            container="privileged-worker",
            image=random.choice(self.IMAGES),
            reason="Privileged container detected",
            action=random.choice(["TERMINATED", "AUDIT"]),
            policyName="default-security-policy",
            nodeName=random.choice(self.NODES),
            description=f"Container is running in privileged mode with access to host kernel capabilities. Pod terminated to prevent potential container escape.",
        )
    
    def _generate_crypto_mining_event(self) -> SecurityEvent:
        """Generate a crypto mining detection event."""
        pod = self._random_pod_name()
        pool = random.choice([
            "stratum+tcp://xmr.pool.minergate.com:45700",
            "stratum+tcp://pool.supportxmr.com:3333",
            "stratum+tcp://xmrpool.eu:5555",
        ])
        
        return SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            eventType="CRYPTO_MINING",
            severity="CRITICAL",
            podName=pod,
            namespace=random.choice(self.NAMESPACES),
            container="main",
            image="alpine:latest",
            reason="Crypto mining activity detected",
            action="TERMINATED",
            policyName="default-security-policy",
            nodeName=random.choice(self.NODES),
            description=f"Process attempted to connect to mining pool at {pool}. Container terminated immediately.",
        )
    
    def _generate_lateral_movement_event(self) -> SecurityEvent:
        """Generate a lateral movement detection event."""
        pod = self._random_pod_name()
        target_service = random.choice([
            "kubernetes.default.svc",
            "kube-apiserver:6443",
            "etcd:2379",
            "metadata.google.internal",
        ])
        
        return SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            eventType="LATERAL_MOVEMENT",
            severity="CRITICAL",
            podName=pod,
            namespace=random.choice(self.NAMESPACES),
            container="main",
            image=random.choice(self.IMAGES),
            reason=f"Suspicious access attempt to {target_service}",
            action="AUDIT",
            policyName="default-security-policy",
            nodeName=random.choice(self.NODES),
            description=f"Container made unexpected connection attempt to internal service {target_service}. This may indicate lateral movement or service account token abuse.",
        )
    
    def _generate_config_drift_event(self) -> SecurityEvent:
        """Generate a configuration drift event."""
        pod = self._random_pod_name()
        drift_type = random.choice([
            "SecurityContext modified",
            "Environment variables changed",
            "Resource limits removed",
            "Network policy bypassed",
        ])
        
        return SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            eventType="CONFIG_DRIFT",
            severity="MEDIUM",
            podName=pod,
            namespace=random.choice(self.NAMESPACES),
            container="main",
            image=random.choice(self.IMAGES),
            reason=drift_type,
            action="AUDIT",
            policyName=random.choice(self.POLICIES),
            nodeName=random.choice(self.NODES),
            description=f"Configuration drift detected: {drift_type}. Pod configuration does not match declared GitOps state.",
        )
    
    def _generate_registry_violation_event(self) -> SecurityEvent:
        """Generate a disallowed registry event."""
        pod = self._random_pod_name()
        bad_registry = random.choice([
            "untrusted-registry.io",
            "public.ecr.aws/unknown",
            "docker.io/malicious-user",
        ])
        
        return SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            eventType="DISALLOWED_REGISTRY",
            severity="HIGH",
            podName=pod,
            namespace=random.choice(self.NAMESPACES),
            container="main",
            image=f"{bad_registry}/suspicious-image:latest",
            reason=f"Image from disallowed registry: {bad_registry}",
            action="TERMINATED",
            policyName="registry-allowlist",
            nodeName=random.choice(self.NODES),
            description=f"Pod attempted to use image from {bad_registry} which is not in the approved registry list. Pod terminated.",
        )
    
    def _generate_privilege_escalation_event(self) -> SecurityEvent:
        """Generate a privilege escalation event."""
        pod = self._random_pod_name()
        escalation = random.choice([
            "setuid binary execution",
            "CAP_SYS_ADMIN capability usage",
            "ptrace syscall detected",
            "Namespace manipulation attempt",
        ])
        
        return SecurityEvent(
            timestamp=datetime.utcnow().isoformat() + "Z",
            eventType="PRIVILEGE_ESCALATION",
            severity="CRITICAL",
            podName=pod,
            namespace=random.choice(self.NAMESPACES),
            container="main",
            image=random.choice(self.IMAGES),
            reason=f"Privilege escalation: {escalation}",
            action="TERMINATED",
            policyName="default-security-policy",
            nodeName=random.choice(self.NODES),
            description=f"Detected {escalation} which may indicate container escape attempt. Immediate action taken.",
        )
    
    def _run(self) -> None:
        """Main simulation loop."""
        while not self._stop_event.is_set():
            try:
                event = self._generate_random_event()
                self._callback(event)
            except Exception as e:
                # Log but don't crash the simulation
                print(f"Simulation error: {e}")
            
            self._stop_event.wait(self._interval)
    
    def start(self) -> None:
        """Start the simulation background thread."""
        if not self._enabled:
            return
            
        if self._running:
            return
        
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the simulation background thread."""
        if not self._running:
            return
        
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if simulation is running."""
        return self._running
