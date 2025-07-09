import urllib.parse

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.params import Query, Body

from starlette.responses import JSONResponse, Response

from schemas.service import RequestCreate, AdditionalPath
from schemas.responses import ResponseData, Meta, ResponseDelete, ResponseCreate
from schemas import pyggy_bank as pb_schemes

from database import models
from database.cruds import CRUDManagerSQL, LegendCruds, KTDCruds, GameCruds

from typing import Annotated, List, Optional

from common_lib.file_storage.file_manager import file_manager

PIGGY_BANK_GROUP_TAG = 'piggy_bank_group'
PIGGY_BANK_KTD_TAG = 'piggy_bank_ktd'
PIGGY_BANK_LEGEND_TAG = 'piggy_bank_legend'
PIGGY_BANK_GAME_TAG = 'piggy_bank_game'
PIGGY_BANK_TYPE_GAME_TAG = 'piggy_bank_type_game'

piggy_bank_router = APIRouter(prefix='/piggy_bank', tags=['piggy_bank_methods'])

@piggy_bank_router.get(
    path='/groups/',
    tags=[PIGGY_BANK_GROUP_TAG],
    response_model=ResponseData[pb_schemes.PiggyBankGroupResponse],
    summary='Получить группы детей'
)
async def get_groups(
    group_ids: Annotated[List[int], Query(
        description="Список id групп"
    )] = None
):

    groups = await CRUDManagerSQL.get_data(
        model=models.PiggyBankGroups,
        row_id=group_ids
    )

    return ResponseData(
        data=groups,
        meta=Meta(total=len(groups))
    )


@piggy_bank_router.post(
    path='/groups/',
    tags=[PIGGY_BANK_GROUP_TAG],
    summary='Добавить группу детей'
)
async def create_group(
        group: Annotated[pb_schemes.PiggyBankGroupCreate, Body()]
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


@piggy_bank_router.get(
    path='/types_game/',
    tags=[PIGGY_BANK_TYPE_GAME_TAG],
    response_model=ResponseData[pb_schemes.PiggyBankTypeGameResponse],
    summary='Получить типы игр'
)
async def get_types_game(
    type_game_ids: Annotated[List[int], Query(
        description="Список id типов игр"
    )] = None
):

    types_game = await CRUDManagerSQL.get_data(
        model=models.PiggyBankTypesGame,
        row_id=type_game_ids
    )

    return ResponseData(
        data=types_game,
        meta=Meta(total=len(types_game))
    )


@piggy_bank_router.post(
    path='/types_game/',
    tags=[PIGGY_BANK_TYPE_GAME_TAG],
    summary='Добавить тип игры'
)
async def create_type_game(
        type_game: Annotated[pb_schemes.PiggyBankTypeGameCreate, Body()]
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


@piggy_bank_router.get(
    path='/games/',
    tags=[PIGGY_BANK_GAME_TAG],
    response_model=ResponseData[pb_schemes.PiggyBankGameResponse],
    summary='Получить игры'
)
async def get_games(
        game_ids: Annotated[int, Query(
            description="Id игр"
        )] = None,
        user_id: Annotated[Optional[int], Query(
            description="Id пользователя telegram"
        )] = None
):
    songs = await CRUDManagerSQL.get_data(
            model=models.PiggyBankGames,
            row_id=game_ids
    )

    # await CRUDManagerSQL.insert_request(
    #     request_type_title='Игра',
    #     body=RequestCreate(
    #         id_content=data[0].id,
    #         id_user=user_id,
    #         content_display_value=data[0].title
    #     )
    # )

    return ResponseData(
        data=songs,
        meta=Meta(total=len(songs))
    )


@piggy_bank_router.get(
    path='/games/by_type_group/',
    tags=[PIGGY_BANK_GAME_TAG],
    response_model=ResponseData[pb_schemes.PiggyBankGameResponse],
    summary='Получить игры по типу игры и группе детей'
)
async def get_games_by_type_group(
        type_id: Annotated[int, Query(
        description="Id типа игры"
        )],
        group_id: Annotated[int, Query(
            description="Id группы детей"
        )]
):

    games = await GameCruds.get_game_by_group_type(
        group_id=group_id,
        type_id=type_id
    )
    return ResponseData(
        data=games,
        meta=Meta(total=len(games))
    )


@piggy_bank_router.post(
    path='/games/',
    tags=[PIGGY_BANK_GAME_TAG],
    response_model=ResponseCreate[pb_schemes.PiggyBankGameResponse],
    summary='Добавить игру'
)
async def insert_game(
        game_data: Annotated[pb_schemes.PiggyBankGameCreate, Body(
            description="Тело игры"
        )]
):

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

    if new_song_data := await GameCruds.insert_game_transaction(
        game=game_data
    ):
        return ResponseCreate(
            data=new_song_data
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании'
    )


@piggy_bank_router.put(
    path='/games/file/',
    tags=[PIGGY_BANK_GAME_TAG],
    summary='Добавить/Обновить файл к игре'
)
async def load_game_file(
        game_id: Annotated[int, Query(
        description="Id игры"
        )],
        file: Annotated[UploadFile, File(
            description="Файл для игры"
        )]
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


@piggy_bank_router.get(
    path='/games/file/',
    tags=[PIGGY_BANK_GAME_TAG],
    summary='Получить файл игры'
)
async def get_game_file(
        game_id: Annotated[int, Query(
            description="Id игры"
        )]
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


@piggy_bank_router.get(
    path='/legends/',
    tags=[PIGGY_BANK_LEGEND_TAG],
    response_model=ResponseData[pb_schemes.PiggyBankBaseStructureResponse],
    summary='Получить легенды'
)
async def get_legends(
    legend_ids: Annotated[List[int], Query(
        description="Список id легенд"
    )] = None,
    user_id: Annotated[Optional[int], Query(
        description="Id пользователя telegram"
    )] = None
):
    legends = await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
        row_id=legend_ids,
    )

    # await CRUDManagerSQL.insert_request(
    #     request_type_title='Легенда',
    #     body=RequestCreate(
    #         id_content=data[0].id,
    #         id_user=user_id,
    #         content_display_value=data[0].title
    #     )
    # )

    return ResponseData(
        data=legends,
        meta=Meta(total=len(legends))
    )


@piggy_bank_router.get(
    path='/legends/by_group/',
    tags=[PIGGY_BANK_LEGEND_TAG],
    response_model=ResponseData[pb_schemes.PiggyBankBaseStructureResponse],
    summary='Получить легенды по группе детей'
)
async def get_legends_by_group(
    group_id: Annotated[int, Query(
        description="Id группы детей"
    )]
):
    legends = await LegendCruds.get_legends_by_group(
        group_id=group_id
    )

    return ResponseData(
        data=legends,
        meta=Meta(total=len(legends))
    )

@piggy_bank_router.post(
    path='/legends/',
    tags=[PIGGY_BANK_LEGEND_TAG],
    response_model=ResponseCreate[pb_schemes.PiggyBankBaseStructureResponse],
    summary='Создать легенду'
)
async def create_legend(
        legend: Annotated[pb_schemes.PiggyBankBaseStructureCreate, Body(
            description="Тело легенды"
        )]
):

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

    if new_legend_data := await LegendCruds.insert_legend_transaction(
            data=legend
    ):
        return ResponseCreate(
            data=new_legend_data
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании легенды'
    )


@piggy_bank_router.put(
    path='/legends/file/',
    tags=[PIGGY_BANK_LEGEND_TAG],
    summary='Добавить/Обновить файл легенды'
)
async def load_legend_file(
        legend_id: Annotated[int, Query(
            description="Id легенды"
        )],
        file: Annotated[UploadFile, File(
            description="Файл для легенды"
        )]
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


@piggy_bank_router.get(
    path='/legends/file/',
    tags=[PIGGY_BANK_LEGEND_TAG],
    summary='Получить файл легенды'
)
async def get_legend_file(
        legend_id: Annotated[int, Query(
            description="Id легенды"
        )]
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


@piggy_bank_router.get(
    path='/ktd/',
    tags=[PIGGY_BANK_KTD_TAG],
    response_model=ResponseData[pb_schemes.PiggyBankBaseStructureResponse],
    summary='Получить КТД'
)
async def get_ktd_by_id(
        ktd_ids: Annotated[List[int], Query(
            description="Список id КТД"
        )] = None,
        user_id: Annotated[Optional[int], Query(
            description="Id пользователя telegram"
        )] = None
):

    ktds = await CRUDManagerSQL.get_data(
        model=models.PiggyBankKTD,
        row_id=ktd_ids
    )

    # await CRUDManagerSQL.insert_request(
    #     request_type_title='КТД',
    #     body=RequestCreate(
    #         id_content=data[0].id,
    #         id_user=user_id,
    #         content_display_value=data[0].title
    #     )
    # )

    return ResponseData(
        data=ktds,
        meta=Meta(total=len(ktds))
    )


@piggy_bank_router.post(
    path='/ktd/',
    tags=[PIGGY_BANK_KTD_TAG],
    response_model=ResponseCreate[pb_schemes.PiggyBankBaseStructureResponse],
    summary="Создать КТД"
)
async def create_ktd(
    ktd: Annotated[pb_schemes.PiggyBankBaseStructureCreate, Body(
        description="Данные для создания КТД"
    )]
):

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

    if new_ktd_data := await KTDCruds.insert_ktd_transaction(
            data=ktd
    ):
        return ResponseCreate(
            data=new_ktd_data
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании КТД'
    )


@piggy_bank_router.get(
    path='/ktd/by_group/',
    tags=[PIGGY_BANK_KTD_TAG],
    response_model=ResponseData[pb_schemes.PiggyBankBaseStructureResponse],
    summary='Получить КТД по группе детей'
)
async def get_ktd_by_group(
        group_id: Annotated[int, Query(
            description="Id группы детей"
        )]
):
    ktds = await KTDCruds.get_ktd_by_group(
        group_id=group_id
    )

    return ResponseData(
        data=ktds,
        meta=Meta(total=len(ktds))
    )


@piggy_bank_router.put(
    path='/ktd/file/',
    tags=[PIGGY_BANK_KTD_TAG],
    summary='Загрузить/Обновить файл КТД'
)
async def load_ktd_file(
        ktd_id: Annotated[int, Query(
            description="Id КТД"
        )],
        file: Annotated[UploadFile, File(
            description="Файл для КТД"
        )]
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



@piggy_bank_router.get(
    path='/ktd/file/',
    tags=[PIGGY_BANK_KTD_TAG],
    summary='Получить файл КТД'
)
async def get_ktd_file(
        ktd_id: Annotated[int, Query(
            description="Id КТД"
        )]
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

