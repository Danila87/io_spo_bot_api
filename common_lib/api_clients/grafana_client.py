import asyncio
from typing import List, Optional

from .api_client import ApiClientBase
from .url_factory import grafana_url_f
from config import GRAFANA_TOKEN
from schemas.dashboard import Dashboard, Visualization
from .enums import RenderType

class GrafanaClient(ApiClientBase):
    def __init__(
            self,
            bearer_token: str
    ):
        super().__init__(token=bearer_token)


    async def get_dashboards(
            self,
    ) -> List[Dashboard]:
        data = await self.call_async_get(
            url=grafana_url_f.all_dashboards
        )
        dashboards = [Dashboard(**dashboard) for dashboard in data if dashboard['type'] == 'dash-db']

        return dashboards

    async def get_dashboard(
            self,
            dashboard_uid: str
    ) -> Dashboard:
        data = await self.call_async_get(
            url=grafana_url_f.all_vizualizations_by_dashboard(
                dashboard_uid=dashboard_uid
            )
        )

        return Dashboard(
            id = data['dashboard']['id'],
            uid = data['dashboard']['uid'],
            title = data['dashboard']['title'],
            tags = data['dashboard']['tags']
            )


    async def get_visualizations(
            self,
            dashboard_uid: str
    ) -> List[Visualization]:
        data = await self.call_async_get(
            url=grafana_url_f.all_vizualizations_by_dashboard(
                dashboard_uid=dashboard_uid
            )
        )

        visualizations = [
            Visualization(
                id = visualisation['id'],
                title = visualisation['title'],
                dashboard_uid = visualisation['datasource']['uid']
            )
            for visualisation in data['dashboard']['panels']
        ]

        return visualizations

    async def get_visualisation_by_id(
            self,
            dashboard_uid: str,
            visualisation_id: int
    ) -> Visualization:

        visualisations = await self.get_visualizations(dashboard_uid)
        visualisation = next(v for v in visualisations if v.id == visualisation_id)

        return visualisation


    async def get_dashboard_to_img(
            self,
            dashboard_uid: str
    ):

        params = {
            'theme': 'dark',
            'kiosk': ''
        }

        data = await self.call_async_get(
            url=grafana_url_f.render_img(
                dashboard_uid=dashboard_uid,
                render_type=RenderType.D
            ),
            params=params
        )

        dashboard_data = await self.get_dashboard(
            dashboard_uid=dashboard_uid
        )

        return {
            'img_data': data,
            'dashboard': dashboard_data
        }

    async def get_visualizations_to_img(
            self,
            dashboard_uid: str,
            panel_id: int,
            **panel_params
    ):
        params = {
            'panelId': f'panel-{panel_id}',
            **panel_params
        }

        data = await self.call_async_get(
            url=grafana_url_f.render_img(
                dashboard_uid=dashboard_uid,
                render_type=RenderType.D_SOLO
            ),
            params=params
        )

        visualisation = await self.get_visualisation_by_id(
            dashboard_uid=dashboard_uid,
            visualisation_id=panel_id
        )

        return {
            'img_data': data,
            'visualisation': visualisation
        }

grafana_client = GrafanaClient(
    bearer_token=GRAFANA_TOKEN
)

async def main():
    data = await grafana_client.get_visualizations_to_img(
        dashboard_uid='ce82dsm22s7pcf',
        panel_id=4
    )
    pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
