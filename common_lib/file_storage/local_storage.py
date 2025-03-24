import os
import shutil
import mimetypes

from pathlib import Path

from typing import Union

from fastapi import UploadFile

from schemas.service import AdditionalPath, FileResponse
from .interface import FileStorageInterface
from ..logger import logger


class LocalStorage(FileStorageInterface):
    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    async def save_file(
            self,
            file: Union[UploadFile, str],
            additional_path: AdditionalPath
    ) -> str:
        try:
            with open(f'{self.base_path}/{additional_path.value}/{file.filename}', 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            return buffer.name

        except Exception as e:
            logger.error(f'Возникла ошибка при сохранении файла {e}')
            return ''

    async def get_file(
            self,
            path: Path
    ) -> FileResponse:
        with path.open('rb') as file:
            file_data = file.read()


        return FileResponse(
            filename=path.name,
            suffix=path.suffix,
            file_data=file_data,
            content_type=mimetypes.guess_type(path.name)[0]
        )

    async def delete_file(
            self,
            path: str
    ) -> bool:
        full_path = os.path.join(self.base_path, path)
        try:
            os.remove(full_path)
            return True
        except FileNotFoundError:
            return False

