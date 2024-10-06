import uvicorn

from fastapi import FastAPI

from routers.song.router import song_router
from routers.service.router import router_service
from routers.piggy_bank.router import piggy_bank_router
from routers.methodical_book.router import methodical_book_router

app = FastAPI()

app.include_router(
    router=song_router,
    )

app.include_router(
    router=router_service,
)

app.include_router(
    router=piggy_bank_router
)

app.include_router(
    router=methodical_book_router
)


@app.get('/')
def main():
    return 'Success'


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)