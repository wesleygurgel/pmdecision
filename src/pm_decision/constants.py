from datetime import time, timedelta
from pathlib import Path

APPLICATION_NAME = "pm-decision"
DEFAULT_BASE_URL = "https://app.firstdecision.com.br/pmdecision"
DEFAULT_REPOSITORIES_ROOT = Path(r"C:\Users\Wesley-\Documents\Repositorios\first")
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

FOLDER_PICKER_TIMEOUT_SECONDS = 60
OPENAI_TIMEOUT_SECONDS = 10
OPENAI_MAX_TOKENS = 80
OPENAI_TEMPERATURE = 0.3
DETALHAMENTO_MAX_CHARACTERS = 180

WORK_DURATION = timedelta(hours=8)
LUNCH_DURATION = timedelta(hours=1)
ENTRY_TIME_START = time(8, 45)
ENTRY_TIME_END = time(9, 15)
LUNCH_START_RANGE_BEGIN = time(11, 30)
LUNCH_START_RANGE_END = time(14, 0)

HOLIDAY_COUNTRY_CODE = "BR"
EXPECTED_INTERVALS_PER_DAY = 2
TIME_FORMAT = "%H:%M"
DATE_FORMAT_BR = "%d/%m/%Y"
MONTH_YEAR_FORMAT = "%m/%Y"

LOGIN_PATH = "/Login"
LOGOUT_PATH = "/Login/Logout"
CREATE_PATH = "/Lancamento/Create"

SELECTOR_LOGIN = "#Login"
SELECTOR_PASSWORD = "#Senha"
SELECTOR_SUBMIT_LOGIN = "button[type='submit']"
SELECTOR_MONTH_YEAR = "#MesAnoId"
SELECTOR_CLIENT = "#ClienteId"
SELECTOR_PROJECT = "#ProjetoId"
SELECTOR_PROJECT_ROLE = "#ProjetoFuncaoId"
SELECTOR_ACTIVITY_TYPE = "#TipoAtividadeId"
SELECTOR_DAY = "#Dia"
SELECTOR_START_TIME = "#HoraInicio"
SELECTOR_END_TIME = "#HoraTermino"
SELECTOR_DETAILS = "#Detalhamento"
SELECTOR_SAVE = "#novolancamentoform button[type='submit']"
SELECTOR_MONTH_ENTRIES = "#divLancamentoNoMes"
SAVE_NAVIGATION_TIMEOUT_MS = 30_000
MORNING_INTERVAL_START_LIMIT = time(12, 0)

GENERIC_DETALHAMENTO_WITHOUT_REPO = (
    "Trabalhei no desenvolvimento e manutenção do projeto em andamento."
)
GENERIC_DETALHAMENTO_WITH_REPO = "Trabalhei no desenvolvimento do projeto."
DETALHAMENTO_GIT_FALLBACK_PREFIX = "Trabalhei nisto: "
DETALHAMENTO_TAG_TEMPLATE = "[{tag}] "
FOLDER_PICKER_TITLE = "Selecione o repositório em que você está trabalhando"
USELESS_COMMIT_PATTERNS = (
    r"^merge\b",
    r"^wip\b",
    r"^atualização:\s*commit via copilot",
)

NESTED_GIT_SKIP_DIRECTORY_NAMES = frozenset(
    {
        "node_modules",
        "vendor",
        ".venv",
        "venv",
        "dist",
        "build",
        "__pycache__",
        ".git",
        "tmp",
        "storage",
    }
)
NESTED_GIT_MAX_DEPTH = 4

STATE_FILE_NAME = "state.json"
STATE_KEY_LAST_REPO_PATH = "last_repo_path"
STATE_KEY_SELECTED_AT = "selected_at"
