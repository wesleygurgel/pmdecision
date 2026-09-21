# Decisões vigentes

Datas no formato ISO. Alterar só com confirmação do usuário.

## 2026-09-21 — produto

| ID | Decisão | Motivo |
|---|---|---|
| D01 | Stack: **Python 3 + Playwright (headless)** | App legado ASP.NET MVC + jQuery, máscaras, CSRF e dropdowns AJAX. Reaproveita `ponto.py`. |
| D02 | HTTP puro (`httpx`) é plano B, não v1 | Endpoints mapeados, mas o Create é form `multipart` com token e validadores de tela. |
| D03 | Escopo v1: **dia corrente + dias atrasados** do mês aberto | Há gap em 16, 17, 18 e 21/09/2026. |
| D04 | Horário de execução **livre** | Só precisa cumprir 8h + 1h de almoço, como o `ponto.py`. |
| D05 | **Não** automatizar envio para aprovação | Usuário faz manual quando necessário. |
| D06 | Dois lançamentos por dia útil (manhã + tarde) | Padrão histórico no sistema e regra de almoço de 1h. |
| D07 | Pular fim de semana, feriado nacional BR e dia já lançado | 07/09/2026 (Independência) não foi lançado; sábados/domingos também não. |
| D08 | Não lançar data futura | Validador do form: `Não pode ser uma data futura.` |
| D09 | Credenciais só em `.env` gitignored | Login AD; senha não vai para o Git. |
| D10 | Detalhamento ≤ 180 caracteres a partir do Git da pasta escolhida | Pedido do cliente do timesheet. Fallback simples se a IA/Git falhar. |
| D11 | Demanda permanece vazia | Histórico do usuário está vazio nesse campo. |
| D12 | Cliente/projeto/função/atividade: usar os únicos disponíveis no mês aberto, sem hardcode de IDs mensais | Em 09/2026: MGI / MDIC / Desenvolvedor Sênior / Desenvolvimento. `MesAnoId` muda todo mês. |
| D13 | Escolha da pasta: **diálogo nativo do Windows** (estilo File Explorer), timeout **60s**, senão usa a **última pasta salva** | O usuário pode não estar no PC quando o job rodar. `--repo` fica só como override de teste. |
| D14 | IA do detalhamento: **OpenAI `gpt-4o-mini`**, chave opcional; 3 degraus (IA → subject Git → texto genérico) | Uma chamada por run. Sem chave o script já funciona. |
| D15 | Detalhamento em **primeira pessoa** com tag `[REPOSITORIO]` no início | Ex.: `[CONECTA-INDUSTRIA] Melhorei a gestão de demandas...`. Tag = 1º diretório sob `first\`. |

## Fora de escopo (até nova decisão)

- Tela Consulta, exceto leitura para idempotência
- Envio para aprovação
- UI gráfica (exceção: o folder picker nativo do Windows, D13)
- Agendamento no Task Scheduler (só depois do dry-run + um dia real conferido)
- Ponto da empresa empregadora (app celular)
