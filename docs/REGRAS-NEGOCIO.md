# Regras de negócio do lançamento

Fonte de verdade da jornada: `C:\Users\Wesley-\ponto.py` (copiar/adaptar para dentro deste repo na implementação; não editar o arquivo da home sem necessidade).

## Jornada de um dia útil

1. Entrada aleatória entre **08:45** e **09:15**
2. Início do almoço aleatório entre **11:30** e **14:00**
3. Fim do almoço = início + **1 hora** (fixo)
4. Saída = entrada + **8h de trabalho** + **1h de almoço**
5. Dois POSTs no PM Decision:
   - Manhã: `HoraInicio=entrada`, `HoraTermino=início do almoço`
   - Tarde: `HoraInicio=fim do almoço`, `HoraTermino=saída`

Invariantes (o sistema marca inválido se quebrar):

- Soma dos dois intervalos = **08:00**
- Intervalo entre manhã e tarde = **01:00**
- Término > início em cada intervalo
- `DataLancamento` ≤ hoje
- Dia ainda não completo (precisa de **dois** intervalos: manhã e tarde)
- Se só a manhã existir, completar a tarde com 1h de almoço e total de 8h, sem gerar um novo dia aleatório

O gerador atual não valida explicitamente "almoço depois da entrada", mas com os ranges atuais isso sempre vale (entrada máxima 09:15, almoço mínimo 11:30).

## Quais dias lançar (v1)

- Dia corrente, se for dia útil e ainda não tiver 8h
- Dias atrasados do **mês aberto** no combo Timesheets Abertos (em 21/09/2026: 16, 17, 18, 21)
- Não lançar sábado, domingo, feriado nacional brasileiro, nem data futura
- Não relançar dia que já tenha o par manhã/tarde; dia com só um intervalo continua pendente

Feriados: usar calendário nacional BR (ex.: pacote `holidays` com `BR`). O 07/09/2026 confirmou o comportamento no histórico.

## CLI prevista

- `dry-run` — gera horários e detalhamento, não clica em Salvar
- `hoje` — só o dia corrente
- `atrasados` — gaps do mês aberto até hoje
- v1 operacional: **hoje + atrasados** no mesmo run (decisão D03)

Envio para aprovação: comando futuro, não implementar agora.
