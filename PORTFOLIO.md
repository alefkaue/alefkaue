# Cybersecurity Portfolio

Academic and personal projects organized by area. The highlights combine documented scope, reproducible examples and honest limits. New utilities were built with AI assistance; they are not claims of professional operations or production use.

## Highlights

| Project | Skill demonstrated | Demo |
| --- | --- | --- |
| [SIMOC Integrador / CYMAG](https://github.com/alefkaue/simoc-integrador) | Academic team project: authorized lab, Python automation and Groq/Llama integration | Read the academic scope and technical/executive reporting work |
| [Cyber CTF Write-ups](https://github.com/alefkaue/cyber-ctf-writeups) | Completed RSA case and partial forensic investigation; 3rd place overall reported by the participant | Run the sanitized offline Python demonstrations |
| [PHP2Shell Security Assessor](https://github.com/alefkaue/php2shell-security-assessor) | Evidence-aware version, vendor-backport and lifecycle triage in Python | Compare a synthetic affected version, vendor package and unconfirmed banner |
| [JAR Surface Auditor](https://github.com/alefkaue/jar-surface-auditor) | Java: bounded archive metadata, safe-path review and class-runtime compatibility | Inspect an owned JAR without executing or extracting it |
| [Service Posture Auditor](https://github.com/alefkaue/service-posture-auditor) | C#: Windows service command lines and explicit ACL evidence | Compare a quoted path, ambiguous candidate and unresolved environment path |
| [PCAP DNS Guard](https://github.com/alefkaue/pcap-dns-guard) | C++20: bounded binary parsing, packet offsets and malformed-input tests | Inspect a generated synthetic PCAP offline |

Each README explains how to reproduce the result and what the project cannot conclude. Personal utilities include synthetic fixtures and automated tests. SIMOC remains an academic team project with its own historical scope, not an interchangeable personal utility.

## Supporting tools

| Area | Project | Scope |
| --- | --- | --- |
| AppSec / C# | [Dotnet Config Auditor](https://github.com/alefkaue/dotnet-config-auditor) | Review one configuration layer without exporting sensitive values |
| Binary analysis / C++ | [PE Hardening Lens](https://github.com/alefkaue/pe-hardening-lens) | Parse PE metadata and declared protection flags without execution |
| DNS / evidence | [DNS Trace Investigator](https://github.com/alefkaue/dns-trace-investigator) | Offline DNS patterns, DHCP timing and evidence provenance |
| SOC / Python | [SSH Watch](https://github.com/alefkaue/ssh-watch) | Failure bursts and subsequent login correlation |
| Integrity / Python | [Integrity Guard](https://github.com/alefkaue/integrity-guard) | Baselines and file-change evidence |
| Cloud / Python | [IAM Policy Lens](https://github.com/alefkaue/iam-policy-lens) | Offline policy review and scope reasoning |
| Java / artifact integrity | [Artifact Hash Guard](https://github.com/alefkaue/artifact-hash-guard) | Offline SHA-256 manifest verification, safe-path checks and file integrity reports |
| C# / authentication triage | [Auth Event Lens](https://github.com/alefkaue/auth-event-lens) | Normalized authentication events, multi-account failure patterns and success correlation |
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
