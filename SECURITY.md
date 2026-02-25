# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes    |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Please report security issues by opening a [GitHub Security Advisory](https://github.com/tracecontext-ai/tracecontext/security/advisories/new) on this repository.

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 72 hours and work with you to release a fix.

## API Keys

Never commit API keys or secrets to this repository. The `.env` file is gitignored.
Use `.env.example` as a template and keep real credentials local only.
