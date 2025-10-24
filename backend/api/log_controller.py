from fastapi import APIRouter, Depends
from backend.api.log_service import LogService
import json

router = APIRouter(prefix="/logs", tags=["Logs"])

# Dependency Injection
def get_log_service():
    return LogService()

@router.get("/level/counts")
def get_log_counts(service: LogService = Depends(get_log_service)):
    """
    API to fetch log counts by category for the last 24 hours.
    """
    return service.get_log_counts_for_each_4h()

def get_model_json(model):
    with open('model_info.json', 'r') as file:
        data = json.load(file)
        return data[model]


@router.get("model1/info")
def get_model_info(model):
    return get_model_json("model-1")

@router.get("model2/info")
def get_model_info(model):
    return get_model_json("model-2")