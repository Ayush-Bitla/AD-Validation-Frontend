from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Union

import pandas as pd


def _normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(column).strip().lower() for column in frame.columns]
    return frame


def _clean_string_values(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.copy()
    for column in cleaned.columns:
        if cleaned[column].dtype == object:
            cleaned[column] = cleaned[column].map(
                lambda value: str(value).strip() if value is not None and not pd.isna(value) else ''
            )
    return cleaned


def read_uploaded_file(file_source: Union[str, Path, bytes, BinaryIO], sheet_name: str | None = None) -> pd.DataFrame:
    if isinstance(file_source, (str, Path)):
        path = Path(file_source)
        suffix = path.suffix.lower()
        if suffix == '.csv':
            frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        elif suffix in {'.xlsx', '.xls'}:
            frame = pd.read_excel(path, sheet_name=sheet_name, dtype=str, engine='openpyxl')
        else:
            raise ValueError(f'Unsupported file type: {suffix}')
    else:
        raw_bytes = file_source.read() if hasattr(file_source, 'read') else file_source
        if not raw_bytes:
            raise ValueError('Empty file.')
        buffer = BytesIO(raw_bytes)
        if isinstance(raw_bytes, bytes) and raw_bytes.startswith(b'PK'):
            frame = pd.read_excel(buffer, sheet_name=sheet_name, dtype=str, engine='openpyxl')
        else:
            frame = pd.read_csv(buffer, dtype=str, keep_default_na=False)

    frame = _normalize_columns(frame)
    frame = _clean_string_values(frame)
    return frame
