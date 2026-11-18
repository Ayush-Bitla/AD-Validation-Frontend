import sys
from pathlib import Path

import pandas as pd

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.checks.name_match import check_name_match
from app.reader import read_uploaded_file


def test_reader_reads_csv_and_normalizes_columns(tmp_path):
    csv_path = tmp_path / 'sample.csv'
    pd.DataFrame([
        {'SamAccountName': ' Alice ', 'Name': ' Alice Smith ', 'Enabled': 'True', 'LastLogonDate': '2024-01-02'}
    ]).to_csv(csv_path, index=False)

    df = read_uploaded_file(csv_path)

    assert not df.empty
    assert list(df.columns) == ['samaccountname', 'name', 'enabled', 'lastlogondate']
    assert df.iloc[0]['samaccountname'] == 'Alice'
    assert df.iloc[0]['name'] == 'Alice Smith'


def test_name_match_detects_mismatched_accounts():
    onprem = pd.DataFrame([
        {'samaccountname': 'user001', 'name': 'Alice Smith'},
        {'samaccountname': 'user002', 'name': 'Bob Jones'},
    ])
    azure = pd.DataFrame([
        {'samaccountname': 'user001', 'name': 'Alice Smith'},
        {'samaccountname': 'user002', 'name': 'Robert Jones'},
    ])

    result = check_name_match(onprem, azure)

    assert len(result) == 1
    assert result[0]['account'] == 'user002'
    assert result[0]['status'] == 'FAIL'
    assert 'different from Azure name' in result[0]['reason']
