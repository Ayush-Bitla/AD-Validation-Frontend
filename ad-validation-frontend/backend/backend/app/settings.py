from __future__ import annotations

COLUMNS = {
    "onprem": {
        "id": "samaccountname",
        "name": "name",
        "enabled": "enabled",
        "last_login": "lastlogondate",
        "dc": "logonserver",
    },
    "azure": {
        "id": "samaccountname",
        "name": "name",
    },
    "accounts": {
        "id": "samaccountname",
        "type": "type",
    },
}

EXPECTED_DCS = [
    "DC01",
    "DC02",
    "DC03",
    "DC04",
    "DC05",
    "DC06",
    "DC07",
    "DC08",
    "DC09",
    "DC10",
    "DC11",
]

LIMITS = {"vendor": 15, "employee": 30}
LAST_LOGIN_MAX_DAYS = 30
MAX_UPLOAD_MB = 50
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
