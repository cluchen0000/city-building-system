"""
城市建筑检测系统 - FastAPI 应用入口
"""
from dotenv import load_dotenv
load_dotenv()  # 加载 backend/.env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.building_detect import router as detect_router
from app.api.camera import router as camera_router

app = FastAPI(
    title=settings.APP_NAME,
    description="基于 YOLO11 的遥感影像建筑物检测与面积统计",
    version=settings.APP_VERSION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（上传图 + 结果图）
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# 注册路由
app.include_router(detect_router)
app.include_router(camera_router)


@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
