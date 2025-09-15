from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from backend.database.connection import get_database
from backend.database.models import (
    Order, OrderItem, Product, User, Review, AgentLog, 
    PriceHistory, InventoryLog, CustomerInteraction
)
from backend.api.auth import get_current_active_user

logger = logging.getLogger(__name__)
router = APIRouter()

def require_admin(current_user: User = Depends(get_current_active_user)):
    """Require admin access"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/dashboard")
async def get_dashboard_analytics(
    days: int = Query(30, ge=1, le=365),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """Get dashboard analytics overview"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Revenue metrics
        revenue_data = db.query(
            func.sum(Order.total_amount).label('total_revenue'),
            func.count(Order.id).label('total_orders'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.status.in_(['processing', 'shipped', 'delivered'])
            )
        ).first()
        
        # User metrics
        total_users = db.query(User).count()
        new_users = db.query(User).filter(User.created_at >= start_date).count()
        
        # Product metrics
        total_products = db.query(Product).filter(Product.is_active == True).count()
        low_stock_products = db.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.stock_quantity <= Product.min_stock_level
            )
        ).count()
        
        # Top selling products
        top_products = db.query(
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.total_price).label('total_revenue')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.status.in_(['processing', 'shipped', 'delivered'])
            )
        ).group_by(
            Product.id, Product.name
        ).order_by(
            desc('total_sold')
        ).limit(5).all()
        
        # Agent performance
        agent_performance = db.query(
            AgentLog.agent_name,
            func.count(AgentLog.id).label('total_executions'),
            func.sum(func.case([(AgentLog.result == 'success', 1)], else_=0)).label('successful_executions')
        ).filter(
            AgentLog.created_at >= start_date
        ).group_by(
            AgentLog.agent_name
        ).all()
        
        return {
            "period_days": days,
            "revenue": {
                "total_revenue": float(revenue_data.total_revenue or 0),
                "total_orders": revenue_data.total_orders or 0,
                "average_order_value": float(revenue_data.avg_order_value or 0)
            },
            "users": {
                "total_users": total_users,
                "new_users": new_users,
                "growth_rate": round((new_users / max(total_users - new_users, 1)) * 100, 2)
            },
            "products": {
                "total_active_products": total_products,
                "low_stock_products": low_stock_products,
                "stock_alert_rate": round((low_stock_products / max(total_products, 1)) * 100, 2)
            },
            "top_selling_products": [
                {
                    "name": product.name,
                    "units_sold": int(product.total_sold),
                    "revenue": float(product.total_revenue)
                }
                for product in top_products
            ],
            "ai_agents": {
                "total_agents": len(agent_performance),
                "performance": [
                    {
                        "agent_name": agent.agent_name,
                        "executions": int(agent.total_executions),
                        "success_rate": round(
                            (int(agent.successful_executions) / max(int(agent.total_executions), 1)) * 100, 2
                        )
                    }
                    for agent in agent_performance
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@router.get("/sales")
async def get_sales_analytics(
    days: int = Query(30, ge=1, le=365),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """Get sales analytics with time series data"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Determine grouping format
        if group_by == "day":
            date_format = func.date(Order.created_at)
        elif group_by == "week":
            date_format = func.date_trunc('week', Order.created_at)
        else:  # month
            date_format = func.date_trunc('month', Order.created_at)
        
        # Sales over time
        sales_data = db.query(
            date_format.label('period'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('orders'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.status.in_(['processing', 'shipped', 'delivered'])
            )
        ).group_by(
            date_format
        ).order_by(
            date_format
        ).all()
        
        # Sales by category
        category_sales = db.query(
            Product.category_id,
            func.sum(OrderItem.total_price).label('revenue'),
            func.sum(OrderItem.quantity).label('units_sold')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            and_(
                Order.created_at >= start_date,
                Order.status.in_(['processing', 'shipped', 'delivered'])
            )
        ).group_by(
            Product.category_id
        ).order_by(
            desc('revenue')
        ).all()
        
        return {
            "period_days": days,
            "group_by": group_by,
            "time_series": [
                {
                    "period": str(data.period),
                    "revenue": float(data.revenue),
                    "orders": int(data.orders),
                    "avg_order_value": float(data.avg_order_value)
                }
                for data in sales_data
            ],
            "category_breakdown": [
                {
                    "category_id": data.category_id,
                    "revenue": float(data.revenue),
                    "units_sold": int(data.units_sold)
                }
                for data in category_sales
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting sales analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sales analytics")

@router.get("/inventory")
async def get_inventory_analytics(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """Get inventory analytics"""
    try:
        # Inventory levels
        inventory_stats = db.query(
            func.count(Product.id).label('total_products'),
            func.sum(Product.stock_quantity).label('total_stock'),
            func.avg(Product.stock_quantity).label('avg_stock'),
            func.sum(func.case([(Product.stock_quantity <= Product.min_stock_level, 1)], else_=0)).label('low_stock_count'),
            func.sum(func.case([(Product.stock_quantity == 0, 1)], else_=0)).label('out_of_stock_count')
        ).filter(
            Product.is_active == True
        ).first()
        
        # Recent inventory changes
        recent_changes = db.query(InventoryLog).order_by(
            desc(InventoryLog.created_at)
        ).limit(10).all()
        
        # Products needing attention
        attention_products = db.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.stock_quantity <= Product.min_stock_level
            )
        ).order_by(
            Product.stock_quantity.asc()
        ).limit(20).all()
        
        return {
            "inventory_summary": {
                "total_products": int(inventory_stats.total_products or 0),
                "total_stock_units": int(inventory_stats.total_stock or 0),
                "average_stock_per_product": float(inventory_stats.avg_stock or 0),
                "low_stock_products": int(inventory_stats.low_stock_count or 0),
                "out_of_stock_products": int(inventory_stats.out_of_stock_count or 0)
            },
            "recent_changes": [
                {
                    "id": log.id,
                    "product_id": log.product_id,
                    "change_type": log.change_type,
                    "quantity_change": log.quantity_change,
                    "new_quantity": log.new_quantity,
                    "reason": log.reason,
                    "agent_action": log.agent_action,
                    "created_at": log.created_at.isoformat()
                }
                for log in recent_changes
            ],
            "products_needing_attention": [
                {
                    "id": product.id,
                    "name": product.name,
                    "sku": product.sku,
                    "current_stock": product.stock_quantity,
                    "min_stock_level": product.min_stock_level,
                    "status": "out_of_stock" if product.stock_quantity == 0 else "low_stock"
                }
                for product in attention_products
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting inventory analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve inventory analytics")

@router.get("/pricing")
async def get_pricing_analytics(
    days: int = Query(30, ge=1, le=365),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """Get pricing analytics"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Price changes
        price_changes = db.query(PriceHistory).filter(
            PriceHistory.created_at >= start_date
        ).count()
        
        ai_price_changes = db.query(PriceHistory).filter(
            and_(
                PriceHistory.created_at >= start_date,
                PriceHistory.agent_action == True
            )
        ).count()
        
        # Recent price changes
        recent_changes = db.query(PriceHistory).order_by(
            desc(PriceHistory.created_at)
        ).limit(10).all()
        
        # Price elasticity analysis
        elasticity_data = db.query(
            func.avg(Product.price_elasticity).label('avg_elasticity'),
            func.count(func.case([(Product.price_elasticity < -1, 1)], else_=None)).label('elastic_products'),
            func.count(func.case([(Product.price_elasticity >= -1, 1)], else_=None)).label('inelastic_products')
        ).filter(
            and_(
                Product.is_active == True,
                Product.price_elasticity.isnot(None)
            )
        ).first()
        
        return {
            "period_days": days,
            "price_change_summary": {
                "total_price_changes": price_changes,
                "ai_automated_changes": ai_price_changes,
                "automation_rate": round((ai_price_changes / max(price_changes, 1)) * 100, 2)
            },
            "elasticity_analysis": {
                "average_elasticity": float(elasticity_data.avg_elasticity or 0),
                "elastic_products": int(elasticity_data.elastic_products or 0),
                "inelastic_products": int(elasticity_data.inelastic_products or 0)
            },
            "recent_price_changes": [
                {
                    "id": change.id,
                    "product_id": change.product_id,
                    "old_price": float(change.old_price),
                    "new_price": float(change.new_price),
                    "change_percent": round(((change.new_price - change.old_price) / change.old_price) * 100, 2),
                    "change_reason": change.change_reason,
                    "agent_action": change.agent_action,
                    "created_at": change.created_at.isoformat()
                }
                for change in recent_changes
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting pricing analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve pricing analytics")

@router.get("/customer-service")
async def get_customer_service_analytics(
    days: int = Query(30, ge=1, le=365),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """Get customer service analytics"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Interaction metrics
        interaction_stats = db.query(
            func.count(CustomerInteraction.id).label('total_interactions'),
            func.sum(func.case([(CustomerInteraction.agent_handled == True, 1)], else_=0)).label('ai_handled'),
            func.sum(func.case([(CustomerInteraction.status == 'resolved', 1)], else_=0)).label('resolved'),
            func.avg(CustomerInteraction.satisfaction_score).label('avg_satisfaction')
        ).filter(
            CustomerInteraction.created_at >= start_date
        ).first()
        
        # Interaction types
        interaction_types = db.query(
            CustomerInteraction.interaction_type,
            func.count(CustomerInteraction.id).label('count')
        ).filter(
            CustomerInteraction.created_at >= start_date
        ).group_by(
            CustomerInteraction.interaction_type
        ).all()
        
        # Response times (mock data for now)
        avg_response_time = 2.5  # hours
        
        return {
            "period_days": days,
            "interaction_summary": {
                "total_interactions": int(interaction_stats.total_interactions or 0),
                "ai_handled_interactions": int(interaction_stats.ai_handled or 0),
                "resolved_interactions": int(interaction_stats.resolved or 0),
                "ai_automation_rate": round((int(interaction_stats.ai_handled or 0) / max(int(interaction_stats.total_interactions or 1), 1)) * 100, 2),
                "resolution_rate": round((int(interaction_stats.resolved or 0) / max(int(interaction_stats.total_interactions or 1), 1)) * 100, 2),
                "average_satisfaction": round(float(interaction_stats.avg_satisfaction or 0), 1)
            },
            "interaction_types": [
                {
                    "type": interaction.interaction_type,
                    "count": int(interaction.count)
                }
                for interaction in interaction_types
            ],
            "performance_metrics": {
                "average_response_time_hours": avg_response_time,
                "first_contact_resolution_rate": 78.5,  # Mock data
                "customer_satisfaction_score": round(float(interaction_stats.avg_satisfaction or 4.2), 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting customer service analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve customer service analytics")

@router.get("/ai-agents")
async def get_ai_agent_analytics(
    days: int = Query(30, ge=1, le=365),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """Get AI agent performance analytics"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Agent performance
        agent_stats = db.query(
            AgentLog.agent_name,
            func.count(AgentLog.id).label('total_executions'),
            func.sum(func.case([(AgentLog.result == 'success', 1)], else_=0)).label('successful_executions'),
            func.avg(AgentLog.execution_time).label('avg_execution_time')
        ).filter(
            AgentLog.created_at >= start_date
        ).group_by(
            AgentLog.agent_name
        ).all()
        
        # Action breakdown
        action_stats = db.query(
            AgentLog.action_type,
            func.count(AgentLog.id).label('count'),
            func.sum(func.case([(AgentLog.result == 'success', 1)], else_=0)).label('successful')
        ).filter(
            AgentLog.created_at >= start_date
        ).group_by(
            AgentLog.action_type
        ).all()
        
        return {
            "period_days": days,
            "agent_performance": [
                {
                    "agent_name": agent.agent_name,
                    "total_executions": int(agent.total_executions),
                    "successful_executions": int(agent.successful_executions),
                    "success_rate": round((int(agent.successful_executions) / max(int(agent.total_executions), 1)) * 100, 2),
                    "average_execution_time": round(float(agent.avg_execution_time or 0), 2)
                }
                for agent in agent_stats
            ],
            "action_breakdown": [
                {
                    "action_type": action.action_type,
                    "total_count": int(action.count),
                    "successful_count": int(action.successful),
                    "success_rate": round((int(action.successful) / max(int(action.count), 1)) * 100, 2)
                }
                for action in action_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting AI agent analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve AI agent analytics")
