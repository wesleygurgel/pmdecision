# Plano de implementação

v1 de código existe (dry-run por padrão). `--apply` grava de verdade — usar `--only-date` no primeiro save.

## Princípios

- Dry-run primeiro; gravar no PM Decision só com `--apply`
- IDs de mês/projeto lidos da tela, não hardcoded
- Senha só em `.env`
- Um dia = dois saves; se o segundo falhar, reportar quantos dias deste run já gravaram
- OpenAI `gpt-4o-mini` opcional; fallback Git / texto genérico

## Estrutura

```
pm-decision/
  docs/
  .env.example
  pyproject.toml
  src/pm_decision/
    constants.py
    settings.py
    hours.py
    work_calendar.py
    state_store.py
    folder_picker.py
    repository_selection.py
    git_source.py
    detalhamento.py
    timesheet_browser.py
    planner.py
    cli.py
```

## Como rodar

O `python` precisa ser o interpretador onde o pacote foi instalado. O venv da home (`C:\Users\Wesley-\venv`) **não** vê o módulo até `pip install -e .` nele.

```bat
cd C:\Users\Wesley-\Documents\Repositorios\first\pm-decision
C:\Users\Wesley-\venv\Scripts\python.exe -m pip install -e .
C:\Users\Wesley-\venv\Scripts\python.exe -m playwright install chromium
```

Ou use o `.venv` do próprio projeto.

Preencher `.env` (usuário, senha; `OPENAI_API_KEY` opcional).

```bat
python -m pm_decision --repo C:\Users\Wesley-\Documents\Repositorios\first\sdic_api
python -m pm_decision --apply --only-date 2026-09-16
python -m pm_decision --apply
```

Sem `--repo`, abre o File Explorer por até 60s.

## Fases

- F1 Fundação — feito
- F2 Playwright dry-run — feito
- F3 `--apply` + `--only-date` — código pronto; primeiro save real ainda a conferir na UI
- F4 job diário / Task Scheduler — depois do primeiro apply validado
- F5 envio para aprovação — fora

## Critérios de pronto do v1

- Dry-run não altera dados
- `--apply` lança exatamente 8h + 1h almoço
- Não duplica dia já preenchido
- Detalhamento não vazio, ≤ 250 caracteres
- Credenciais fora do Git
