# Hardened Roboflow Inference Deployment on GKE (DevSecOps Blueprint)

A reference architecture demonstrating how to deploy and operate the **Roboflow Inference Server** securely on **Google Kubernetes Engine (GKE)** with automated CI/CD security guardrails and defense-in-depth container hardening.

## Architecture & Security Principles

Rather than treating security as a post-deployment checkbox, this repository embeds automated guardrails directly into the development and deployment lifecycle:

1. **Shift-Left CI/CD Security (`devsecops-pipeline.yml`)**:
   - **Secret Hygiene (`Gitleaks`)**: Blocks commits containing hardcoded `ROBOFLOW_API_KEY` or cloud credentials before they reach version control.
   - **IaC Compliance (`Checkov`)**: Validates Terraform configurations to prevent overly permissive IAM roles or exposed cluster endpoints.
   - **Supply Chain Scanning (`Trivy`)**: Continuously scans container base images for `CRITICAL` OS and library CVEs prior to deployment.

2. **Zero-Trust Container Hardening (`k8s/deployment.yaml`)**:
   - **Least-Privilege Execution**: Enforces `runAsNonRoot: true`, drops all Linux capabilities (`drop: ["ALL"]`), disables privilege escalation, and sets `automountServiceAccountToken: false` to minimize blast radius.
   - **Immutable Filesystem**: Enforces `readOnlyRootFilesystem: true` with a size-bounded `emptyDir` volume mounted at `/tmp` for ephemeral model caching.
   - **Resource & DoS Protection**: Hard CPU/memory limits prevent oversized image payloads from triggering Out-Of-Memory (OOM) node crashes.

---

## Threat Model (STRIDE-Inspired Summary)

| Threat Scenario | Potential Impact | Architectural Mitigation |
| :--- | :--- | :--- |
| **Credential Leakage** | Unauthorized API usage & quota exhaustion | Secrets injected strictly via K8s Secrets / Secret Manager; enforced by `Gitleaks` in CI. |
| **Container Breakout** | Host node compromise or lateral cluster movement | Non-root user (`UID 10001`), `RuntimeDefault` seccomp profile, read-only root FS, and disabled SA token mounting. |
| **Payload-Based DoS** | High-resolution images exhausting node RAM (OOM) | Strict K8s `resources.limits` (4Gi RAM / 2 CPU) and bounded `/tmp` cache (`1Gi`). |
| **Vulnerable Base Image** | Exploitation of unpatched OS/Python dependencies | Automated `Trivy` vulnerability gate failing builds on unpatched `CRITICAL` CVEs. |

---

## Quick Start (Local Docker Verification)

1. **Start the Roboflow Inference Server locally:**
   ```bash
   docker run -d --name roboflow-inference -p 9001:9001 roboflow/roboflow-inference-server-cpu:latest
   ```

2. **Run the Python inference client securely via environment variables:**
   ```bash
   export ROBOFLOW_API_KEY="your_actual_api_key_here"
   pip install requests
   python app/test_inference.py
   ```
