# PM Decision — contexto para agentes

Automação pessoal do timesheet no PM Decision (First Decision / MGI), substituindo o preenchimento manual diário de 8h com 1h de almoço.

Este diretório é a fonte de contexto para qualquer agente. **Confie no código em `src/pm_decision/` quando divergir destes docs.**

## Leia nesta ordem

1. [DECISOES.md](DECISOES.md) — o que já foi decidido (não reabrir sem o usuário)
2. [2026-09-21-descobertas-pm-decision.md](2026-09-21-descobertas-pm-decision.md) — sistema real (URLs, campos, AJAX, regras)
3. [REGRAS-NEGOCIO.md](REGRAS-NEGOCIO.md) — 8h, almoço, feriados, atrasados
4. [DETALHAMENTO.md](DETALHAMENTO.md) — File Explorer (timeout 60s / última pasta) e texto com tag + primeira pessoa
5. [PLANO-IMPLEMENTACAO.md](PLANO-IMPLEMENTACAO.md) — o que implementar e em que ordem

Bug, feature nova ou refactor: **TDD**. Escrever teste que falha em `tests/`, implementar, rodar `python -m pytest` (suíte completa). Sem atalho de “só o arquivo que eu toquei”.

## Estado do repositório

- Código em `src/pm_decision/` (CLI `python -m pm_decision`)
- Testes em `tests/` (`python -m pytest`)
- Dry-run é o padrão; `--apply` grava no PM Decision
- Job diário no Task Scheduler: `pm-decision-daily` (seg–sex 10:00) — ver `HOW-RUN.md`
- Credenciais em `.env` (gitignored). Modelo de detalhamento: `gpt-4o-mini`
- Gerador original de horários (referência): `C:\Users\Wesley-\ponto.py`

## O que este projeto NÃO é

- Não envia hours para aprovação (tela `/EnvioAprovacaoTimesheet` fica manual)
- Não deve gravar senha em arquivo versionado nem nestes docs

## Credenciais

Usar variáveis de ambiente (`.env` local, gitignored), nunca hardcoded:

- `PM_DECISION_USER`
- `PM_DECISION_PASSWORD`
- `PM_DECISION_BASE_URL` (default `https://app.firstdecision.com.br/pmdecision`)

O usuário já autenticou com sucesso neste ambiente em 2026-09-21. Não repetir a senha em chat, commit ou documentação.
