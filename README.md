# Role-Based Access Control (RBAC) Security System

This document outlines the step-by-step instructions and architectural design used to implement token-based security across the backend system. The perimeter guard architecture ensures a strict division of access between administrative actions and clinical medical workflows.

---

##  Security Architecture Overview

The backend enforces security by verifying authorization status at the HTTP router perimeter before any business logic, domain use cases, or database queries are reached. 

1. **Authentication Gate:** The system uses standard JSON Web Tokens (JWT). When a user provides valid credentials, the backend generates an encrypted token that encapsulates the user's explicit database role (e.g., `Admin` or `Radiologist`).
2. **Authorization Perimeter:** Individual application routers are wrapped with security dependencies. These dependencies decode incoming tokens, verify cryptographic integrity, check the role embedded inside, and either allow execution or drop the connection.

---

##  Step-by-Step Implementation Instructions

### Step 1: Provisioning the Cryptographic Security Library
To sign, issue, and securely read JSON Web Tokens, ensure the environment has a standards-compliant processing engine installed:
* Execute the Python package installer tool to add the `pyjwt` library to your virtual environment dependency list.

### Step 2: Parameter and Constant Declarations
Establish the cryptographic environment constants required for token management. These are typically stored in global configuration spaces or a security-specific settings file:
* **The Signing Secret Key:** Define a long, cryptographically secure random string used to hash token signatures.
* **The Encryption Hashing Algorithm:** Specify an industry-standard symmetric algorithm, such as `HS256`.

### Step 3: Constructing Perimeter Guards in Dependencies
In your application dependency module, create two connected gatekeeping mechanisms:
1. **The Extraction and Token-Verification Layer:**
   * Configure a route dependency to automatically listen to incoming request headers for the standard HTTP authentication scheme (`Bearer <token>`).
   * Attempt to decode the incoming cryptographic signature using your defined secret key.
   * **Exception Handling Rule:** If the token signature is altered, expired, or malformed, immediately halt execution and reply with an HTTP `401 Unauthorized` response status. If valid, pass the inner payload contents down the chain.
2. **The Reusable Role Filter Factory:**
   * Create a dynamic guard utility that can accept a custom list of permitted roles (such as `["Admin"]` or `["Radiologist"]`).
   * Instruct this guard to read the decoded payload claims from the extraction layer.
   * **Guard Condition Rule:** Look up the user's embedded role. If their specific role configuration is not included in the permitted list, intercept the request instantly and return an HTTP `403 Forbidden` response.

### Step 4: Integrating Role Extraction in the Login Logic
Modify the internal user login router handler to attach permissions directly to the token generation step:
* Once credentials successfully pass password-hashing verifications, fetch the user's designated profile from the database.
* Compile an identity payload dictionary containing their unique email address.
* **Critical Step:** Bind the user's explicit role classification string (e.g., `Admin` or `Radiologist`) directly into the payload data matrix.
* Attach a deterministic token expiration timestamp (e.g., 8 hours) to prevent open-ended token reuse.
* Cryptographically sign and encode this complete payload dictionary using the secret key, and return the final token string to the client application.

### Step 5: Applying Guards to Target Endpoints
Protect specific feature modules by attaching the role guard utilities directly to your router file endpoints through the framework’s dependency injection parameters:
* **Protecting Admin Management Pages:** Inject a guard restricting access exclusively to `["Admin"]` roles on routes managing user profile registration, personnel list view mappings, or staff deletions.
* **Protecting Clinical Doctor Pages:** Inject a guard restricting access exclusively to `["Radiologist"]` roles on workflows handling neural scanning queues, medical image processing analysis, or patient diagnosis lookups.

### Step 6: Operational Security Testing via the Interactive Docs UI
Verify the end-to-end security workflows by leveraging the built-in interactive Swagger UI framework:
1. Boot up the local web service environment.
2. Navigate to the interactive documentation path (`/docs`) using a web browser. A green **Authorize** padlocks widget will now populate the upper dashboard layout.
3. Call the authentication login endpoint using a registered account to receive a valid bearer token string.
4. Open the global **Authorize** prompt, input the raw token string into the data submission field, and save the settings.
5. Attempt to trigger an administrative management task (like deleting a user) while authenticated under a doctor-level role token. The perimeter guard will recognize the permission conflict, stop execution before hitting the use-case layer, and cleanly return an HTTP `403 Forbidden` response.