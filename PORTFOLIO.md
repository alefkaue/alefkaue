# Portfólio de cibersegurança

Projetos independentes e laboratórios organizados por área. Os três destaques foram escolhidos pela combinação de implementação funcional, testes automatizados, demonstração reproduzível e explicação dos limites.

## Destaques

| Projeto | Competência demonstrada | Demonstração |
| --- | --- | --- |
| [SSH Watch](https://github.com/alefkaue/ssh-watch) | SOC: parsing de logs, correlação temporal e evidências | Detectar três falhas SSH e o login posterior |
| [Integrity Guard](https://github.com/alefkaue/integrity-guard) | Blue Team: SHA-256, baseline e detecção de alterações | Criar inventário e identificar arquivo modificado |
| [IAM Policy Lens](https://github.com/alefkaue/iam-policy-lens) | Cloud Security: revisão de permissões e recomendações | Comparar uma política ampla com uma política delimitada |

Os três usam Python sem dependências externas, incluem exemplos sintéticos e executam testes no GitHub Actions em Linux e Windows. Cada README explica como reproduzir o resultado e o que a ferramenta não consegue concluir.

## Ferramentas complementares

| Área | Projeto | Escopo |
| --- | --- | --- |
| Segurança de redes / inventário | [Nmap Surface Diff](https://github.com/alefkaue/nmap-surface-diff) | Comparação offline de XML do Nmap, endpoints observados e mudanças de escopo |
| Segurança de redes / políticas | [Firewall Rule Lens](https://github.com/alefkaue/firewall-rule-lens) | Revisão de regras first-match em JSON, encobrimento e origens amplas |
| Linux / hardening | [Linux Permission Audit](https://github.com/alefkaue/linux-permission-audit) | Revisão de permissões Unix com coletor opcional de metadados POSIX |
| Threat Intelligence / triagem | [IOC Workbench](https://github.com/alefkaue/ioc-workbench) | Normalização, deduplicação e proveniência de indicadores, sem consultas externas |
| AppSec | [Header Sentry](https://github.com/alefkaue/header-sentry) | Revisão offline de cabeçalhos HTTP com achados JSON |
| SOC / fundamentos | [Mini SOC Analyzer](https://github.com/alefkaue/mini-soc-analyzer) | Análise introdutória de eventos de segurança em Python |
| Pentest / laboratório | [Pentest Ponto Cego](https://github.com/alefkaue/pentest-ponto-cego) | Relatório, evidências e documentação do laboratório |

## Como explorar

Comece pelo README de um destaque, execute o exemplo e depois os testes. Altere um dado de entrada e explique por que a saída mudou. Os projetos documentam falsos positivos e limitações para permitir discussão técnica em entrevistas.

Os novos utilitários foram desenvolvidos com assistência de IA; a proposta é manter código e decisões abertos à revisão, com escopo verificável. Repositórios de aulas e desenvolvimento web continuam acessíveis na aba de repositórios do perfil, separados desta seleção editorial de cibersegurança.
