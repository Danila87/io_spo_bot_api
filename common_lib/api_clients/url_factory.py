from config import GRAFANA_PORT, GRAFANA_HOST
from .enums import Protocols, RenderType

class UrlFactoryBase:
    def __init__(
            self,
            host:str,
            port: int,
            protocol: Protocols
    ):
        self._host = host
        self._port = port
        self._protocol = protocol

    @property
    def base_url(self):
        return f'{self._protocol}://{self._host}:{self._port}'

    @property
    def api(self):
        return f'{self.base_url}/api'


class GrafanaUrlFactory(UrlFactoryBase):
    def __init__(
            self,
            host: str,
            port: int,
            protocol: Protocols
    ):
        super().__init__(
            host=host,
            port=port,
            protocol=protocol.value
        )

    @property
    def dashboards_resource(self):
        return f'{self.api}/dashboards'

    @property
    def render_resource(self):
        return f'{self.base_url}/render'

    @property
    def all_dashboards(self):
        return f'{self.api}/search'


    def all_vizualizations_by_dashboard(
            self,
            dashboard_uid: str
    ):
        return f'{self.dashboards_resource}/uid/{dashboard_uid}'

    def render_img(
            self,
            dashboard_uid: str,
            render_type: RenderType
    ):
        return f'{self.render_resource}/{render_type}/{dashboard_uid}/'

grafana_url_f = GrafanaUrlFactory(
    host=GRAFANA_HOST,
    port=GRAFANA_PORT,
    protocol=Protocols.HTTP
)