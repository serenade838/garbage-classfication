from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from schema.admin_schema import AdminLoginReq
from service.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["管理员端"])

@router.post("/login", summary="管理员登录")
def admin_login(req: AdminLoginReq, db: Session = Depends(get_db)):
    return AdminService.login(db, req)