from sqlalchemy import Column, String, BIGINT, Integer, DATETIME, JSON, FLOAT, TEXT, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


# ============================================================
# 1. 居民用户表（对应 resident）
# ============================================================
class Resident(Base):
    __tablename__ = "resident"
    resident_id = Column(BIGINT, primary_key=True, autoincrement=True)
    phone = Column(String(11), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    nickname = Column(String(50), default='')  # 新增
    building = Column(String(32), default="")
    status = Column(Integer, default=1)
    create_time = Column(DATETIME, default=datetime.now)
    update_time = Column(DATETIME, default=datetime.now, onupdate=datetime.now)


# ============================================================
# 2. 管理员表（对应 administrator）
# ============================================================
class Administrator(Base):
    __tablename__ = "administrator"
    admin_id = Column(BIGINT, primary_key=True, autoincrement=True)
    username = Column(String(32), unique=True, nullable=False)
    password = Column(String(64), nullable=False)
    real_name = Column(String(20), default="")
    create_time = Column(DATETIME, default=datetime.now)
    update_time = Column(DATETIME, default=datetime.now, onupdate=datetime.now)


# ============================================================
# 3. 垃圾四大类（对应 garbage_category）
# ============================================================
class GarbageCategory(Base):
    __tablename__ = "garbage_category"
    category_id = Column(BIGINT, primary_key=True, autoincrement=True)
    category_name = Column(String(20), unique=True, nullable=False)
    sort = Column(Integer, default=0)


# ============================================================
# 4. 细分垃圾投放规则（对应 throw_rule）
# ============================================================
class ThrowRule(Base):
    __tablename__ = "throw_rule"
    rule_id = Column(BIGINT, primary_key=True, autoincrement=True)
    category_id = Column(BIGINT, nullable=False)
    garbage_name = Column(String(50), nullable=False)
    alias = Column(String(100), default="")
    tip = Column(TEXT, default=None)
    confuse_tip = Column(TEXT, default=None)
    create_time = Column(DATETIME, default=datetime.now)
    update_time = Column(DATETIME, default=datetime.now, onupdate=datetime.now)


# ============================================================
# 5. AI识别历史记录（对应 recognition_history）
# ============================================================
class RecognitionHistory(Base):
    __tablename__ = "recognition_history"
    record_id = Column(BIGINT, primary_key=True, autoincrement=True)
    resident_id = Column(BIGINT, nullable=False)
    img_path = Column(String(255), nullable=False)
    result_json = Column(JSON, nullable=False)
    has_feedback = Column(Integer, default=0)
    rec_time = Column(DATETIME, default=datetime.now)


# ============================================================
# 6. 用户纠错样本表（对应 feedback_sample）
# ============================================================
class FeedbackSample(Base):
    __tablename__ = "feedback_sample"
    sample_id = Column(BIGINT, primary_key=True, autoincrement=True)
    record_id = Column(BIGINT, nullable=False)
    user_label = Column(BIGINT, nullable=False)
    remark = Column(String(200), default="")
    audit_status = Column(Integer, default=0)
    audit_admin_id = Column(BIGINT, default=None)
    audit_reason = Column(String(200), default="")
    use_for_train = Column(Integer, default=0)
    create_time = Column(DATETIME, default=datetime.now)
    audit_time = Column(DATETIME, default=None)


# ============================================================
# 7. 模型配置表（对应 model_config）
# ============================================================
class ModelConfig(Base):
    __tablename__ = "model_config"
    config_id = Column(BIGINT, primary_key=True, autoincrement=True)
    model_type = Column(String(20), nullable=False)
    version = Column(String(20), nullable=False)
    onnx_path = Column(String(255), nullable=False)
    map_score = Column(FLOAT, default=None)
    accuracy = Column(FLOAT, default=None)
    f1_score = Column(FLOAT, default=None)
    conf_thresh = Column(FLOAT, default=0.5)
    iou_thresh = Column(FLOAT, default=0.45)
    train_time = Column(DATETIME, default=None)
    is_online = Column(Integer, default=0)


# ============================================================
# 8. 科普公告表（对应 system_notice）
# ============================================================
class SystemNotice(Base):
    __tablename__ = "system_notice"
    notice_id = Column(BIGINT, primary_key=True, autoincrement=True)
    admin_id = Column(BIGINT, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(TEXT, nullable=False)
    show_miniprogram = Column(Integer, default=1)
    publish_time = Column(DATETIME, default=datetime.now)