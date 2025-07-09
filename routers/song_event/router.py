from fastapi import APIRouter, Query, Body

from database.models import SongEvents
from schemas import song_event as se_schemas
from schemas.responses import ResponseData, Meta, ResponseCreate, ResponseDelete
from database.cruds import SongEventCruds, CRUDManagerSQL

from typing import List, Annotated, Dict

song_event_router = APIRouter(prefix='/song-events', tags=['song_events'])


@song_event_router.get(
    path='/',
    response_model=ResponseData[se_schemas.SongEventResponse],
    summary="Получить музыкальные события",
)
async def get_song_events(
    row_ids: Annotated[List[int], Query(
        description="Список id событий"
    )] = None,
    is_actual: Annotated[bool, Query(
        description="Вернуть только актуальные события"
    )] = False
):

    data = await SongEventCruds.get_song_event(
        row_id=row_ids,
        is_actual=is_actual
    )
    song_events = []
    for song_event in data:
        song_ids = [song.id for song in song_event.rel_songs]

        song_event = song_event.to_dict()
        song_event['song_ids'] = song_ids
        song_events.append(song_event)

    return ResponseData(
        data=song_events,
        meta=Meta(total=len(song_events))
    )


@song_event_router.post(
    path='/',
    response_model=ResponseCreate[se_schemas.SongEventCreateResponse],
    summary="Создать музыкальное событие"
)
async def create_song_event(
    song_event: Annotated[se_schemas.SongEventCreateWithSong, Body(
        description="Данные для создания события"
    )]
):
    data = await SongEventCruds.insert_song_event(
        song_event=song_event
    )

    return ResponseCreate(
        data=data,
    )

@song_event_router.delete(
    path='/',
    response_model=ResponseDelete,
    summary="Удалить музыкальное событие"
)
async def delete_song_event(
    row_id: Annotated[int, Query(
        description="Id события"
    )]
):

    is_delete = await CRUDManagerSQL.delete_data(
        model=SongEvents,
        row_id=row_id
    )

    return ResponseDelete(
        message='Запись успешно удалена.' if is_delete else 'Возникла ошибка при удалении записи.'
    )