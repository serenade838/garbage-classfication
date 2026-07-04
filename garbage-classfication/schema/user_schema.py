from pydantic import BaseModel, Field
from typing import Optional, List

class RegisterReq(BaseModel):
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, description="密码")
    building: Optional[str] = None
    nickname: Optional[str] = None

class LoginReq(BaseModel):
    phone: str
    password: str

class LoginResp(BaseModel):
    token: str
    user_id: int
    nickname: str

class ChangePasswordReq(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码，不少于6位")

#纠错反馈
class FeedbackReq(BaseModel):
    record_id: int = Field(..., description="识别记录ID")
    correct_category: str = Field(..., description="用户认为正确的类别名称")

class ChangeNicknameReq(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=50, description="新昵称")

class UpdateBuildingReq(BaseModel):
    building: str = Field(..., max_length=32, description="新楼栋")

class FeedbackStatusItem(BaseModel):
    sample_id: int
    record_id: int
    original_category: str          # 原识别类别
    user_correct_category: str      # 用户提交的正确类别
    audit_status: int               # 0-待审核，1-通过，2-驳回
    audit_reason: Optional[str] = None
    audit_admin_id: Optional[int] = None
    create_time: str
    audit_time: Optional[str] = None

class FeedbackListResp(BaseModel):
    code: int
    msg: str
    data: List[FeedbackStatusItem]

