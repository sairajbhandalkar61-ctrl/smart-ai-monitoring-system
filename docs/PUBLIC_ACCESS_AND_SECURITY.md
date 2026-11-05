# SENTINEL AI — Public Access and Security Protocol

---

## 1. Authentication & Role-Based Access Control (RBAC)

SENTINEL AI protects all cloud monitoring endpoints behind a cryptographic authentication barrier.

### Standard Roles & Permissions:

| Role | Permissions | Use Case | Default Account |
| :--- | :--- | :--- | :--- |
| **Administrator** | Full system control: manual count reconciliation, edge device registration, user management, and system configuration. | Campus Facilities Lead / Security Director | `admin` / `SentinelAdmin2026!` |
| **Operator** | Live monitoring, alert acknowledgement, viewing reports, and telemetry inspection. | Security Desk Officer / Floor Warden | `operator` / `Operator2026!` |
| **Viewer** | Read-only access to macro dashboard and aggregated zone utilization. | Institutional Auditors / General Staff | Configurable |

### Password Storage Security:
* Passwords are never stored in plaintext.
* Derived using **PBKDF2-HMAC-SHA256** with unique 16-byte random cryptographic salts and 100,000 hashing iterations.
* Constant-time comparison (`secrets.compare_digest`) protects against timing attacks.

---

## 2. Network & Public Transport Security

1. **Mandatory HTTPS:** All traffic between clients and the cloud dashboard is encrypted via TLS 1.3 / HTTPS.
2. **Edge Security Token:** Outbound requests from the Dell laptop require an `EDGE_DEVICE_TOKEN` header or payload verification.
3. **Restricted CORS Policy:** Cross-Origin Resource Sharing is configurable via `CORS_ALLOWED_ORIGINS` to prevent unauthorized domain embedding.
4. **No Raw Video Over the Internet:** Raw video frames are processed in-memory on the laptop CPU and immediately discarded, eliminating privacy exposure.
