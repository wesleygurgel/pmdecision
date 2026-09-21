# Detalhamento

Campo HTML `Detalhamento`, obrigatório (`Detalhe a atividade.`). O textarea não tem `maxlength` no HTML, mas o teto que usamos na geração é **250 caracteres** (tag inclusive).

## Escolha da pasta (decisão D13)

Ao iniciar a automação (dry-run ou apply), abrir um **seletor nativo de pasta do Windows** (IFileOpenDialog com `FOS_PICKFOLDERS` — o diálogo que parece o File Explorer, não o `FolderBrowserDialog` antigo em árvore nem um `tkinter` genérico).

Diretório inicial do diálogo:

1. Última pasta salva, se o caminho ainda existir
2. Senão: `C:\Users\Wesley-\Documents\Repositorios\first`

### Timeout de 1 minuto

O diálogo nativo é modal e bloqueante. Por isso o picker **roda em subprocesso**. O processo pai espera **60 segundos**.

| Resultado | Ação |
|---|---|
| Pasta selecionada antes de 60s | Usar essa pasta, gravar como última escolhida, seguir |
| Usuário cancelou o diálogo | Igual ao timeout: última pasta salva |
| 60s sem escolha (não está no PC, diálogo ainda aberto) | Matar o subprocesso do picker e usar a última pasta salva |
| Timeout/cancel **e** não há última pasta (primeiro run) | Não abortar o ponto. Seguir com fallback mínimo de texto, **sem** Git. Logar aviso claro |

Constante: `FOLDER_PICKER_TIMEOUT_SECONDS = 60`.

### Onde guardar a última pasta

Arquivo **fora do Git**, específico da máquina:

`%LOCALAPPDATA%\pm-decision\state.json`

Exemplo:

```json
{
  "last_repo_path": "C:\\Users\\Wesley-\\Documents\\Repositorios\\first\\conecta-industria",
  "selected_at": "2026-09-21T09:36:00-03:00"
}
```

Gravar só depois de uma seleção explícita no diálogo (não sobrescrever a última pasta num timeout). Se a última pasta foi apagada, tratar como “não há última pasta”.

### Override para teste

`--repo C:\caminho\completo` (ou nome relativo a `first\`) **não abre** o Explorer. Não é o fluxo diário.

Não usar `ACTIVE_REPO` no `.env` como forma principal — a memória fica no `state.json`.

## Resolver o Git da pasta escolhida

Não inferir o repo pela data de commit entre as pastas de `first\` (vários projetos ficam semanas sem commit).

Na pasta escolhida:

- `{pasta}/.git` se existir
- senão, o `.git` mais próximo **dentro** dessa pasta (monorepo / frontend+backend). Se houver mais de um, preferir o com `HEAD` mais recente; se ainda ambíguo, falhar o Git e cair no fallback mínimo de texto

A **data do último commit não importa**. Sempre usar `HEAD` atual.

`conecta-industria` (2026-09-21) não tem `.git` na raiz — nested git é obrigatório.

## Como montar o texto

Formato: `[TAG] ` + uma frase em **primeira pessoa** (`Melhorei`, `Ajustei`, `Fiz`, `Implementei`). Total ≤ **250** caracteres, tag inclusive.

A tag é o **primeiro diretório** sob `REPOSITORIES_ROOT`, em maiúsculas. Ex.: pasta `...\first\conecta-industria\conecta-industria-frontend` → `[CONECTA-INDUSTRIA]`.

O modelo gera só o corpo; o código prefixa a tag (evita tag duplicada ou errada).

Ordem:

1. **IA (se houver `OPENAI_API_KEY`)**  
   Modelo: **`gpt-4o-mini`**. Prompt em primeira pessoa, sem tag. Timeout 10s. Falha → (2).

2. **Fallback sem IA**  
   `[TAG] Trabalhei nisto: {subject do HEAD}`. Subject inútil → (3).

3. **Fallback mínimo**  
   Com pasta: `[TAG] Trabalhei no desenvolvimento do projeto.`  
   Sem pasta: `Trabalhei no desenvolvimento e manutenção do projeto em andamento.`

Não inventar demanda/ticket. Não colocar horário, usuário ou dados do PM Decision no detalhamento.

## Exemplos (tamanho ok)

- `[CONECTA-INDUSTRIA] Melhorei a gestão de demandas com visualizações detalhadas e testes mais robustos.`
- `[OID-BACKEND] Corrigi o entrypoint Docker para evitar CrashLoop no Rancher.`
