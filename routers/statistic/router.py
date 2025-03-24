import urllib
from typing import List

from fastapi import APIRouter
from io import BytesIO
from common_lib.api_clients.grafana_client import grafana_client
from fastapi.responses import FileResponse, Response

from schemas.dashboard import Dashboard, Visualization

statistic_router = APIRouter(prefix='/statistic', tags=['piggy_bank'])


@statistic_router.get(
    path='/dashboards',
    tags=['statistic'],
    response_model=List[Dashboard]
)
async def get_all_dashboard():
    return await grafana_client.get_dashboards()


@statistic_router.get(
    path='/dashboards/bot',
    tags=['statistic'],
    response_model=List[Dashboard]
)
async def get_bot_dashboard():
    all_dashboards = await grafana_client.get_dashboards()
    return [dashboard for dashboard in all_dashboards if 'bot_view' in dashboard.tags]


@statistic_router.get(
    path='/dashboards/{dashboard_uid}/visualisations',
    tags=['statistic'],
    response_model=List[Visualization]
)
async def get_visualisations_by_dashboard(
        dashboard_uid: str
):
    return await grafana_client.get_visualizations(
        dashboard_uid=dashboard_uid
    )


@statistic_router.get(
    path='/dashboards/{dashboard_uid}/visualisations/{panel_id}/img',
    tags=['statistic']
)
async def get_visualisation_img(
        dashboard_uid: str,
        panel_id: int
):
    file_bytes = await grafana_client.get_visualizations_to_img(
        dashboard_uid=dashboard_uid,
        panel_id=panel_id
    )

    filename = f'{file_bytes["visualisation"].title}.png'
    filename = urllib.parse.quote(filename.encode('utf-8'))

    return Response(
        content=file_bytes['img_data'],
        media_type="image/png",
        headers={
            'file_type': '.png',
            'filename': filename
        }
    )
    # return Response(
    #     content=file_bytes,
    #     media_type="image/png",
    #     headers={
    #         "Content-Disposition": "attachment; filename=image.png"
    #     }
    # )

@statistic_router.get(
    path='/dashboards/{dashboard_uid}/img',
    tags=['statistic'],
)
async def get_dashboard_img(
        dashboard_uid: str
):
    data = await grafana_client.get_dashboard_to_img(
        dashboard_uid=dashboard_uid,
    )
    filename = f'{data["dashboard"].title}.png'
    filename = urllib.parse.quote(filename.encode('utf-8'))

    return Response(
        content=data['img_data'],
        media_type="image/png",
        headers={
            'file_type': '.png',
            'filename': filename
        }
    )