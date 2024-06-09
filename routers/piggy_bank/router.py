from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import FileResponse

from pydantic_schemes import schemes

from database import models
from database.cruds import BaseCruds, PiggyBankCruds

from typing import Annotated, Union

from misc.verify_data import verify_data
from misc import file_work

piggy_bank_router = APIRouter(prefix='/piggy_bank', tags=['piggy_bank'])


@piggy_bank_router.get('/groups', tags=['piggy_bank'])
async def get_groups():
    return await BaseCruds.get_all_data(model=models.PiggyBankGroups)


@piggy_bank_router.post('/groups', tags=['piggy_bank'])
async def create_group(data: schemes.PiggyBankGroup):
    await verify_data(
        schema=data,
        model=models.PiggyBankGroups,
        error_msg='Такая группа уже существует',
        title=data.title
    )

    if await BaseCruds.insert_data(model=models.PiggyBankGroups, **dict(data)):
        return HTTPException(status_code=201, detail='Группа успешно добавлена')

    return HTTPException(status_code=500, detail='Произошла ошибка при создании')


@piggy_bank_router.get('/types_game', tags=['piggy_bank'])
async def get_types_game():
    return await BaseCruds.get_all_data(model=models.PiggyBankTypesGame)


@piggy_bank_router.post('/types_game', tags=['piggy_bank'])
async def create_type_game(data: schemes.PiggyBankTypeGame):
    await verify_data(
        schema=data,
        model=models.PiggyBankTypesGame,
        error_msg='Такой тип уже существует',
        title=data.title
    )

    if await BaseCruds.insert_data(model=models.PiggyBankTypesGame, **dict(data)):
        return HTTPException(status_code=201, detail='Тип игр успешно добавлен')

    return HTTPException(status_code=500, detail='Произошла ошибка при создании')


@piggy_bank_router.get('/games/{game_id}', tags=['piggy_bank'])
async def get_game(game_id: int):
    return await BaseCruds.get_data_by_id(model=models.PiggyBankGames, model_id=game_id)


@piggy_bank_router.get('/games/{game_id}/file', tags=['piggy_bank'])
async def get_game_with_file(game_id: int):
    game = await BaseCruds.get_data_by_id(model=models.PiggyBankGames, model_id=game_id)

    file = game['file_path']

    headers_data = {
        'file_type': '.pdf'
    }

    return FileResponse(path=file, filename='avc.pdf', headers=headers_data)


@piggy_bank_router.get('/games/', tags=['piggy_bank'])
async def get_games_by_type_group(type_id: int, group_id: int):
    return await PiggyBankCruds.get_game_by_group_type(group_id=group_id, type_id=type_id)


@piggy_bank_router.post('/games/', tags=['piggy_bank'])
async def insert_game(
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
        group_id: Annotated[int, Form()],
        type_id: Annotated[int, Form()]
):
    try:
        file_path = file_work.save_file('database/files_data/piggy_bank_data', file=file)

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    data = schemes.PiggyBankGame.model_validate({
        'title': title,
        'description': description,
        'file_path': file_path,
        'group_id': group_id,
        'type_id': type_id
    })

    await verify_data(
        schema=data,
        model=models.PiggyBankGames,
        error_msg='Такая игра уже существует',
        title=data.title
    )

    if await PiggyBankCruds.insert_game_transaction(data=data):
        return HTTPException(status_code=201, detail='Тип игра добавлена!')

    return HTTPException(status_code=500, detail='Произошла ошибка при создании')


@piggy_bank_router.get('/legends', tags=['piggy_bank'])
async def get_all_legends() -> list[dict]:
    return await BaseCruds.get_all_data(model=models.PiggyBankLegends)


@piggy_bank_router.post('/legends', tags=['piggy_bank'])
async def create_legend(
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
        group_id: Annotated[int, Form()]
):
    try:
        file_path = file_work.save_file('database/files_data/piggy_bank_data', file=file)

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    data = schemes.PiggyBankBaseStructure.model_validate({
        'title': title,
        'description': description,
        'file_path': file_path,
        'group_id': group_id
    })

    await verify_data(
        schema=data,
        model=models.PiggyBankLegends,
        error_msg='Такая легенда уже существует',
        title=data.title
    )

    if await PiggyBankCruds.insert_ktd_or_legend_transaction(
            item_model=models.PiggyBankLegends,
            item_type='legend',
            data=data
    ):
        return HTTPException(status_code=201, detail='Легенда добавлена!')

    return HTTPException(status_code=500, detail='Произошла ошибка при создании легенды')


@piggy_bank_router.get('/legend/by_group/{group_id}')
async def get_legend_by_group(group_id: int):

    return await PiggyBankCruds.get_legends_or_krd_by_group(
        item_model=models.PiggyBankLegends,
        mtm_model=models.PiggyBankGroupsForLegend,
        group_id=group_id
    )


@piggy_bank_router.get('/legends/{legend_id}/file')
async def get_legend_by_id_file(legend_id: int):

    legend = await BaseCruds.get_data_by_id(model=models.PiggyBankLegends, model_id=legend_id)

    file = legend['file_path']

    headers_data = {
        'file_type': '.pdf'
    }

    return FileResponse(path=file, filename='avc.pdf', headers=headers_data)


@piggy_bank_router.get('/legends/{legend_id}')
async def get_legend_by_id(legend_id: int):

    return await BaseCruds.get_data_by_id(model=models.PiggyBankLegends, model_id=legend_id)


@piggy_bank_router.get('/ktd', tags=['piggy_bank'])
async def get_all_legends() -> list[dict]:
    return await BaseCruds.get_all_data(model=models.PiggyBankKTD)


@piggy_bank_router.post('/ktd', tags=['piggy_bank'])
async def create_ktd(
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
        group_id: Annotated[int, Form()]
):
    try:
        file_path = file_work.save_file('database/files_data/piggy_bank_data', file=file)

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    data = schemes.PiggyBankBaseStructure.model_validate({
        'title': title,
        'description': description,
        'file_path': file_path,
        'group_id': group_id
    })

    await verify_data(
        schema=data,
        model=models.PiggyBankKTD,
        error_msg='Такое КТД уже существует',
        title=data.title
    )

    if await PiggyBankCruds.insert_ktd_or_legend_transaction(
            item_model=models.PiggyBankKTD,
            item_type='ktd',
            data=data
    ):
        return HTTPException(status_code=201, detail='КТД добавлено!')

    return HTTPException(status_code=500, detail='Произошла ошибка при создании КТД')


@piggy_bank_router.get('/ktd/by_group/{group_id}')
async def get_ktd_by_group(group_id: int):

    return await PiggyBankCruds.get_legends_or_krd_by_group(
        item_model=models.PiggyBankKTD,
        mtm_model=models.PiggyBankGroupsForKTD,
        group_id=group_id
    )


@piggy_bank_router.get('/ktd/{ktd_id}/file')
async def get_legend_by_id_file(ktd_id: int):
    ktd = await BaseCruds.get_data_by_id(model=models.PiggyBankLegends, model_id=ktd_id)

    file = ktd['file_path']

    headers_data = {
        'file_type': '.pdf'
    }

    return FileResponse(path=file, filename='avc.pdf', headers=headers_data)


@piggy_bank_router.get('/ktd/{ktd_id}')
async def get_legend_by_id(ktd_id: int):
    return await BaseCruds.get_data_by_id(model=models.PiggyBankKTD, model_id=ktd_id)
