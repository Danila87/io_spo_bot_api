import json

import aiohttp
from aiohttp import ClientResponse

from typing import Optional, Dict, Union

from aiohttp.http import HTTPStatus

from common_lib.logger import logger


class ApiClientBase:
    def __init__(
            self,
            token
    ):
        self._token = token


    def get_headers_base(
            self
    ) -> Dict:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f'Bearer {self._token}'
        }

        return headers

    async def _parse_response(
            self,
            response: ClientResponse
    ) -> Union[str, bytes, Dict]:

        if response.content_type == "application/xml":
            return await response.content.read()
        elif response.content_type == "application/json":
            return await response.json()
        elif response.content_type.startswith("application/"):
            return await response.content.read()
        elif response.content_type == 'image/png':
            return await response.content.read()
        else:
            return await response.text()

    # TODO нужна более понятная проработка Exception по примеру той, которой делал на работе
    async def call_async_post(
            self,
            url: str,
            body: Union[Dict, bytes],
            params: Optional[Dict] = None,
            headers: Optional[Dict] = None
    ):
        if headers is None:
            headers = self.get_headers_base()
        data = json.dumps(body) if isinstance(body, Dict) else body
        try:
            async with aiohttp.ClientSession() as session:

                async with session.post(
                    url=url,
                    headers=headers,
                    params=params,
                    data=data
                ) as response:

                    if response.status == HTTPStatus.INTERNAL_SERVER_ERROR or response.status == HTTPStatus.UNAUTHORIZED:
                        raise Exception(await response.text())

                    return await self._parse_response(response)

        except Exception as e:
            logger.error(f'Произошла ошибка при выполнении операции POST по пути {response.url}.\nПараметры: {response.headers}.\nТекст ошибки {await response.text()}')
            raise Exception(
                f'Произошла ошибка при выполнении операции POST'
            )

    async def call_async_delete(
            self,
            url: str,
            body: Union[Dict, bytes],
            params: Optional[Dict] = None,
            headers: Optional[Dict] = None
    ):
        if headers is None:
            headers = self.get_headers_base()

        try:
            async with aiohttp.ClientSession() as session:

                async with session.post(
                        url=url,
                        headers=headers,
                        params=params,
                        body=body
                ) as response:
                    if response == HTTPStatus.INTERNAL_SERVER_ERROR:
                        raise Exception(await response.text())

                    return self._parse_response(response)


        except Exception:
            logger.error(
                f'Произошла ошибка при выполнении операции DELETE по пути {response.url}.\nПараметры: {response.headers}.\nТекст ошибки {await response.text()}')
            raise Exception(
                f'Произошла ошибка при выполнении операции DELETE'
            )

    async def call_async_put(
            self,
            url: str,
            body: Union[Dict, bytes],
            params: Optional[Dict] = None,
            headers: Optional[Dict] = None
    ):
        if headers is None:
            headers = self.get_headers_base()

        try:
            async with aiohttp.ClientSession() as session:

                async with session.post(
                        url=url,
                        headers=headers,
                        params=params,
                        body=body
                ) as response:
                    if response == HTTPStatus.INTERNAL_SERVER_ERROR:
                        raise Exception(await response.text())

                    return self._parse_response(response)


        except Exception:
            logger.error(
                f'Произошла ошибка при выполнении операции PUT по пути {response.url}.\nПараметры: {response.headers}.\nТекст ошибки {await response.text()}')
            raise Exception(
                f'Произошла ошибка при выполнении операции PUT'
            )

    async def call_async_get(
            self,
            url: str,
            params: Optional[Dict] = None,
            headers: Optional[Dict] = None
    ):
        if headers is None:
            headers = self.get_headers_base()

        try:
            async with aiohttp.ClientSession() as session:

                async with session.get(
                        url=url,
                        headers=headers,
                        params=params,
                ) as response:
                    if response.status == HTTPStatus.INTERNAL_SERVER_ERROR or response.status == HTTPStatus.UNAUTHORIZED:
                        raise Exception(await response.text())

                    return await self._parse_response(response)

        except Exception as e:
            logger.error(
                f'Произошла ошибка при выполнении операции GET по пути {url}.\nПараметры: {params}.\nТекст ошибки {e}')