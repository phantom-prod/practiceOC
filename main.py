import uvicorn
from fastapi import FastAPI
from src.router import router

app = FastAPI()
app.include_router(router)

# main:app название приложения, тут ничего не менять
if __name__ == "__main__":
    # reload=True позволяет при каждом сохранении перезапускать сервер
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, workers=3)

    """main.py используется для запуска, в него подключаем модуль для запуска локалхоста - uvicorn и сам модуль фастапи, который имеет в своей арсенале swagger
    при переходе на /docs"""