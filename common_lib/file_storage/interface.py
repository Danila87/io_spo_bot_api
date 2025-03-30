from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Union

from fastapi import UploadFile
from schemas.service import FileResponse, AdditionalPath


class FileStorageInterface(ABC):

    @abstractmethod
    async def save_file(
            self,
            additional_path: AdditionalPath,
            file: Union[UploadFile, str],
    ) -> bool:
        pass

    @abstractmethod
    async def get_file(
            self,
            path: Path
    ) -> FileResponse:
        pass

    @abstractmethod
    async def delete_file(
            self,
            path: str
    ) -> bool:
        pass
