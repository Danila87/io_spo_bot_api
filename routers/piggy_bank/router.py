from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse

from pydantic_schemes.PyggyBank import schemes as pb_schemes

from database import models
from database.cruds import CRUDManagerSQL, PiggyBankCruds

from typing import Annotated, List

from misc import file_work

piggy_bank_router = APIRouter(prefix='/piggy_bank', tags=['piggy_bank'])


@piggy_bank_router.get('/groups', tags=['piggy_bank'])
async def get_groups() -> list[pb_schemes.PiggyBankGroupResponse]:

    return await CRUDManagerSQL.get_data(
        model=models.PiggyBankGroups,
    )


@piggy_bank_router.post('/groups', tags=['piggy_bank'])
async def create_group(
        group: pb_schemes.PiggyBankGroup
) -> JSONResponse:

    if await CRUDManagerSQL.insert_data(
            model=models.PiggyBankGroups,
            body=dict(group)
    ):

        return JSONResponse(
            status_code=201,
            content={'message': 'Группа успешно добавлена'}
        )

    return JSONResponse(
        status_code=500,
        content={'message': 'Произошла ошибка при создании'}
    )


@piggy_bank_router.get('/types_game', tags=['piggy_bank'])
async def get_types_game() -> list[pb_schemes.PiggyBankTypeGameResponse]:

    return await CRUDManagerSQL.get_data(
        model=models.PiggyBankTypesGame,
    )


@piggy_bank_router.post('/types_game', tags=['piggy_bank'])
async def create_type_game(
        type_game: pb_schemes.PiggyBankTypeGame
) -> JSONResponse:

    if await CRUDManagerSQL.insert_data(
            model=models.PiggyBankTypesGame,
            body=dict(type_game)
    ):

        return JSONResponse(
            status_code=201,
            content={'message': 'Тип игр успешно добавлен'}
        )

    return JSONResponse(
        status_code=500,
        content={'message': 'Произошла ошибка при создании'}
    )


@piggy_bank_router.get('/games/{game_id}', tags=['piggy_bank'])
async def get_game(
        game_id: int
) -> pb_schemes.PiggyBankGameResponse:

    return await CRUDManagerSQL.get_data(
        model=models.PiggyBankGames,
        row_id=game_id
    )


@piggy_bank_router.get('/games/{game_id}/file', tags=['piggy_bank'])
async def get_game_with_file(
        game_id: int
) -> FileResponse:

    game = await CRUDManagerSQL.get_data(
        model=models.PiggyBankGames,
        row_id=game_id
    )

    file = game.file_path

    headers_data = {
        'file_type': '.pdf'
    }

    return FileResponse(path=file, filename='avc.pdf', headers=headers_data)


@piggy_bank_router.get('/games/', tags=['piggy_bank'])
async def get_games_by_type_group(
        type_id: int,
        group_id: int
) -> List[pb_schemes.PiggyBankGameResponse]:

    return await PiggyBankCruds.get_game_by_group_type(
        group_id=group_id,
        type_id=type_id
    )


@piggy_bank_router.post('/games/', tags=['piggy_bank'])
async def insert_game(
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
        group_id: Annotated[int, Form()],
        type_id: Annotated[int, Form()]
) -> JSONResponse:
    try:
        file_path = file_work.save_file('database/files_data/piggy_bank_data',
                                        file=file)

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={'message': str(error)}
        )

    game = pb_schemes.PiggyBankGameCreate.model_validate({
        'title': title,
        'description': description,
        'file_path': file_path,
        'group_id': group_id,
        'type_id': type_id
    })

    if await PiggyBankCruds.insert_game_transaction(game=game):
        return JSONResponse(
            status_code=201,
            content={'message': 'Тип игра добавлена!'}
        )

    return JSONResponse(
        status_code=500,
        content={'message': 'Произошла ошибка при создании'}
    )


@piggy_bank_router.get('/legends', tags=['piggy_bank'])
async def get_all_legends() -> list[pb_schemes.PiggyBankBaseStructureResponse]:

    return await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
    )


@piggy_bank_router.post('/legends', tags=['piggy_bank'])
async def create_legend(
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
        group_id: Annotated[int, Form()]
) -> JSONResponse:
    try:
        file_path = file_work.save_file('database/files_data/piggy_bank_data',
                                        file=file)

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={'message': str(error)}
        )

    data = pb_schemes.PiggyBankBaseStructureCreate.model_validate({
        'title': title,
        'description': description,
        'file_path': file_path,
        'group_id': group_id
    })

    if await PiggyBankCruds.insert_ktd_or_legend_transaction(
            item_model=models.PiggyBankLegends,
            item_type='legend',
            data=data
    ):
        return JSONResponse(
            status_code=201,
            content={'message': 'Легенда добавлена!'}
        )

    return JSONResponse(
        status_code=500,
        content={'message': 'Произошла ошибка при создании легенды'}
    )


@piggy_bank_router.get('/legend/by_group/{group_id}')
async def get_legend_by_group(group_id: int):

    return await PiggyBankCruds.get_legends_or_krd_by_group(
        item_model=models.PiggyBankLegends,
        mtm_model=models.PiggyBankGroupsForLegend,
        group_id=group_id
    )


@piggy_bank_router.get('/legends/{legend_id}/file')
async def get_legend_by_id_file(
        legend_id: int
) -> FileResponse:

    legend = await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
        row_id=legend_id,
    )

    file = legend.file_path

    headers_data = {
        'file_type': '.pdf'
    }

    return FileResponse(
        path=file,
        filename='avc.pdf',
        headers=headers_data
    )


@piggy_bank_router.get('/legends/{legend_id}')
async def get_legend_by_id(
        legend_id: int
) -> pb_schemes.PiggyBankBaseStructureResponse:

    return await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
        row_id=legend_id
    )


@piggy_bank_router.get('/ktd', tags=['piggy_bank'])
async def get_all_ktd() -> list[pb_schemes.PiggyBankBaseStructureResponse]:

    return await CRUDManagerSQL.get_data(
        model=models.PiggyBankKTD,
    )


@piggy_bank_router.post('/ktd', tags=['piggy_bank'])
async def create_ktd(
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
        group_id: Annotated[int, Form()]
) -> JSONResponse:
    try:
        file_path = file_work.save_file('database/files_data/piggy_bank_data',
                                        file=file)

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={'message': str(error)}
        )

    data = pb_schemes.PiggyBankBaseStructureCreate.model_validate({
        'title': title,
        'description': description,
        'file_path': file_path,
        'group_id': group_id
    })

    if await PiggyBankCruds.insert_ktd_or_legend_transaction(
            item_model=models.PiggyBankKTD,
            item_type='ktd',
            data=data
    ):
        return JSONResponse(
            status_code=201,
            content={'message': 'КТД добавлено!'}
        )

    return JSONResponse(
        status_code=500,
        content={'message': 'Произошла ошибка при создании КТД'}
    )


@piggy_bank_router.get('/ktd/by_group/{group_id}')
async def get_ktd_by_group(
        group_id: int
) -> list[pb_schemes.PiggyBankBaseStructureResponse]:

    return await PiggyBankCruds.get_legends_or_krd_by_group(
        item_model=models.PiggyBankKTD,
        mtm_model=models.PiggyBankGroupsForKTD,
        group_id=group_id
    )


@piggy_bank_router.get('/ktd/{ktd_id}/file')
async def get_legend_by_id_file(
        ktd_id: int
) -> FileResponse:

    ktd = await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
        row_id=ktd_id
    )

    file = ktd.file_path

    headers_data = {
        'file_type': '.pdf'
    }

    return FileResponse(
        path=file,
        filename='avc.pdf',
        headers=headers_data
    )


@piggy_bank_router.get('/ktd/{ktd_id}')
async def get_legend_by_id(
        ktd_id: int
) -> pb_schemes.PiggyBankBaseStructureResponse:

    return await CRUDManagerSQL.get_data(
        model=models.PiggyBankKTD,
        row_id=ktd_id
    )
