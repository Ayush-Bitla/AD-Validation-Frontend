from __future__ import annotations

from datetime import datetime

import pandas as pd

from app.settings import LIMITS


def _to_bool(value: object) -> bool:
    if value is None or pd.isna(value):
        return False
    return str(value).strip().lower() in {'1', 'true', 'yes', 'y'}


def _days_since(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = pd.to_datetime(text, errors='coerce')
        if pd.isna(parsed):
            return None
        return int((datetime.utcnow().date() - parsed.date()).days)
    except Exception:
        return None


def check_inactive(onprem: pd.DataFrame, accounts: pd.DataFrame) -> list[dict[str, str]]:
    if onprem.empty:
        return []

    unique_onprem = onprem[['samaccountname', 'enabled', 'lastlogondate']].drop_duplicates(subset=['samaccountname'], keep='first').copy()
    unique_accounts = accounts[['samaccountname', 'type']].drop_duplicates(subset=['samaccountname'], keep='first').copy()

    merged = unique_onprem.merge(unique_accounts, on='samaccountname', how='left')
    if merged.empty:
        return []

    failed: list[dict[str, str]] = []
    for _, row in merged.iterrows():
        account = str(row['samaccountname']).strip() or 'N/A'
        enabled = _to_bool(row.get('enabled'))
        if not enabled:
            continue

        account_type = str(row.get('type', '')).strip().lower() if row.get('type') is not None else ''
        if account_type not in LIMITS:
            failed.append({
                'account': account,
                'status': 'N/A',
                'reason': 'Type is missing or unknown.',
            })
            continue

        days = _days_since(row.get('lastlogondate'))
        if days is None:
            failed.append({
                'account': account,
                'status': 'N/A',
                'reason': 'Last login date is missing or unreadable.',
            })
            continue

        limit = LIMITS[account_type]
        if days > limit:
            failed.append({
                'account': account,
                'status': 'SHOULD DISABLE',
                'reason': f"{account_type} unused for {days} days. Limit is {limit}.",
            })

    return failed
