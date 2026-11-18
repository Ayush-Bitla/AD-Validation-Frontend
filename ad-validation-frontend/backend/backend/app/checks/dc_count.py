from __future__ import annotations

import pandas as pd

from app.settings import EXPECTED_DCS


def check_dc_count(frame: pd.DataFrame) -> list[dict[str, str]]:
    if frame.empty:
        return []

    working = frame.copy()
    working['dc_normalized'] = working['logonserver'].fillna('').astype(str).str.strip().str.upper()
    account_groups = (
        working.groupby('samaccountname', dropna=False)
        .agg(
            record_count=('logonserver', 'size'),
            unique_dcs=('dc_normalized', lambda values: sorted(set(values.astype(str)))),
            seen_dcs=('dc_normalized', lambda values: list(values.astype(str))),
        )
        .reset_index()
    )

    failed: list[dict[str, str]] = []
    for _, row in account_groups.iterrows():
        account = str(row['samaccountname']).strip() or 'N/A'
        seen = set(str(value).upper() for value in row['seen_dcs'])
        unique_set = set(row['unique_dcs'])
        missing = [dc for dc in EXPECTED_DCS if dc not in seen]
        repeated = 'yes' if row['record_count'] != len(unique_set) else 'no'
        unknown = sorted(value for value in seen if value not in EXPECTED_DCS)

        if row['record_count'] != 11 or missing or repeated == 'yes' or unknown:
            reason = (
                f"{row['record_count']} records. Missing DCs: {', '.join(missing) if missing else 'none'}. "
                f"Repeated DC: {repeated}. Unknown DC: {', '.join(unknown) if unknown else 'none'}."
            )
            failed.append({'account': account, 'status': 'FAIL', 'reason': reason})

    return failed
