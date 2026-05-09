from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models.points_log import PointsRule
from ..schemas.points import PointsRuleCreate, PointsRuleUpdate, PointsRuleOut
from ..utils.deps import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/rules", tags=["积分规则"])


@router.get("/", response_model=list[PointsRuleOut])
async def list_rules(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PointsRule).where(PointsRule.owner_id == user.id).order_by(PointsRule.id)
    )
    return [PointsRuleOut.model_validate(r) for r in result.scalars().all()]


@router.post("/", response_model=PointsRuleOut)
async def create_rule(
    data: PointsRuleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rule = PointsRule(
        name=data.name,
        points=data.points,
        category=data.category,
        icon=data.icon,
        owner_id=user.id,
    )
    db.add(rule)
    await db.flush()
    await db.refresh(rule)
    return PointsRuleOut.model_validate(rule)


@router.put("/{rule_id}", response_model=PointsRuleOut)
async def update_rule(
    rule_id: int,
    data: PointsRuleUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PointsRule).where(PointsRule.id == rule_id, PointsRule.owner_id == user.id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")

    if data.name is not None:
        rule.name = data.name
    if data.points is not None:
        rule.points = data.points
    if data.category is not None:
        rule.category = data.category
    if data.icon is not None:
        rule.icon = data.icon
    if data.is_active is not None:
        rule.is_active = data.is_active
    await db.flush()
    await db.refresh(rule)
    return PointsRuleOut.model_validate(rule)


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PointsRule).where(PointsRule.id == rule_id, PointsRule.owner_id == user.id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    await db.delete(rule)
    return {"message": "规则已删除"}
