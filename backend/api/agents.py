from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from backend.agents.base_agent import agent_coordinator
from backend.database.connection import get_database
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

class AgentExecutionRequest(BaseModel):
    agent_name: str
    context: Dict[str, Any] = {}
    auto_execute: bool = True

class AgentStatusResponse(BaseModel):
    name: str
    description: str
    is_active: bool
    last_execution: Optional[str]
    execution_count: int

class RecommendationRequest(BaseModel):
    user_id: int
    limit: int = 10

class CustomerInquiryRequest(BaseModel):
    user_id: int
    message: str
    interaction_type: str = "chat"

@router.get("/status", response_model=Dict[str, AgentStatusResponse])
async def get_all_agents_status():
    """Get status of all AI agents"""
    try:
        status = agent_coordinator.get_all_agents_status()
        return {
            name: AgentStatusResponse(**agent_status)
            for name, agent_status in status.items()
        }
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{agent_name}", response_model=AgentStatusResponse)
async def get_agent_status(agent_name: str):
    """Get status of a specific agent"""
    try:
        status = agent_coordinator.get_agent_status(agent_name)
        if not status:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        
        return AgentStatusResponse(**status)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute/{agent_name}")
async def execute_agent(agent_name: str, request: AgentExecutionRequest):
    """Execute a specific AI agent"""
    try:
        if agent_name not in agent_coordinator.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        
        result = await agent_coordinator.execute_agent(agent_name, request.context)
        return {
            "agent_name": agent_name,
            "execution_result": result,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-all")
async def execute_all_agents(context: Dict[str, Any] = {}):
    """Execute all active AI agents"""
    try:
        results = await agent_coordinator.execute_all_agents(context)
        return {
            "execution_results": results,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error executing all agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-parallel")
async def execute_agents_parallel(agent_names: List[str], context: Dict[str, Any] = {}):
    """Execute multiple agents in parallel"""
    try:
        results = await agent_coordinator.execute_agents_parallel(agent_names, context)
        return {
            "execution_results": results,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error executing agents in parallel: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activate/{agent_name}")
async def activate_agent(agent_name: str):
    """Activate a specific agent"""
    try:
        if agent_name not in agent_coordinator.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        
        agent_coordinator.agents[agent_name].activate()
        return {"message": f"Agent {agent_name} activated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating agent {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/deactivate/{agent_name}")
async def deactivate_agent(agent_name: str):
    """Deactivate a specific agent"""
    try:
        if agent_name not in agent_coordinator.agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        
        agent_coordinator.agents[agent_name].deactivate()
        return {"message": f"Agent {agent_name} deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating agent {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Specialized agent endpoints

@router.post("/inventory/check-stock")
async def check_inventory_status():
    """Check inventory status using the inventory agent"""
    try:
        result = await agent_coordinator.execute_agent("InventoryAgent", {
            "action": "check_stock",
            "auto_execute": False
        })
        return result
        
    except Exception as e:
        logger.error(f"Error checking inventory status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pricing/optimize")
async def optimize_pricing():
    """Run pricing optimization"""
    try:
        result = await agent_coordinator.execute_agent("PricingAgent", {
            "action": "optimize_prices",
            "auto_execute": False
        })
        return result
        
    except Exception as e:
        logger.error(f"Error optimizing pricing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations/generate", response_model=List[Dict[str, Any]])
async def generate_recommendations(request: RecommendationRequest):
    """Generate personalized recommendations for a user"""
    try:
        if "RecommendationAgent" not in agent_coordinator.agents:
            raise HTTPException(status_code=503, detail="Recommendation agent not available")
        
        recommendation_agent = agent_coordinator.agents["RecommendationAgent"]
        recommendations = await recommendation_agent.get_recommendations_for_user(
            request.user_id, request.limit
        )
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/customer-service/handle-inquiry")
async def handle_customer_inquiry(request: CustomerInquiryRequest):
    """Handle a customer inquiry using the customer service agent"""
    try:
        if "CustomerServiceAgent" not in agent_coordinator.agents:
            raise HTTPException(status_code=503, detail="Customer service agent not available")
        
        customer_service_agent = agent_coordinator.agents["CustomerServiceAgent"]
        result = await customer_service_agent.handle_customer_inquiry(
            request.user_id, request.message, request.interaction_type
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error handling customer inquiry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/agent-performance")
async def get_agent_performance_analytics(db: Session = Depends(get_database)):
    """Get analytics on agent performance"""
    try:
        # This would query the AgentLog table for performance metrics
        # For now, return mock data
        return {
            "total_executions": 150,
            "success_rate": 95.5,
            "average_execution_time": 2.3,
            "agent_breakdown": {
                "InventoryAgent": {
                    "executions": 45,
                    "success_rate": 98.0,
                    "avg_time": 1.8
                },
                "PricingAgent": {
                    "executions": 38,
                    "success_rate": 94.0,
                    "avg_time": 2.1
                },
                "CustomerServiceAgent": {
                    "executions": 42,
                    "success_rate": 96.0,
                    "avg_time": 2.8
                },
                "RecommendationAgent": {
                    "executions": 25,
                    "success_rate": 92.0,
                    "avg_time": 3.2
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting agent performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{agent_name}")
async def get_agent_logs(agent_name: str, limit: int = 50, db: Session = Depends(get_database)):
    """Get execution logs for a specific agent"""
    try:
        # This would query the AgentLog table
        # For now, return mock data
        return {
            "agent_name": agent_name,
            "logs": [
                {
                    "id": i,
                    "action_type": "execute",
                    "result": "success",
                    "execution_time": 2.1,
                    "created_at": "2024-01-01T00:00:00Z"
                }
                for i in range(1, min(limit + 1, 11))
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting agent logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
