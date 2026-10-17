# Cybersecurity Portfolio

Independent projects and labs organized by area. The three highlights were chosen for combining a working implementation, automated tests, a reproducible demo, and an honest account of their limits.

## Highlights

| Project | Skill demonstrated | Demo |
| --- | --- | --- |
| [SSH Watch](https://github.com/alefkaue/ssh-watch) | SOC: log parsing, time-based correlation, and evidence | Detect three SSH failures and the login that follows |
| [Integrity Guard](https://github.com/alefkaue/integrity-guard) | Blue Team: SHA-256, baselines, and change detection | Build an inventory and flag a modified file |
| [IAM Policy Lens](https://github.com/alefkaue/iam-policy-lens) | Cloud Security: permission review and recommendations | Compare a broad policy with a scoped one |

All three are pure Python with no external dependencies, include synthetic examples, and run tests on GitHub Actions across Linux and Windows. Each README explains how to reproduce the result and what the tool cannot conclude.

## Supporting tools

| Area | Project | Scope |
| --- | --- | --- |
| Network security / inventory | [Nmap Surface Diff](https://github.com/alefkaue/nmap-surface-diff) | Offline diff of Nmap XML — observed endpoints and scope changes |
| Network security / policy | [Firewall Rule Lens](https://github.com/alefkaue/firewall-rule-lens) | First-match rule review in JSON — shadowing and overly broad sources |
| Linux / hardening | [Linux Permission Audit](https://github.com/alefkaue/linux-permission-audit) | Unix permission review with an optional POSIX metadata collector |
| Threat Intelligence / triage | [IOC Workbench](https://github.com/alefkaue/ioc-workbench) | Indicator normalization, deduplication, and provenance — no external lookups |
| AppSec | [Header Sentry](https://github.com/alefkaue/header-sentry) | Offline HTTP header review with JSON findings |
| SOC / fundamentals | [Mini SOC Analyzer](https://github.com/alefkaue/mini-soc-analyzer) | Introductory security-event analysis in Python |
| Pentest / lab | [Pentest Ponto Cego](https://github.com/alefkaue/pentest-ponto-cego) | Lab report, evidence, and documentation |

## How to explore

Start with a highlight's README, run the example, then the tests. Change an input and explain why the output changed. The projects document their false positives and limitations so they hold up to technical discussion in interviews.

The newer utilities were built with AI assistance; the goal is to keep the code and the decisions open to review, with a verifiable scope. Coursework and web-development repositories remain available under the profile's Repositories tab, kept separate from this curated cybersecurity selection.
