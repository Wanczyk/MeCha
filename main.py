import uvicorn
from fastapi import FastAPI
from src.api.routers import router_v1

app = FastAPI()
app.include_router(router_v1)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
