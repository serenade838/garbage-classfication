import os
import shutil
import uuid
import random
from datetime import datetime
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from db.models import Resident, RecognitionHistory, FeedbackSample, GarbageCategory
from utils.auth_util import hash_password, verify_password, create_access_token
from fastapi import HTTPException
from schema.user_schema import RegisterReq, LoginReq, ChangePasswordReq, FeedbackReq
from config.settings import settings
from sqlalchemy import and_, desc, func
from typing import Optional
from datetime import timedelta
from db.models import SystemNotice
from db.models import ThrowRule, GarbageCategory
from sqlalchemy import or_
from ml.model_loader import predict_image
from PIL import Image
import cv2
import numpy as np
from PIL import Image


class UserService:
    @staticmethod
    def register(db: Session, req: RegisterReq):
        existing_user = db.query(Resident).filter(Resident.phone == req.phone).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="手机号已被注册")

        hashed_password = hash_password(req.password)
        # 获取昵称，若未提供则使用手机号
        nickname = req.nickname if req.nickname else req.phone
        new_user = Resident(
            phone=req.phone,
            password=hashed_password,
            nickname=nickname,  # 新增字段
            building=req.building or ""
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"msg": "注册成功"}

    @staticmethod
    def login(db: Session, req: LoginReq):
        try:
            user = db.query(Resident).filter(Resident.phone == req.phone).first()
            if not user:
                return {"code": 400, "msg": "手机号不存在", "data": None}

            if not verify_password(req.password, user.password):
                return {"code": 400, "msg": "密码错误", "data": None}

            token = create_access_token(data={
                "user_id": user.resident_id,
                "user_type": "resident"
            })

            nickname = user.nickname if user.nickname else user.phone
            return {
                "code": 200,
                "msg": "登录成功",
                "data": {
                    "token": token,
                    "user_id": user.resident_id,
                    "nickname": nickname
                }
            }
        except Exception as e:
            return {
                "code": 500,
                "msg": "系统错误",
                "error": type(e).__name__,
                "detail": str(e)
            }

    @staticmethod
    def change_password(db: Session, user_id: int, req: ChangePasswordReq):
        user = db.query(Resident).filter(Resident.resident_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if not verify_password(req.old_password, user.password):
            raise HTTPException(status_code=400, detail="旧密码错误")

        new_hashed = hash_password(req.new_password)
        user.password = new_hashed
        db.commit()

        return {"code": 200, "msg": "密码修改成功"}

    @staticmethod
    async def recognize(db: Session, user_id: int, image: UploadFile):
        # ---------- 1. 文件校验 ----------
        if not image.filename:
            raise HTTPException(status_code=400, detail="未选择文件")
        ext = os.path.splitext(image.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="图片格式不支持，仅支持jpg/png/jpeg")

        contents = await image.read()
        if len(contents) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="图片大小超过5MB限制")
        await image.seek(0)  # 重置指针，后续还需要读取

        # ---------- 2. 保存图片到磁盘 ----------
        date_str = datetime.now().strftime("%Y/%m/%d")
        save_dir = os.path.join(settings.UPLOAD_DIR, date_str)
        os.makedirs(save_dir, exist_ok=True)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(save_dir, unique_filename)
        relative_path = os.path.join(date_str, unique_filename).replace("\\", "/")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # ---------- 3. 模型推理（真实 YOLO） ----------
        await image.seek(0)  # 再次重置，以便从头部读取图片
        img_pil = Image.open(image.file).convert("RGB")
        detections = predict_image(img_pil)

        # 没检测到，默认“其他垃圾”
        if not detections:
            detections = [{
                "class_name": "其他垃圾",
                "confidence": 0.0
            }]

        # 投放建议与提示映射
        advice_map = {
            "可回收物": {"advice": "压扁后投入蓝色垃圾桶", "tips": "请清空残留液体"},
            "有害垃圾": {"advice": "轻拿轻放，投入红色垃圾桶", "tips": "避免破损泄漏"},
            "厨余垃圾": {"advice": "沥干水分后投入绿色垃圾桶", "tips": "请勿混入塑料袋"},
            "其他垃圾": {"advice": "投入灰色垃圾桶", "tips": "无法回收利用的废弃物"}
        }
        code_map = {
            "可回收物": "recyclable",
            "有害垃圾": "hazardous",
            "厨余垃圾": "kitchen",
            "其他垃圾": "other"
        }

        # 构造结果列表（每个检测框对应一个结果）
        result_items = []
        for det in detections:
            category_name = det["class_name"] if det["class_name"] in advice_map else "其他垃圾"
            confidence = det.get("confidence", 0.0)
            info = advice_map.get(category_name, advice_map["其他垃圾"])
            result_items.append({
                "category": category_name,
                "category_code": code_map.get(category_name, "other"),
                "confidence": confidence,
                "disposal_advice": info["advice"],
                "tips": info["tips"],
            })

        # ---------- 4. 保存识别历史 ----------
        # 将整个 result_items 列表存入 result_json
        result_json = {
            "results": result_items,
            "detections": detections  # 可包含坐标等原始数据，便于扩展
        }
        history = RecognitionHistory(
            resident_id=user_id,
            img_path=relative_path,
            result_json=result_json,
            has_feedback=0
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        # ---------- 5. 返回响应 ----------
        # 为兼容前端现有格式，我们返回第一个结果作为主结果，同时增加列表字段
        # ---------- 5. 返回响应 ----------
        # 取第一个结果作为主结果（兼容旧字段）
        first_result = result_items[0] if result_items else {
            "category": "其他垃圾",
            "category_code": "other",
            "confidence": 0.0,
            "disposal_advice": "投入灰色垃圾桶",
            "tips": "无法回收利用的废弃物"
        }
        image_url = f"/uploads/{relative_path}"
        return {
            "code": 200,
            "msg": "识别成功",
            "data": {
                "record_id": history.record_id,
                "category": first_result["category"],
                "category_code": first_result["category_code"],
                "confidence": first_result["confidence"],
                "disposal_advice": first_result["disposal_advice"],
                "tips": first_result["tips"],
                "image_url": image_url,
                "all_results": result_items,  # 所有检测结果列表
                "detections": detections  # 原始检测框数据（含坐标）
            }
        }




    @staticmethod
    def get_recognize_detail(db: Session, user_id: int, record_id: int):
        record = db.query(RecognitionHistory).filter(
            RecognitionHistory.record_id == record_id,
            RecognitionHistory.resident_id == user_id
        ).first()

        if not record:
            raise HTTPException(status_code=404, detail="记录不存在或无权限")

        result = record.result_json
        data = {
            "record_id": record.record_id,
            "image_url": f"/uploads/{record.img_path}",
            "category": result.get("category"),
            "category_code": result.get("category_code"),
            "confidence": result.get("confidence"),
            "disposal_advice": result.get("disposal_advice"),
            "is_correct": None,
            "created_at": record.rec_time.strftime("%Y-%m-%d %H:%M:%S") if record.rec_time else None
        }
        return {"code": 200, "msg": "获取成功", "data": data}

    @staticmethod
    def get_user_info(db: Session, user_id: int):
        user = db.query(Resident).filter(Resident.resident_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        total = db.query(RecognitionHistory).filter(RecognitionHistory.resident_id == user_id).count()
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "user_id": user.resident_id,
                "phone": user.phone,
                "nickname": user.nickname or user.phone,
                "building": user.building,
                "total_recognition": total,
                "created_at": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None
            }
        }
#xinzinz新增更改昵称
    @staticmethod
    def update_nickname(db: Session, user_id: int, new_nickname: str):
        user = db.query(Resident).filter(Resident.resident_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        user.nickname = new_nickname.strip()
        db.commit()
        return {"code": 200, "msg": "昵称更新成功"}

#关键词查询规则
    @staticmethod
    def search_rules(db: Session, keyword: str):
        # 模糊匹配垃圾名称或别名
        query = db.query(ThrowRule, GarbageCategory).join(
            GarbageCategory,
            ThrowRule.category_id == GarbageCategory.category_id
        ).filter(
            or_(
                ThrowRule.garbage_name.like(f"%{keyword}%"),
                ThrowRule.alias.like(f"%{keyword}%")
            )
        )
        results = query.all()
        data = []
        for rule, category in results:
            data.append({
                "id": rule.rule_id,
                "name": rule.garbage_name,
                "category": category.category_name,
                "category_code": "recyclable",  # 可扩展，暂时硬编码或从category获取编码
                "advice": rule.tip or "请正确分类投放"
                # 若需额外字段可扩展
            })
        return {"code": 200, "msg": "查询成功", "data": data}

#四大垃圾分类
    @staticmethod
    def get_all_categories(db: Session):
        categories = db.query(GarbageCategory).order_by(GarbageCategory.sort).all()
        # 预定义颜色映射（可按需调整）
        color_map = {
            "可回收物": "#2196F3",
            "厨余垃圾": "#4CAF50",
            "有害垃圾": "#F44336",
            "其他垃圾": "#9E9E9E"
        }
        code_map = {
            "可回收物": "recyclable",
            "厨余垃圾": "kitchen",
            "有害垃圾": "hazardous",
            "其他垃圾": "other"
        }
        data = []
        for c in categories:
            data.append({
                "id": c.category_id,
                "name": c.category_name,
                "code": code_map.get(c.category_name, ""),
                "color": color_map.get(c.category_name, ""),
                "description": ""  # 暂无描述字段，可后续扩展
            })
        return {"code": 200, "msg": "获取成功", "data": data}

    @staticmethod
    def get_history_list(db: Session, user_id: int, page: int, size: int, category: Optional[str] = None):
        query = db.query(RecognitionHistory).filter(RecognitionHistory.resident_id == user_id)
        if category:
            query = query.filter(RecognitionHistory.result_json['category'].astext == category)
        total = query.count()
        records = query.order_by(desc(RecognitionHistory.rec_time)) \
            .offset((page - 1) * size) \
            .limit(size) \
            .all()
        list_data = []
        for record in records:
            result = record.result_json
            # 兼容多种存储格式
            if isinstance(result, dict):
                # 优先取 all_results 或 results 列表
                if "all_results" in result and result["all_results"]:
                    first = result["all_results"][0]
                    cat = first.get("category")
                    conf = first.get("confidence")
                elif "results" in result and result["results"]:
                    first = result["results"][0]
                    cat = first.get("category")
                    conf = first.get("confidence")
                else:
                    # 单结果模式
                    cat = result.get("category")
                    conf = result.get("confidence")
            else:
                cat = None
                conf = None

            list_data.append({
                "id": record.record_id,
                "image_url": f"/uploads/{record.img_path}",
                "category": cat or "未识别",
                "confidence": conf if conf is not None else "--",
                "created_at": record.rec_time.strftime("%Y-%m-%d %H:%M:%S") if record.rec_time else None
            })
        return {
            "code": 200,
            "msg": "查询成功",
            "data": {
                "total": total,
                "page": page,
                "size": size,
                "list": list_data
            }
        }

    @staticmethod
    def delete_history(db: Session, user_id: int, record_id: int):
        record = db.query(RecognitionHistory).filter(
            RecognitionHistory.record_id == record_id,
            RecognitionHistory.resident_id == user_id
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在或无权限")
        db.delete(record)
        db.commit()
        return {"code": 200, "msg": "删除成功"}

    @staticmethod
    def add_feedback(db: Session, user_id: int, req: FeedbackReq):
        # 1. 验证记录存在且属于该用户
        record = db.query(RecognitionHistory).filter(
            RecognitionHistory.record_id == req.record_id,
            RecognitionHistory.resident_id == user_id
        ).first()
        if not record:
            raise HTTPException(status_code=404, detail="识别记录不存在或无权限")

        # 2. 根据类别名称获取类别ID
        category = db.query(GarbageCategory).filter(
            GarbageCategory.category_name == req.correct_category
        ).first()
        if not category:
            raise HTTPException(status_code=400, detail="无效的类别名称")

        # 3. 防止重复提交
        existing = db.query(FeedbackSample).filter(
            FeedbackSample.record_id == req.record_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="该记录已提交过反馈，请勿重复提交")

        # 4. 创建反馈记录
        feedback = FeedbackSample(
            record_id=req.record_id,
            user_label=category.category_id,
            remark="",
            audit_status=0,
            audit_admin_id=None,
            audit_reason="",
            use_for_train=0
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return {"code": 200, "msg": "反馈提交成功，等待管理员审核"}

#排行榜
    @staticmethod
    def get_rank(db: Session, cycle: str):
        now = datetime.now()
        if cycle == "day":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif cycle == "week":
            start_time = now - timedelta(days=7)
        elif cycle == "month":
            start_time = now - timedelta(days=30)
        else:
            start_time = None

        query = db.query(
            Resident.nickname,
            Resident.phone,
            func.count(RecognitionHistory.record_id).label("total")
        ).join(RecognitionHistory, Resident.resident_id == RecognitionHistory.resident_id)
        if start_time:
            query = query.filter(RecognitionHistory.rec_time >= start_time)
        query = query.group_by(Resident.resident_id).order_by(desc("total")).limit(10)

        results = query.all()
        rank_list = []
        for idx, row in enumerate(results, 1):
            # 先定义 display_name
            display_name = row.nickname if row.nickname else row.phone
            rank_list.append({
                "rank": idx,
                "nickname": display_name,
                "total_recognition": row.total
            })
        return {"code": 200, "msg": "获取成功", "data": rank_list}

#公告列表
    @staticmethod
    def get_notice_list(db: Session):
        notices = db.query(SystemNotice).order_by(desc(SystemNotice.publish_time)).all()
        list_data = []
        for n in notices:
            summary = n.content[:50] + ("..." if len(n.content) > 50 else "")
            list_data.append({
                "id": n.notice_id,
                "title": n.title,
                "summary": summary,
                "is_top": False,  # 可扩展
                "created_at": n.publish_time.strftime("%Y-%m-%d %H:%M:%S") if n.publish_time else None
            })
        return {"code": 200, "msg": "获取成功", "data": list_data}

#公告详情
    @staticmethod
    def get_notice_detail(db: Session, notice_id: int):
        notice = db.query(SystemNotice).filter(SystemNotice.notice_id == notice_id).first()
        if not notice:
            raise HTTPException(status_code=404, detail="公告不存在")
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "id": notice.notice_id,
                "title": notice.title,
                "content": notice.content,
                "created_at": notice.publish_time.strftime("%Y-%m-%d %H:%M:%S") if notice.publish_time else None
            }

      }

    @staticmethod
    def update_building(db: Session, user_id: int, new_building: str):
        user = db.query(Resident).filter(Resident.resident_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        user.building = new_building.strip()
        db.commit()
        return {"code": 200, "msg": "楼栋更新成功"}

    @staticmethod
    def get_my_feedback(db: Session, user_id: int):
        # 查询当前用户的所有识别记录ID
        subq = db.query(RecognitionHistory.record_id).filter(RecognitionHistory.resident_id == user_id).subquery()
        # 关联反馈表
        feedbacks = db.query(FeedbackSample).filter(FeedbackSample.record_id.in_(subq)).order_by(
            desc(FeedbackSample.create_time)).all()
        result = []
        for fb in feedbacks:
            # 获取原识别结果类别
            record = db.query(RecognitionHistory).filter(RecognitionHistory.record_id == fb.record_id).first()
            original_category = "未知"
            if record and record.result_json:
                # 兼容不同存储格式
                if isinstance(record.result_json, dict):
                    original_category = record.result_json.get("category", "未知")
                elif isinstance(record.result_json, str):
                    try:
                        import json
                        data = json.loads(record.result_json)
                        original_category = data.get("category", "未知")
                    except:
                        original_category = "未知"
            # 获取用户纠正的类别名称
            category = db.query(GarbageCategory).filter(GarbageCategory.category_id == fb.user_label).first()
            user_correct = category.category_name if category else "未知"
            result.append({
                "sample_id": fb.sample_id,
                "record_id": fb.record_id,
                "original_category": original_category,
                "user_correct_category": user_correct,
                "audit_status": fb.audit_status,
                "audit_reason": fb.audit_reason or "",
                "audit_admin_id": fb.audit_admin_id,
                "create_time": fb.create_time.strftime("%Y-%m-%d %H:%M:%S") if fb.create_time else "",
                "audit_time": fb.audit_time.strftime("%Y-%m-%d %H:%M:%S") if fb.audit_time else None
            })
        return {"code": 200, "msg": "获取成功", "data": result}

