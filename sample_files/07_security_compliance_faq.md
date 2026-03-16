# Security & Compliance — FAQ

## Is NovaDesk SOC 2 compliant?

Yes. NovaDesk is **SOC 2 Type II certified**. Our latest audit report is available to Enterprise customers under NDA. Contact security@novadesk.io to request a copy.

## Is data encrypted?

Yes. All data is encrypted:
- **In transit** — TLS 1.2 and 1.3
- **At rest** — AES-256 encryption on all storage systems

## Where is data stored?

By default, customer data is stored in **AWS US-East-1** (Virginia, USA). Enterprise customers can request **data residency in the EU** (AWS eu-west-1, Ireland) or the **Asia-Pacific region** (AWS ap-southeast-1, Singapore) for an additional fee.

## Is NovaDesk GDPR compliant?

Yes. NovaDesk is fully GDPR compliant. Key features include:
- **Data export** — Export all data for a contact on request.
- **Right to erasure** — Permanently delete a contact and all associated data via Settings or the API.
- **Data Processing Agreement (DPA)** — Available for all customers at [novadesk.io/legal/dpa](https://novadesk.io/legal/dpa).

## Is NovaDesk HIPAA compliant?

NovaDesk can sign a **Business Associate Agreement (BAA)** for Enterprise customers who handle Protected Health Information (PHI). Contact sales@novadesk.io to arrange this.

## What authentication options are available?

- **Email & password** (all plans)
- **Google SSO / Microsoft SSO** (all plans)
- **SAML 2.0 SSO** (Enterprise only — supports Okta, Azure AD, OneLogin)
- **Two-Factor Authentication (2FA)** via authenticator app (all plans)
- Admins can **enforce 2FA** for all agents on Growth and Enterprise plans.

## Does NovaDesk conduct penetration testing?

Yes. We conduct third-party penetration tests at least **once per year**. Findings are remediated according to severity, and summaries are available to Enterprise customers upon request.

## How do I report a security vulnerability?

Please disclose vulnerabilities responsibly via our bug bounty program at [novadesk.io/security](https://novadesk.io/security) or email security@novadesk.io. We aim to respond within 48 hours.
