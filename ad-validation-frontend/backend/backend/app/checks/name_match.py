from __future__ import annotations

import pandas as pd


def _normalize_name(value: object) -> str:
    if value is None or pd.isna(value):
        return ''
    return str(value).strip().lower()


def check_name_match(onprem: pd.DataFrame, azure: pd.DataFrame) -> list[dict[str, str]]:
    if onprem.empty or azure.empty:
        return []

    onprem_unique = onprem[['samaccountname', 'name']].drop_duplicates(subset=['samaccountname'], keep='first').copy()
    azure_unique = azure[['samaccountname', 'name']].drop_duplicates(subset=['samaccountname'], keep='first').copy()

    merged = onprem_unique.merge(
        azure_unique.rename(columns={'name': 'azure_name'}),
        on='samaccountname',
        how='inner',
    )

    if merged.empty:
        return []

    onprem_names = merged['name'].map(_normalize_name)
    azure_names = merged['azure_name'].map(_normalize_name)
    mismatches = merged[onprem_names.ne(azure_names)]

    failed: list[dict[str, str]] = []
    for _, row in mismatches.iterrows():
        account = str(row['samaccountname']).strip() or 'N/A'
        onprem_name = str(row['name']).strip() or 'N/A'
        azure_name = str(row['azure_name']).strip() or 'N/A'
        failed.append({
            'account': account,
            'status': 'FAIL',
            'reason': f"On-Prem name '{onprem_name}' is different from Azure name '{azure_name}'.",
        })

    return failed
