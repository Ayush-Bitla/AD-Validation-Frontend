from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.auth import get_current_user
from app.checks.dc_count import check_dc_count
from app.checks.in_azure import check_in_azure
from app.checks.inactive import check_inactive
from app.checks.last_login import check_last_login
from app.checks.name_match import check_name_match
from app.reader import read_uploaded_file
from app.settings import ALLOWED_EXTENSIONS, COLUMNS, MAX_UPLOAD_MB

app = FastAPI(title='AD Validation & Reconciliation Tool API')


def _file_extension_error() -> HTTPException:
    return HTTPException(status_code=400, detail='Only .csv and .xlsx files are allowed.')


def _require_columns(frame: dict[str, Any], label: str, required: set[str]) -> None:
    missing = sorted(column for column in required if column not in frame.columns)
    if missing:
        joined = ', '.join(missing)
        raise HTTPException(status_code=400, detail=f'{label} file is missing required column(s): {joined}.')


def _read_file(upload: UploadFile, label: str, sheet_name: str | None) -> dict[str, Any]:
    filename = upload.filename or ''
    suffix = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if suffix not in {'csv', 'xlsx'}:
        raise _file_extension_error()

    if upload.size is not None and upload.size > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f'{label} file exceeds the {MAX_UPLOAD_MB} MB limit.')

    data = upload.file.read()
    if not data:
        raise HTTPException(status_code=400, detail=f'{label} file is empty.')

    try:
        frame = read_uploaded_file(data, sheet_name=sheet_name)
    except ValueError as exc:
        message = str(exc)
        if 'sheet' in message.lower() or 'excel' in message.lower():
            raise HTTPException(status_code=400, detail=f'Unable to read the Excel sheet for {label}.')
        raise HTTPException(status_code=400, detail=message)
    except Exception:
        raise HTTPException(status_code=400, detail=f'Unable to read the Excel sheet for {label}.')

    return {'frame': frame, 'filename': filename}


@app.get('/api/health')
def health_check() -> dict[str, str]:
    return {'status': 'ok'}


@app.post('/api/validate')
def validate_files(
    onprem: UploadFile = File(...),
    azure: UploadFile = File(...),
    accounts: UploadFile = File(...),
    onprem_sheet: str | None = Form(default=None),
    azure_sheet: str | None = Form(default=None),
    accounts_sheet: str | None = Form(default=None),
    user: dict[str, str] = Depends(get_current_user),
) -> dict[str, Any]:
    _ = user
    try:
        onprem_data = _read_file(onprem, 'On-Prem', onprem_sheet)
        azure_data = _read_file(azure, 'Azure', azure_sheet)
        accounts_data = _read_file(accounts, 'Accounts', accounts_sheet)

        onprem_frame = onprem_data['frame']
        azure_frame = azure_data['frame']
        accounts_frame = accounts_data['frame']

        for label, frame, required in [
            ('On-Prem', onprem_frame, set(COLUMNS['onprem'].values())),
            ('Azure', azure_frame, set(COLUMNS['azure'].values())),
            ('Accounts', accounts_frame, set(COLUMNS['accounts'].values())),
        ]:
            _require_columns(frame, label, required)

        dc_failures = check_dc_count(onprem_frame)
        name_failures = check_name_match(onprem_frame, azure_frame)
        inactive_failures = check_inactive(onprem_frame, accounts_frame)
        last_login_failures = check_last_login(onprem_frame)
        azure_failures = check_in_azure(onprem_frame, azure_frame)

        response = {
            'summary': {
                'totalAccounts': int(onprem_frame['samaccountname'].nunique(dropna=False)) if 'samaccountname' in onprem_frame.columns else 0,
                'dc': len(dc_failures),
                'name': len(name_failures),
                'inactive': len(inactive_failures),
                'lastLogin': len(last_login_failures),
                'azure': len(azure_failures),
            },
            'dc': dc_failures,
            'name': name_failures,
            'inactive': inactive_failures,
            'lastLogin': last_login_failures,
            'azure': azure_failures,
        }
        return response
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail='Validation failed. Please try again.')
