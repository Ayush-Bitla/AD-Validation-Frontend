from __future__ import annotations

import pandas as pd


def _normalize_id(value: object) -> str:
    return str(value).strip().lower() if value is not None and not pd.isna(value) else ''


def check_in_azure(onprem: pd.DataFrame, azure: pd.DataFrame) -> list[dict[str, str]]:
    if onprem.empty:
        return []

    onprem_unique = onprem[['samaccountname']].drop_duplicates(subset=['samaccountname'], keep='first').copy()
    azure_unique = azure[['samaccountname']].drop_duplicates(subset=['samaccountname'], keep='first').copy()

    azure_ids = set(_normalize_id(value) for value in azure_unique['samaccountname'])
    failed: list[dict[str, str]] = []

    for _, row in onprem_unique.iterrows():
        account = str(row['samaccountname']).strip() or 'N/A'
        if _normalize_id(account) not in azure_ids:
            failed.append({'account': account, 'status': 'FAIL', 'reason': 'Not found in Azure.'})

    return failed
