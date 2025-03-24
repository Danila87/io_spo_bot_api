import urllib.parse

from fastapi import APIRouter, UploadFile, File, HTTPException

from starlette.responses import JSONResponse, Response

from schemas.service import RequestCreate, AdditionalPath
from schemas import pyggy_bank as pb_schemes

from database import models
from database.cruds import CRUDManagerSQL, LegendCruds, KTDCruds, GameCruds

from typing import Annotated, List, Optional

from common_lib.file_storage.file_manager import file_manager
from common_lib.logger import logger

piggy_bank_router = APIRouter(prefix='/piggy_bank', tags=['piggy_bank'])

@piggy_bank_router.get('/groups', tags=['piggy_bank'])
async def get_groups() -> List[pb_schemes.PiggyBankGroupResponse]:

    data = await CRUDManagerSQL.get_data(
        model=models.PiggyBankGroups,
    )

    return [
        pb_schemes.PiggyBankGroupResponse(**row.to_dict()) for row in data
    ] if data else []


@piggy_bank_router.post('/groups', tags=['piggy_bank'])
async def create_group(
        group: pb_schemes.PiggyBankGroupCreate
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.PiggyBankGroups,
        row_filter={
            'title': group.title
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данная группа уже есть в БД'
        )

    if await CRUDManagerSQL.insert_data(
            model=models.PiggyBankGroups,
            body=dict(group)
    ):

        return JSONResponse(
            status_code=201,
            content={'message': 'Группа успешно добавлена'}
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании'
    )


@piggy_bank_router.get('/types_game', tags=['piggy_bank'])
async def get_types_game() -> List[pb_schemes.PiggyBankTypeGameResponse]:

    data = await CRUDManagerSQL.get_data(
        model=models.PiggyBankTypesGame,
    )

    return [
        pb_schemes.PiggyBankTypeGameResponse(**row.to_dict()) for row in data
    ]


@piggy_bank_router.post('/types_game', tags=['piggy_bank'])
async def create_type_game(
        type_game: pb_schemes.PiggyBankTypeGameCreate
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.PiggyBankTypesGame,
        row_filter={
            'title': type_game.title
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данный тип игры уже существует в БД'
        )

    if await CRUDManagerSQL.insert_data(
            model=models.PiggyBankTypesGame,
            body=dict(type_game)
    ):

        return JSONResponse(
            status_code=201,
            content={'message': 'Тип игр успешно добавлен'}
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании'
    )


@piggy_bank_router.get('/games/', tags=['piggy_bank'])
async def get_game(
        game_id: int,
        user_id: Optional[int] = None
) -> pb_schemes.PiggyBankGameResponse:

    if not (data := await CRUDManagerSQL.get_data(
            model=models.PiggyBankGames,
            row_id=game_id
        )
    ):
        raise HTTPException(
            status_code=404,
            detail='Игра под указанным id не найдена'
        )

    await CRUDManagerSQL.insert_request(
        request_type_title='Игра',
        body=RequestCreate(
            id_content=data[0].id,
            id_user=user_id,
            content_display_value=data[0].title
        )
    )

    return pb_schemes.PiggyBankGameResponse(
        **data[0].to_dict()
    )



@piggy_bank_router.get('/games/file/', tags=['piggy_bank'])
async def get_game_with_file(
        game_id: int
) -> Response:

    if not (game := await CRUDManagerSQL.get_data(
        model=models.PiggyBankGames,
        row_id=game_id
    )):
        raise HTTPException(
            status_code=404,
            detail='Игра под указанным id не найдена'
        )

    if not (filepath := game[0].file_path):
        raise HTTPException(
            status_code=404,
            detail=f'Не найден связанный файл по пути {game[0].file_path}'
        )

    file = await file_manager.get_file(filepath)

    headers_data = {
        'file_type': file.suffix,
        'filename': urllib.parse.quote(file.filename.encode('utf-8'))
    }

    return Response(
        content=file.file_data,
        media_type=file.content_type,
        headers=headers_data
    )


@piggy_bank_router.get('/games/by_type_group/', tags=['piggy_bank'])
async def get_games_by_type_group(
        type_id: int,
        group_id: int
) -> List[pb_schemes.PiggyBankGameResponse]:

    data = await GameCruds.get_game_by_group_type(
        group_id=group_id,
        type_id=type_id
    )
    return [
        pb_schemes.PiggyBankGameResponse(**row.to_dict()) for row in data
    ]


@piggy_bank_router.post('/games/', tags=['piggy_bank'])
async def insert_game(
        game_data: pb_schemes.PiggyBankGameCreate
) -> JSONResponse:

    intersection_group_type_ids = await GameCruds.check_available_game(
        title=game_data.title,
        type_ids=game_data.type_id,
        group_ids=game_data.group_id
    )

    if intersection_group_type_ids.group_ids and intersection_group_type_ids.type_ids:
        raise HTTPException(
            status_code=500,
            detail='Игра с таким названием уже существует в БД и имеет те же типы и группы, что были переданы.'
        )

    if row_id := await GameCruds.insert_game_transaction(game=game_data):
        return JSONResponse(
            status_code=201,
            content={'message': 'Тип игра добавлена!', 'row_id': row_id}
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании'
    )

@piggy_bank_router.put('/games/{game_id}/load_file', tags=['piggy_bank'])
async def load_game_file(
        game_id: int,
        file: Annotated[UploadFile, File()]
):

    if not await file_manager.save_file(
        file=file,
        additional_path=AdditionalPath.GAMES_PATH
    ):
        raise HTTPException(
            status_code=500,
            detail='Возникла ошибка при сохранении файла'
        )

    if not await CRUDManagerSQL.update_data(
            model=models.PiggyBankGames,
            row_id=game_id,
            body={
                'file_path': f'{AdditionalPath.GAMES_PATH.value}/{file.filename}',
            }
    ):
        raise HTTPException(
            status_code=500,
            detail={'message': 'Ошибка сохранения'}
        )

    return JSONResponse(
        status_code=201,
        content={'message': 'Запись сохранена'}
    )

@piggy_bank_router.get('/legends', tags=['piggy_bank'])
async def get_all_legends() -> List[pb_schemes.PiggyBankBaseStructureResponse]:

    data = await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
    )

    return [
        pb_schemes.PiggyBankBaseStructureResponse(**row.to_dict()) for row in data
    ]


@piggy_bank_router.post('/legends', tags=['piggy_bank'])
async def create_legend(
        legend: pb_schemes.PiggyBankBaseStructureCreate
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
        row_filter={
            'title': legend.title
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данная легенда уже существует в БД'
        )

    if new_id := await LegendCruds.insert_legend_transaction(
            data=legend
    ):
        return JSONResponse(
            status_code=201,
            content={
                'message': 'Легенда добавлена!',
                'row_id': new_id
            }
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании легенды'
    )

@piggy_bank_router.put('/legends/{legend_id}/load_file', tags=['piggy_bank'])
async def load_legend_file(
        legend_id: int,
        file: Annotated[UploadFile, File()]
):
    if not await file_manager.save_file(
        file=file,
        additional_path=AdditionalPath.LEGENDS_PATH
    ):
        raise HTTPException(
            status_code=500,
            detail='Возникла ошибка при сохранении файла',
        )

    if not await CRUDManagerSQL.update_data(
            model=models.PiggyBankLegends,
            row_id=legend_id,
            body={
                'file_path': f'{AdditionalPath.LEGENDS_PATH.value}/{file.filename}',
            }
    ):
        raise HTTPException(
            status_code=500,
            detail={'message': 'Ошибка сохранения'}
        )

    return JSONResponse(
        status_code=201,
        content={'message': 'Запись сохранена'}
    )

@piggy_bank_router.get('/legend/by_group/')
async def get_legends_by_group(
        group_id: int
) -> List[pb_schemes.PiggyBankBaseStructureResponse]:

    data = await LegendCruds.get_legends_by_group(
        group_id=group_id
    )
    return [pb_schemes.PiggyBankBaseStructureResponse(**row.to_dict()) for row in data]


@piggy_bank_router.get('/legends/file/')
async def get_legend_by_id_file(
        legend_id: int
) -> Response:

    if not (legend := await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
        row_id=legend_id,
    )):
        raise HTTPException(
            status_code=500,
            detail=f'Не найдена легенда под id {legend_id}'
        )

    if not (filepath := legend[0].file_path):
        raise HTTPException(
            status_code=404,
            detail=f'Не найден связанный файл по пути {filepath}'
        )

    file = await file_manager.get_file(filepath)

    headers_data = {
        'file_type': file.suffix,
        'filename': urllib.parse.quote(file.filename.encode('utf-8'))
    }

    return Response(
        content=file.file_data,
        media_type=file.content_type,
        headers=headers_data
    )


@piggy_bank_router.get('/legends/')
async def get_legend_by_id(
        legend_id: int,
        user_id: Optional[int] = None
) -> pb_schemes.PiggyBankBaseStructureResponse:

    if not (data := await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
        row_id=legend_id
    )):
        raise HTTPException(
            status_code=404,
            detail='Легенда под указанным id не найдена'
        )

    await CRUDManagerSQL.insert_request(
        request_type_title='Легенда',
        body=RequestCreate(
            id_content=data[0].id,
            id_user=user_id,
            content_display_value=data[0].title
        )
    )

    return pb_schemes.PiggyBankBaseStructureResponse(**data[0].to_dict())


@piggy_bank_router.get('/ktd', tags=['piggy_bank'])
async def get_all_ktd() -> List[pb_schemes.PiggyBankBaseStructureResponse]:
    data = await CRUDManagerSQL.get_data(
        model=models.PiggyBankKTD,
    )

    return [
        pb_schemes.PiggyBankBaseStructureResponse(**row.to_dict()) for row in data
    ]


@piggy_bank_router.post('/ktd', tags=['piggy_bank'])
async def create_ktd(
    ktd: pb_schemes.PiggyBankBaseStructureCreate
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.PiggyBankKTD,
        row_filter={
            'title': ktd.title,
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данное КТД уже существует в БД'
        )

    if new_row_id := await KTDCruds.insert_ktd_transaction(
            data=ktd
    ):
        return JSONResponse(
            status_code=201,
            content={
                'message': 'КТД добавлено!',
                'row_id': new_row_id
            }
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании КТД'
    )

@piggy_bank_router.put('/ktd/{ktd_id}/load_file', tags=['piggy_bank'])
async def load_ktd_file(
        ktd_id: int,
        file: Annotated[UploadFile, File()]
):
    if not await file_manager.save_file(
            file=file,
            additional_path=AdditionalPath.KTD_PATH
    ):
        raise HTTPException(
            status_code=500,
            detail='Возникла ошибка при сохранении файла'
        )

    if not await CRUDManagerSQL.update_data(
            model=models.PiggyBankKTD,
            row_id=ktd_id,
            body={
                'file_path': f'{AdditionalPath.KTD_PATH.value}/{file.filename}',
            }
    ):
        raise HTTPException(
            status_code=500,
            detail={'message': 'Ошибка сохранения'}
        )

    return JSONResponse(
        status_code=201,
        content={'message': 'Запись сохранена'}
    )

@piggy_bank_router.get('/ktd/by_group/')
async def get_ktd_by_group(
        group_id: int
) -> List[pb_schemes.PiggyBankBaseStructureResponse]:
    data = await KTDCruds.get_ktd_by_group(
        group_id=group_id
    )

    return [
        pb_schemes.PiggyBankBaseStructureResponse(**row.to_dict()) for row in data
    ]

@piggy_bank_router.get('/ktd/file/')
async def get_legend_by_id_file(
        ktd_id: int
) -> Response:

    if not (ktd := await CRUDManagerSQL.get_data(
        model=models.PiggyBankKTD,
        row_id=ktd_id
    )):
        raise HTTPException(
            status_code=404,
            detail='Не найдено КТД под указанным id'
        )

    if not (filepath := ktd[0].file_path):
        raise HTTPException(
            status_code=404,
            detail=f'Не найден файл по пути {filepath}'
        )

    file = await file_manager.get_file(filepath)

    headers_data = {
        'file_type': file.suffix,
        'filename': urllib.parse.quote(file.filename.encode('utf-8'))
    }

    return Response(
        content=file.file_data,
        media_type=file.content_type,
        headers=headers_data
    )


@piggy_bank_router.get('/ktd/')
async def get_ktd_by_id(
        ktd_id: int,
        user_id: Optional[int] = None
) -> pb_schemes.PiggyBankBaseStructureResponse:

    if not (data := await CRUDManagerSQL.get_data(
        model=models.PiggyBankKTD,
        row_id=ktd_id
    )):
        raise HTTPException(
            status_code=404,
            detail='КТД под указанным id не найдено'
        )

    await CRUDManagerSQL.insert_request(
        request_type_title='КТД',
        body=RequestCreate(
            id_content=data[0].id,
            id_user=user_id,
            content_display_value=data[0].title
        )
    )

    return pb_schemes.PiggyBankBaseStructureResponse(**data[0].to_dict())
