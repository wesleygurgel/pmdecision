# Descobertas do PM Decision (2026-09-21)

Análise feita com login real na conta do usuário. Conferido no browser, no HTML e nos JS da aplicação. **Não foi gravado nenhum lançamento nesta sessão.**

Sistema: [Login PM Decision](https://app.firstdecision.com.br/pmdecision/Login?ReturnURL=https://app.firstdecision.com.br:443/pmdecision/) — versão **4.0v**.

## Stack da aplicação alvo

- ASP.NET MVC (não WebForms: existe `__RequestVerificationToken`, não `__VIEWSTATE`)
- jQuery 2.1.3, Bootstrap, jQuery Validate unobtrusive, jQuery UI 1.11.4, maskedinput
- Scripts relevantes:
  - `/pmdecision/Scripts/Views/Login.js`
  - `/pmdecision/Scripts/Views/Lancamento.js`
  - `/pmdecision/Scripts/Views/EnvioAprovacaoTimesheet.js`

## Autenticação

- Form `#loginform` POST `/pmdecision/Login` (`enctype=multipart/form-data`)
- Campos: `Login`, `Senha`, `HashSenha`, `Lembrar`, `ReturnUrl`, `__RequestVerificationToken`
- `autenticacaoAD = true` na página: o submit copia a senha para `HashSenha` e zera `Senha` (não aplica SHA-1 nesse modo)
- Sem captcha
- Sessão por cookie após redirect para `/pmdecision/`
- Logout: `/pmdecision/Login/Logout`
- Menu pós-login: só **Timesheet** e **Logout**

## Menu Timesheet

| Item | URL |
|---|---|
| Consulta de Lançamento de Horas | `/pmdecision/Lancamento` |
| Enviar Horas para Aprovação | `/pmdecision/EnvioAprovacaoTimesheet` |
| Lançamento de Horas | `/pmdecision/Lancamento/Create` |

## Lançamento (`/Lancamento/Create`)

Form `#novolancamentoform` POST `/pmdecision/Lancamento/Create`, `multipart/form-data`.

### Campos (nomes HTML)

| Campo | Obrigatório | Notas |
|---|---|---|
| `MesAnoId` | sim | Combo "Timesheets Abertos". Em 09/2026 o único valor era `3151` ("09/2026"). **Não hardcodar.** |
| `ClienteId` | sim | Carregado via AJAX a partir de `MesAnoId`. Único em 09/2026: `2074` — Ministério da Gestão e da Inovação em Serviços Públicos |
| `ProjetoId` | sim | Único em 09/2026: `3076` — `MGI - 52315.000373/2026-88 - MDIC` |
| `ProjetoFuncaoId` | sim | Único em 09/2026: `3533` — Desenvolvedor Sênior |
| `TipoAtividadeId` | sim | Único em 09/2026: `2117` — Desenvolvimento |
| `Demanda` | não | Usuário deixa vazio |
| `Dia` | sim (via `DataLancamento`) | Máscara `99`. Só o dia (`16`), o mês vem de `MesAno` |
| `MesAno` | readonly | Preenchido como `/09/2026` |
| `DataLancamento` | hidden, obrigatório | Montado em JS: `{Dia}/{MesAnoId text}` → `16/09/2026`. Recusa data futura |
| `HoraInicio` | sim | Máscara `99:99` |
| `HoraTermino` | sim | Deve ser posterior a `HoraInicio` |
| `Detalhamento` | **sim** (client-side required; sem maxlength no HTML) | Mensagem: `Detalhe a atividade.` Nosso teto de geração: **250** caracteres. |
| `LancamentoId` | hidden | `0` na criação |
| `__RequestVerificationToken` | sim | Header também usado nos POSTs AJAX |

Botão de gravação: submit **Salvar lançamento**. Um POST = um intervalo (manhã **ou** tarde). Depois do save a página recarrega.

### Cascata AJAX (GET JSON)

Base: `{urlBase}Lancamento/...` com `urlBase` = `https://app.firstdecision.com.br:443/pmdecision/`

- `ObterClientesFuncionario?mesAnoId=`
- `ObterProjetosCliente?mesAnoId=&clienteId=`
- `ObterDadosProjeto?mesAnoId=&projetoId=` → `Funcoes` e `Atividades`
- `ObterLancamentosDoMes?mes=&ano=` → lista do mês (usar para idempotência)
- `ObterDadosFuncionario?funcionarioId=` (consulta)
- `ObterProjetos?clienteId=&funcionarioId=&pesquisa=` (consulta)

POSTs AJAX (JSON + header `__RequestVerificationToken`):

- `Paginando` — consulta
- `Removendo` — exclusão
- `LancamentosMesPaginando` — tabela "Atividades Lançadas no Mês"

Se a lista de clientes/projetos/funções/atividades tiver **um** item, o JS auto-seleciona (não inclui option "Selecione").

## Consulta (`/Lancamento`)

- Funcionário logado: **Wesley Gurgel Marcelino de Oliveira**, `FuncionarioId=3739`
- Filtros: `FiltroMesAno` (`99/9999`), `FuncionarioId`, `FiltroClienteId`, `TipoVisao` (0 calendário / 1 tabela)
- Clientes visíveis no filtro: First Decision (`1`) e MGI (`2074`)

## Envio para aprovação (fora do v1)

- GET `ObterTimesheets?projetoId=&mesAnoId=`
- POST `EnviarParaAprovacaoTimesheets`
- Em 21/09/2026 o mês `09/2026` (`3151`) já aparecia como pendente de envio

## Snapshot de setembro/2026 na data da análise

- Total do mês: **168:00:00**
- Já trabalhadas: **80:00:00** (10 dias × 8h)
- Sempre 2 linhas/dia, tipo Desenvolvimento, projeto MDIC, demanda vazia
- Dias lançados: 01, 02, 03, 04, 08, 09, 10, 11, 14, 15
- 07/09 ausente (feriado nacional)
- 05–06 e 12–13 ausentes (fim de semana)
- **Pendentes até 21/09: 16, 17, 18, 21**

Exemplos reais de intervalos (sempre 8h + 1h almoço):

- 08:52–12:53 / 13:53–17:52
- 08:45–11:39 / 12:39–17:45
- 09:00–12:33 / 13:33–18:00

Legendas da própria tela:

- Horas inválidas: totais no dia acima de 8 horas
- Horas inválidas: totais no dia abaixo de 8 horas
- Horas inválidas: não tem o intervalo de 1 hora de almoço

## Login.js — detalhe útil

Função `Autenticar()` (AJAX `/Login/Index`) faz SHA-1, mas o submit do form **não** usa essa função quando `autenticacaoAD === true`. Playwright deve preencher usuário/senha e clicar **Entrar**, deixando o JS nativo tratar `HashSenha`.

## Identificadores observados (podem mudar)

Não persistir como constantes de mês. Ler da tela/AJAX:

- `identificador` hidden da sessão: UUID por página
- `MesAnoId` 3151 só para 09/2026
- IDs de cliente/projeto/função/atividade acima são do contrato atual; se o combo passar a ter mais de uma opção, a automação deve falhar de forma explícita em vez de escolher no chute
