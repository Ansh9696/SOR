# Security Policy

SOR is an early-stage project. A formal supported-version policy and security response SLA have not yet been established.

## Reporting a vulnerability

Please do not publish exploitable vulnerability details, credentials, tokens, or private data in public issues.

Use GitHub's **Private vulnerability reporting** feature for this repository if it is enabled. If it is not enabled, contact the repository maintainer privately through a verified contact method listed on the maintainer's GitHub profile and ask for a secure reporting channel.

Include, where safe:

- Affected commit, branch, or component.
- Impact and prerequisites.
- Reproduction steps or a minimal proof of concept.
- Suggested mitigation, if known.

Please allow the maintainer reasonable time to investigate and prepare a fix before public disclosure.

## Secrets

Never commit API keys, passwords, access tokens, private keys, or production data. If a secret is exposed, revoke or rotate it immediately; deleting it from the latest commit does not make it safe.
