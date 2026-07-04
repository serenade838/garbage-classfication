from sqlalchemy.orm import Session
from db.models import Administrator
from schema.admin_schema import AdminLoginReq
from utils.auth_util import create_access_token, verify_password

class AdminService:
    @staticmethod
    def login(db: Session, req: AdminLoginReq):
        try:
            admin = db.query(Administrator).filter(Administrator.username == req.username).first()
            if not admin:
                return {"code": 400, "msg": "管理员账号不存在", "data": None}

            # 用 bcrypt 验证密码
            if not verify_password(req.password, admin.password):
                return {"code": 400, "msg": "密码错误", "data": None}

            token = create_access_token(data={
                "admin_id": admin.id,
                "user_type": "admin"
            })

            return {
                "code": 200,
                "msg": "登录成功",
                "data": {
                    "token": token,
                    "admin_id": admin.id,
                    "username": admin.username
                }
            }
        except Exception as e:
            return {
                "code": 500,
                "msg": "系统错误",
                "error": type(e).__name__,
                "detail": str(e)
            }