from fastapi import FastAPI
from apps.user_service.routes import router as user_router
from apps.auth_service.routes import router as auth_router
from apps.content_service.routes import router as content_router

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(content_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
