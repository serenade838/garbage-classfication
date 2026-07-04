from fastapi import APIRouter, Depends, Security, HTTPException, UploadFile, File, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Resident
from schema.user_schema import RegisterReq, LoginReq, ChangePasswordReq, FeedbackReq
from service.user_service import UserService
from utils.auth_util import decode_token
from schema.user_schema import ChangeNicknameReq
from typing import Optional
from schema.user_schema import UpdateBuildingReq
from schema.user_schema import RegisterReq, LoginReq, ChangePasswordReq, FeedbackReq, ChangeNicknameReq
router = APIRouter(prefix="/user", tags=["居民用户端"])
security = HTTPBearer()

# 依赖：从Token中获取当前用户ID
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="无效Token")
    user = db.query(Resident).filter(Resident.resident_id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user_id

@router.post("/register", summary="用户注册")
def register(req: RegisterReq, db: Session = Depends(get_db)):
    return UserService.register(db, req)

@router.post("/login", summary="用户登录")
def login(req: LoginReq, db: Session = Depends(get_db)):
    return UserService.login(db, req)

@router.get("/info", summary="获取个人信息")
def get_user_info(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return UserService.get_user_info(db, user_id)

@router.post("/change_password", summary="修改密码")
def change_password(
    req: ChangePasswordReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return UserService.change_password(db, user_id, req)

#图片识别
@router.post("/recognize", summary="图片识别")
async def recognize(
    image: UploadFile = File(..., description="图片文件"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return await UserService.recognize(db, user_id, image)

#识别详情
@router.get("/recognize/{record_id}", summary="获取识别详情")
def get_recognize_detail(
    record_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return UserService.get_recognize_detail(db, user_id, record_id)

#关键词查询分类规则
@router.get("/rules", summary="关键词查询分类规则")
def search_rules(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    return UserService.search_rules(db, keyword)

#四大垃圾全部分类
@router.get("/category/all", summary="获取四大垃圾全部分类")
def get_all_categories(db: Session = Depends(get_db)):
    return UserService.get_all_categories(db)


#历史
@router.get("/history/list", summary="分页查询历史记录")
def get_history_list(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="按类别筛选（如：可回收物）"),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return UserService.get_history_list(db, user_id, page, size, category)

#删除历史
@router.delete("/history/{record_id}", summary="删除历史记录")
def delete_history(
    record_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return UserService.delete_history(db, user_id, record_id)

#纠错反馈
@router.post("/feedback/add", summary="提交纠错反馈")
def add_feedback(
    req: FeedbackReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return UserService.add_feedback(db, user_id, req)

#排行榜
@router.get("/rank", summary="获取识别排行榜")
def get_rank(
    cycle: str = Query("month", regex="^(day|week|month|all)$", description="统计周期"),
    db: Session = Depends(get_db)
):
    return UserService.get_rank(db, cycle)

#公告列表
@router.get("/notice/list", summary="公告列表")
def get_notice_list(db: Session = Depends(get_db)):
    return UserService.get_notice_list(db)

#公告详情
@router.get("/notice/{notice_id}", summary="公告详情")
def get_notice_detail(
    notice_id: int,
    db: Session = Depends(get_db)
):
    return UserService.get_notice_detail(db, notice_id)

#xiugaimz
@router.put("/nickname", summary="修改昵称")
def update_nickname(
    req: ChangeNicknameReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return UserService.update_nickname(db, user_id, req.nickname)

  # 导入

@router.put("/building", summary="修改楼栋")
def update_building(
    req: UpdateBuildingReq,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return UserService.update_building(db, user_id, req.building)

#查看反馈结果
@router.get("/feedback/list", summary="获取我的纠错反馈列表")
def get_my_feedback(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return UserService.get_my_feedback(db, user_id)

