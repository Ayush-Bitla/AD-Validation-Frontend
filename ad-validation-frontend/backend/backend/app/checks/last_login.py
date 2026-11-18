from __future__ import annotations

from datetime import datetime

import pandas as pd

from app.settings import LAST_LOGIN_MAX_DAYS


def _days_since(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    parsed = pd.to_datetime(text, errors='coerce')
    if pd.isna(parsed):
        return None
    return int((datetime.utcnow().date() - parsed.date()).days)


def check_last_login(frame: pd.DataFrame) -> list[dict[str, str]]:
    if frame.empty:
        return []

    unique = frame[['samaccountname', 'lastlogondate']].drop_duplicates(subset=['samaccountname'], keep='first').copy()
    failed: list[dict[str, str]] = []

    for _, row in unique.iterrows():
        account = str(row['samaccountname']).strip() or 'N/A'
        days = _days_since(row.get('lastlogondate'))
        if days is None:
            failed.append({
                'account': account,
                'status': 'N/A',
                'reason': 'Last login date is missing or unreadable.',
            })
            continue
        if days > LAST_LOGIN_MAX_DAYS:
            failed.append({
                'account': account,
                'status': 'FAIL',
                'reason': f'Last login was {days} days ago.',
            })

    return failed
