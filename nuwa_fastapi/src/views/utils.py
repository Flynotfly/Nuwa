from fastapi import HTTPException


def raise_non_found_error(model_name: str, instance_id: int):
    raise HTTPException(
        status_code=404,
        detail=f"{model_name} with id {instance_id} is not found",
    )
