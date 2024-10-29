from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from starlette.responses import JSONResponse

from pydantic_schemes.PyggyBank import schemes as pb_schemes

from database import models
from database.cruds import CRUDManagerSQL, LegendCruds, KTDCruds, GameCruds

from typing import Annotated, List
from pathlib import Path
from misc import file_work

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
        group: pb_schemes.PiggyBankGroup
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
        type_game: pb_schemes.PiggyBankTypeGame
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
        game_id: int
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

    return pb_schemes.PiggyBankGameResponse(
        **data[0].to_dict()
    )



@piggy_bank_router.get('/games/{game_id}/file', tags=['piggy_bank'])
async def get_game_with_file(
        game_id: int
) -> FileResponse:

    if not (game := await CRUDManagerSQL.get_data(
        model=models.PiggyBankGames,
        row_id=game_id
    )):
        raise HTTPException(
            status_code=404,
            detail='Игра под указанным id не найдена'
        )

    if (filepath := game[0].file_path) is None:
        raise HTTPException(
            status_code=404,
            detail=f'Не найден связанный файл по пути {game[0].file_path}'
        )

    file = Path(filepath)

    headers_data = {
        'file_type': file.suffix
    }

    return FileResponse(
        path=file.resolve(),
        filename=file.name,
        headers=headers_data
    )


@piggy_bank_router.get('/games/', tags=['piggy_bank'])
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
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
        group_id: Annotated[int, Form()],
        type_id: Annotated[int, Form()]
) -> JSONResponse:

    # TODO нужна более продуманная реализация проверки на наличие в БД учитывая мени то мени связь

    if not (file_path := file_work.save_file(
        'database/files_data/piggy_bank_data',
        file=file
    )):
        raise HTTPException(
            status_code=500,
            detail='Возникла ошибка при создании файла'
        )

    game = pb_schemes.PiggyBankGameCreate.model_validate({
        'title': title,
        'description': description,
        'file_path': file_path,
        'group_id': group_id,
        'type_id': type_id
    })

    if await GameCruds.insert_game_transaction(game=game):
        return JSONResponse(
            status_code=201,
            content={'message': 'Тип игра добавлена!'}
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании'
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
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
        group_id: Annotated[int, Form()]
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
        row_filter={
            'title': title
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данная легенда уже существует в БД'
        )

    if not (file_path := file_work.save_file(
        'database/files_data/piggy_bank_data',
        file=file
    )):
        raise HTTPException(
            status_code=500,
            detail='Произошла ошибка при сохранении файла'
        )

    data = pb_schemes.PiggyBankBaseStructureCreate.model_validate({
        'title': title,
        'description': description,
        'file_path': file_path,
        'group_id': group_id
    })

    if await LegendCruds.insert_legend_transaction(
            data=data
    ):
        return JSONResponse(
            status_code=201,
            content={'message': 'Легенда добавлена!'}
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании легенды'
    )


@piggy_bank_router.get('/legend/by_group/')
async def get_legends_by_group(
        group_id: int
) -> List[pb_schemes.PiggyBankBaseStructureResponse]:

    data = await LegendCruds.get_legends_by_group(
        group_id=group_id
    )
    return [pb_schemes.PiggyBankBaseStructureResponse(**row.to_dict()) for row in data]


@piggy_bank_router.get('/legends/{legend_id}/file')
async def get_legend_by_id_file(
        legend_id: int
) -> FileResponse:

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
    file = Path(filepath)

    headers_data = {
        'file_type': file.suffix
    }

    return FileResponse(
        path=file.resolve(),
        filename=file.name,
        headers=headers_data
    )


@piggy_bank_router.get('/legends/')
async def get_legend_by_id(
        legend_id: int
) -> pb_schemes.PiggyBankBaseStructureResponse:

    if not (data := await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
        row_id=legend_id
    )):
        raise HTTPException(
            status_code=404,
            detail='Легенда под указанным id не найдена'
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
        title: Annotated[str, Form()],
        description: Annotated[str, Form()],
        file: Annotated[UploadFile, File()],
        group_id: Annotated[int, Form()]
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.PiggyBankKTD,
        row_filter={
            'title': title
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данное КТД уже существует в БД'
        )

    if not (file_path := file_work.save_file(
            'database/files_data/piggy_bank_data',
            file=file
    )):

        raise HTTPException(
            status_code=500,
            detail='Произошла ошибка при сохранении файла.'
        )

    data = pb_schemes.PiggyBankBaseStructureCreate.model_validate({
        'title': title,
        'description': description,
        'file_path': file_path,
        'group_id': group_id
    })

    if await KTDCruds.insert_ktd_transaction(
            data=data
    ):
        return JSONResponse(
            status_code=201,
            content={'message': 'КТД добавлено!'}
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка при создании КТД'
    )


@piggy_bank_router.get('/ktd/by_group/{group_id}')
async def get_ktd_by_group(
        group_id: int
) -> List[pb_schemes.PiggyBankBaseStructureResponse]:
    data = await KTDCruds.get_ktd_by_group(
        group_id=group_id
    )

    return [
        pb_schemes.PiggyBankBaseStructureResponse(**row.to_dict()) for row in data
    ]

@piggy_bank_router.get('/ktd/{ktd_id}/file')
async def get_legend_by_id_file(
        ktd_id: int
) -> FileResponse:

    if not (ktd := await CRUDManagerSQL.get_data(
        model=models.PiggyBankLegends,
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

    file = Path(filepath)

    headers_data = {
        'file_type': file.suffix
    }

    return FileResponse(
        path=file.resolve(),
        filename=file.name,
        headers=headers_data
    )


@piggy_bank_router.get('/ktd/')
async def get_ktd_by_id(
        legend_id: int
) -> pb_schemes.PiggyBankBaseStructureResponse:

    if not (data := await CRUDManagerSQL.get_data(
        model=models.PiggyBankKTD,
        row_id=legend_id
    )):
        raise HTTPException(
            status_code=404,
            detail='КТД под указанным id не найдено'
        )

    return pb_schemes.PiggyBankBaseStructureResponse(**data[0].to_dict())
