"""
检测历史记录 API 路由
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.database import DetectionHistory, User, get_db
from app.utils.auth import get_current_user
from app.models.schemas import HistoryListResponse, DetectionHistoryResponse
from typing import Optional

router = APIRouter(prefix="/api/history", tags=["检测历史"])


@router.get("/list", response_model=HistoryListResponse)
def get_history_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    detection_type: Optional[str] = Query(None, description="检测类型筛选：single, batch, video, camera"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的检测历史记录列表
    """
    # 构建查询
    query = db.query(DetectionHistory).filter(DetectionHistory.user_id == current_user.id)
    
    # 按类型筛选
    if detection_type:
        query = query.filter(DetectionHistory.detection_type == detection_type)
    
    # 按创建时间倒序
    query = query.order_by(desc(DetectionHistory.created_at))
    
    # 总数
    total = query.count()
    
    # 分页
    skip = (page - 1) * page_size
    histories = query.offset(skip).limit(page_size).all()
    
    # 转换为响应模型
    history_list = [
        DetectionHistoryResponse.model_validate(history)
        for history in histories
    ]
    
    return HistoryListResponse(
        code=200,
        message="获取成功",
        total=total,
        data=history_list
    )


@router.delete("/{history_id}")
def delete_history(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除指定的历史记录
    """
    # 查找记录
    history = db.query(DetectionHistory).filter(
        DetectionHistory.id == history_id,
        DetectionHistory.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="历史记录不存在")
    
    # 删除
    db.delete(history)
    db.commit()
    
    return {"code": 200, "message": "删除成功"}


@router.delete("/")
def delete_all_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除当前用户的所有历史记录
    """
    # 删除所有
    db.query(DetectionHistory).filter(
        DetectionHistory.user_id == current_user.id
    ).delete()
    db.commit()
    
    return {"code": 200, "message": "清空成功"}


# 辅助函数：保存检测历史
def save_detection_history(
    db: Session,
    user_id: int,
    detection_type: str,
    image_url: Optional[str] = None,
    result_url: Optional[str] = None,
    building_count: int = 0,
    total_area: float = 0.0,
    confidence_avg: float = 0.0,
    details: Optional[dict] = None
):
    """
    保存检测历史记录的辅助函数
    """
    history = DetectionHistory(
        user_id=user_id,
        detection_type=detection_type,
        image_url=image_url,
        result_url=result_url,
        building_count=building_count,
        total_area=total_area,
        confidence_avg=confidence_avg,
        details=json.dumps(details, ensure_ascii=False) if details else None
    )
    
    db.add(history)
    db.commit()
    db.refresh(history)
    
    return history
