import urllib
from typing import List, Annotated, Optional

from fastapi import APIRouter
from fastapi.params import Query

from io import BytesIO
from common_lib.api_clients.grafana_client import grafana_client
from fastapi.responses import FileResponse, Response

from schemas.dashboard import Dashboard, Visualization
from schemas.responses import ResponseData, Meta

statistic_router = APIRouter(prefix='/statistic', tags=['statistic'])


@statistic_router.get(
    path='/dashboards/',
    response_model=ResponseData[Dashboard]
)
async def get_all_dashboard(
    tag: Annotated[Optional[str], Query(
        description="Список тегов"
    )] = None
):
    dashboards = await grafana_client.get_dashboards()

    if tag:
        dashboards = [dashboard for dashboard in dashboards if tag in dashboard.tags]

    return ResponseData(
        data=dashboards,
        meta=Meta(total=len(dashboards))
    )


@statistic_router.get(
    path='/dashboards/visualisations/',
    response_model=ResponseData[Visualization]
)
async def get_visualisations_by_dashboard(
        dashboard_uid: Annotated[str, Query(
            description="UID дашборда"
        )]
):
    visualisations =  await grafana_client.get_visualizations(
        dashboard_uid=dashboard_uid
    )
    return ResponseData(
        data=visualisations,
        meta=Meta(total=len(visualisations))
    )


@statistic_router.get(
    path='/dashboards/visualisations/img/',
)
async def get_visualisation_img(
        dashboard_uid: Annotated[str, Query(
            description="UID дашборда"
        )],
        panel_id: Annotated[int, Query(
            description="ID панели"
        )],
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

@statistic_router.get(
    path='/dashboards/img/',
)
async def get_dashboard_img(
        dashboard_uid: Annotated[str, Query(
            description="UID дашборда"
        )]
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