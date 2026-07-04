import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from router.user_router import router as user_router
from router.admin_router import router as admin_router
from db.database import engine, Base
from config.settings import settings
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import logging


app = FastAPI(title="生活垃圾智能分类系统API", version="1.0")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取项目根目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# 创建上传目录
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
# 挂载静态目录（优先于路由）
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
# 配置日志
logging.basicConfig(level=logging.INFO)
@app.get("/uploads/{path:path}")
async def serve_uploaded_file(path: str):
    try:
        # 构造完整路径
        file_path = os.path.normpath(os.path.join(UPLOAD_DIR, path))
        # 安全检查
        if not file_path.startswith(os.path.normpath(UPLOAD_DIR)):
            logging.warning(f"Path traversal attempt: {path}")
            raise HTTPException(status_code=403, detail="Forbidden")
        if not os.path.exists(file_path):
            logging.warning(f"File not found: {file_path}")
            raise HTTPException(status_code=404, detail="File not found")
        if not os.access(file_path, os.R_OK):
            logging.warning(f"Permission denied: {file_path}")
            raise HTTPException(status_code=403, detail="Permission denied")
        # 返回文件
        return FileResponse(file_path)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error serving file {path}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 启动时自动创建数据表
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

# 注册路由
app.include_router(user_router)
app.include_router(admin_router)

# 健康检查
@app.get("/health", summary="健康检查")
def health_check():
    return {"status": "ok", "msg": "服务运行正常"}

@app.get("/test-file")
async def test_file():
    import os
    test_path = os.path.join(UPLOAD_DIR, "2026", "07", "03", "5e87d5feb5bb491999651f38e9fd98c5.jpg")
    exists = os.path.exists(test_path)
    readable = os.access(test_path, os.R_OK)
    return {"exists": exists, "readable": readable, "path": test_path}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


