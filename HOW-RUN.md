# Comandos

Na pasta do projeto, com o venv ativo (`C:\Users\Wesley-\venv` ou `.venv` do projeto) e o `.env` preenchido:

```bat
python -m pm_decision
```

Sem `--apply` **não grava nada** — só mostra o plano.

## Dry-run (não grava)

Abre o File Explorer (até 60s) e lista os dias pendentes:

```bat
python -m pm_decision
```

Se você não escolher pasta em 1 minuto, usa a última salva.

## Gravar todos os dias pendentes

Hoje + atrasados do mês aberto (pula fim de semana, feriado e dia já completo):

```bat
python -m pm_decision --apply
```

## Gravar um único dia

```bat
python -m pm_decision --apply --only-date 2026-09-16
```

Dry-run de um dia só (sem gravar):

```bat
python -m pm_decision --only-date 2026-09-16
```

## Escolher o repositório no File Explorer

Não passe `--repo`. O diálogo nativo abre para você selecionar a pasta do Git (detalhamento).

```bat
python -m pm_decision --apply
```

## Informar o repositório na linha de comando (pula o Explorer)

Caminho completo:

```bat
python -m pm_decision --apply --repo C:\Users\Wesley-\Documents\Repositorios\first\conecta-industria
```

Ou o nome da pasta dentro de `Repositorios\first`:

```bat
python -m pm_decision --apply --repo conecta-industria
```

## Ver o Chromium (debug)

```bat
python -m pm_decision --headed
python -m pm_decision --apply --headed --only-date 2026-09-16
```

## Combinar flags

```bat
python -m pm_decision --apply --only-date 2026-09-21 --repo conecta-industria --headed
```

Envio para aprovação no PM Decision continua **manual**.

## Agendamento (Task Scheduler)

Tarefa `pm-decision-daily`: segunda a sexta às **10:00**, com `--apply`.

- Runner: `scripts\run-daily.cmd`
- Logs: `%LOCALAPPDATA%\pm-decision\logs\daily-YYYY-MM-DD.log`
- Re-registrar (ou recriar após mudança de path):

```bat
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\register-daily-task.ps1
```

A tarefa usa a última pasta salva se o File Explorer não for respondido (timeout 60s).

## Testes

Instalar a extra de desenvolvimento e rodar a suíte **completa** (obrigatório depois de qualquer mudança):

```bat
python -m pip install -e ".[dev]"
python -m pytest
```

TDD: escrever o teste que falha primeiro, implementar o mínimo, só então rodar `python -m pytest` de novo. A suíte é unitária — não abre o PM Decision nem o File Explorer.
