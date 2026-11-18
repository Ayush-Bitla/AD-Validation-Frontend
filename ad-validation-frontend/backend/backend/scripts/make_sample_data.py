from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.settings import EXPECTED_DCS, LIMITS


OUTPUT_DIR = Path(__file__).resolve().parent.parent / 'sample_data'


def build_onprem_rows() -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    count = 160
    missing_dc_accounts = {10, 20, 30}
    repeated_dc_accounts = {11, 21, 31}
    unknown_dc_accounts = {12, 22, 32}

    for index in range(count):
        account_id = f'user{index:04d}'
        first_name = f'User{index % 10}'
        last_name = 'Sample'
        base_name = f'{first_name} {last_name}'

        for dc in EXPECTED_DCS:
            if index in missing_dc_accounts and dc == 'DC07':
                continue
            if index in repeated_dc_accounts and dc == 'DC11':
                continue
            if index in unknown_dc_accounts and dc == 'DC10':
                dc = 'DC99'

            login_days = 12 if index % 12 == 0 else 20 if index % 10 == 0 else 40 if index % 9 == 0 else 60
            if index % 17 == 0:
                last_login = ''
            else:
                last_login = (pd.Timestamp.today() - pd.Timedelta(days=login_days)).strftime('%Y-%m-%d')

            rows.append({
                'samaccountname': account_id,
                'name': base_name,
                'enabled': 'True',
                'lastlogondate': last_login,
                'logonserver': dc,
            })

        if index in repeated_dc_accounts:
            rows.append({
                'samaccountname': account_id,
                'name': base_name,
                'enabled': 'True',
                'lastlogondate': (pd.Timestamp.today() - pd.Timedelta(days=32)).strftime('%Y-%m-%d'),
                'logonserver': 'DC01',
            })

    return pd.DataFrame(rows)


def build_azure_rows(onprem_df: pd.DataFrame) -> pd.DataFrame:
    azure_rows: list[dict[str, str]] = []
    account_ids = sorted(onprem_df['samaccountname'].drop_duplicates().tolist())
    for position, account_id in enumerate(account_ids):
        if position % 13 == 0:
            continue
        name = f'User{position % 10} Sample'
        if position % 9 == 0:
            name = f'Changed Name {position}'
        azure_rows.append({'samaccountname': account_id, 'name': name})

    return pd.DataFrame(azure_rows)


def build_account_rows(onprem_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    with_type = sorted(onprem_df['samaccountname'].drop_duplicates().tolist())
    for position, account_id in enumerate(with_type):
        account_type = 'vendor' if position % 3 == 0 else 'employee'
        if position % 19 == 0:
            account_type = ''
        rows.append({'samaccountname': account_id, 'type': account_type})
    return pd.DataFrame(rows)


def print_summary(onprem_df: pd.DataFrame, azure_df: pd.DataFrame, accounts_df: pd.DataFrame) -> None:
    checks = {
        'dc_failures': 0,
        'name_mismatch': 0,
        'should_disable': 0,
        'login_30_days': 0,
        'azure_missing': 0,
    }

    checks['dc_failures'] = len({account for account in onprem_df['samaccountname'].unique() if onprem_df[onprem_df['samaccountname'] == account].shape[0] != 11})
    azure_lookup = set(azure_df['samaccountname'].str.strip().str.lower())
    checks['azure_missing'] = sum(1 for account in onprem_df['samaccountname'].drop_duplicates() if str(account).strip().lower() not in azure_lookup)
    checks['name_mismatch'] = 0
    merged = onprem_df[['samaccountname', 'name']].drop_duplicates().merge(
        azure_df[['samaccountname', 'name']].rename(columns={'name': 'azure_name'}), on='samaccountname', how='inner'
    )
    checks['name_mismatch'] = int(
        (merged['name'].astype(str).str.strip().str.lower() != merged['azure_name'].astype(str).str.strip().str.lower()).sum()
    )

    # simple counts for the demo summary table
    summary = pd.DataFrame([
        {'check': 'DC failures', 'count': checks['dc_failures']},
        {'check': 'Name mismatch', 'count': checks['name_mismatch']},
        {'check': 'Should disable', 'count': checks['should_disable']},
        {'check': 'Login 30+ days', 'count': checks['login_30_days']},
        {'check': 'Missing in Azure', 'count': checks['azure_missing']},
    ])
    print(summary.to_string(index=False))


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    onprem_df = build_onprem_rows()
    azure_df = build_azure_rows(onprem_df)
    accounts_df = build_account_rows(onprem_df)

    onprem_df.to_csv(OUTPUT_DIR / 'onprem.csv', index=False)
    azure_df.to_csv(OUTPUT_DIR / 'azure.csv', index=False)
    accounts_df.to_csv(OUTPUT_DIR / 'accounts.csv', index=False)

    print(f'Created sample data in {OUTPUT_DIR}')
    print_summary(onprem_df, azure_df, accounts_df)


if __name__ == '__main__':
    main()
