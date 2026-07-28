# Security Policy

## Supported Versions

Security updates are applied to the latest release only. Earlier versions do not receive backported fixes.

| Version | Supported |
| ------- | --------- |
| 3.7.x   | Yes       |
| < 3.7   | No        |

## Reporting a Vulnerability

Do not open a public issue for security vulnerabilities.

Email the maintainer at [m.semoglou@tongji.edu.cn](mailto:m.semoglou@tongji.edu.cn) with:

- A description of the vulnerability
- Steps to reproduce or a proof of concept
- The affected version(s)

Expect an acknowledgment within 5 working days and a status update within 15 working days. If the report is confirmed, a fix will be developed, tested, and released as a patch version before public disclosure.

## Scope

The following are in scope:

- Code in the `renoir/` package directory
- Dependencies declared in `pyproject.toml`
- CI/CD workflows in `.github/workflows/`

The following are out of scope:

- The WikiArt dataset itself (hosted by HuggingFace)
- Third-party services (PyPI, ReadTheDocs, Codecov)
- Vulnerabilities in transitive dependencies that are already patched upstream
