from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Query

from ..schemas.api import DatasetPage
from ..services.dataset_service import DATASET_NAMES, get_dataset


router = APIRouter(prefix="/data", tags=["data"])


@router.get("/{dataset_name}", response_model=DatasetPage)
def read_dataset(
    dataset_name: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> DatasetPage:
    if dataset_name not in DATASET_NAMES:
        raise HTTPException(status_code=404, detail=f"Unknown dataset '{dataset_name}'.")

    frame = get_dataset()[dataset_name]
    items = json.loads(frame.iloc[offset : offset + limit].to_json(orient="records", date_format="iso"))
    return DatasetPage(
        dataset=dataset_name,
        total=len(frame),
        limit=limit,
        offset=offset,
        items=items,
    )