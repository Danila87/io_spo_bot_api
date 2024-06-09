from fastapi import HTTPException

from pydantic import BaseModel

from database.cruds import BaseCruds

from functools import wraps


async def verify_data(schema: BaseModel,
                      model,
                      error_msg: str,
                      **filter_params
                      ) -> BaseModel:
    if await BaseCruds.get_data_by_filter(model=model, verify=True, **filter_params):
        raise HTTPException(status_code=400, detail=error_msg)

    return schema


'''
Идея прикольная
def verify_data_dec(schema: BaseModel,
                    model,
                    error_msg: str,
                    **filter_params):
    def wrapper(func):
        print(func)

        @wraps(func)
        async def verify_data_dec(data):
            print(data)
            await verify_data(schema=data.schema, model=data.model, error_msg=data.error_msg, title=data.title)
            return await func(data)

        return verify_data_dec

    return wrapper'''
