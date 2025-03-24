from pathlib import Path
from contextlib import asynccontextmanager
from typing import Union

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from starlette.datastructures import UploadFile


from .interface import FileStorageInterface
from schemas.service import FileResponse, AdditionalPath

from common_lib.logger import logger


class S3Storage(FileStorageInterface):

   def __init__(
           self,
           access_key: str,
           secret_key: str,
           bucket_name: str,
           endpoint_url: str,
   ):
      self.config = {
         "service_name": "s3",
         "endpoint_url": endpoint_url,
         "aws_access_key_id": access_key,
         "aws_secret_access_key": secret_key,
      }

      self.bucket_name = bucket_name
      self.session = get_session()

   @asynccontextmanager
   async def get_client(self):
      async with self.session.create_client(**self.config) as client:
         yield client

   async def get_file(
           self,
           path: Path,
   ) -> FileResponse:
      try:
         async with self.get_client() as client:
            response = await client.get_object(
               Bucket=self.bucket_name,
               Key=str(path)
            )

            return FileResponse(
               filename=path.name,
               suffix=path.suffix,
               file_data=await response["Body"].read(),
               content_type=response["ContentType"],
            )

      except ClientError as e:
         logger.error(f"Ошибка при скачивании файла: {e}")

   async def save_file(
           self,
           additional_path: AdditionalPath,
           file: Union[UploadFile, str],
   ):
      if isinstance(file, str):
         return await self.save_file_from_str(file, additional_path)

      content = file.file.read()
      try:
         async with self.get_client() as client:
             await client.put_object(
               Bucket=self.bucket_name,
               Key=f'{additional_path.value}/{file.filename}',
               Body=content,
               ContentType=file.content_type,
            )
         return True

      except ClientError as e:
         logger.error(f"Ошибка при сохранении: {e}")
         return False

   async def save_file_from_str(
           self,
           file_path: str,
           additional_path: AdditionalPath,
   ) -> str:
      file = Path(additional_path.value, file_path)

      async with self.get_client() as client:
         with file.open('r') as file_data:
            response = await client.put_object(
               Bucket=self.bucket_name,
               Key=str(file),
               Body=file_data,
            )

            return response

   async def delete_file(
           self,
           path: str,
   ):
      pass

