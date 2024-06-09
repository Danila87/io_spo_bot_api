import shutil
from typing import Any


def save_file(path: str, file: Any) -> bool:
    try:
        with open(f'{path}/{file.filename}', 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        return buffer.name

    except:
        return False
