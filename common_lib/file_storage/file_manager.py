from pathlib import Path
from typing import Optional, Union

from fastapi import UploadFile
from config import S3_ACCESS_KEY, S3_SECRET_KEY
from .interface import FileStorageInterface
from .s3_storage import S3Storage
from .local_storage import LocalStorage
from schemas.service import FileResponse, AdditionalPath


class FileStorageManager:
    def __init__(
            self,
            strategy: FileStorageInterface
    ):
        self._strategy = strategy

    def set_strategy(
            self,
            strategy: FileStorageInterface
    ):
        self._strategy = strategy

    async def save_file(
            self,
            additional_path:AdditionalPath,
            file: Union[UploadFile, str]
    ) -> bool:
        return await self._strategy.save_file(
            file=file,
            additional_path=additional_path
        )

    async def get_file(
            self,
            path: str
    ) -> FileResponse:
        path = Path(path)
        return await self._strategy.get_file(path)

    async def delete_file(self, path: str) -> bool:
        return await self._strategy.delete_file(path)


file_manager = FileStorageManager(
    strategy=S3Storage(
        access_key=S3_ACCESS_KEY,
        secret_key=S3_SECRET_KEY,
        bucket_name="s3-io-spo-bot",
        endpoint_url="https://s3.storage.selcloud.ru",
    )
)

# file_manager = FileStorageManager(
#     LocalStorage(
#         'database/files_data/'
#     )
# )

