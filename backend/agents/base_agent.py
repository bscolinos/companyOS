from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import logging
from backend.database.connection import get_db_connection
from backend.database.models import AgentLog
from backend.database.operations import AgentLogOperations
import json
import time

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents in the ecommerce system"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.is_active = True
        self.last_execution = None
        self.execution_count = 0
        
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method for the agent"""
        pass
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data and provide insights"""
        pass
    
    async def log_action(self, 
                        action_type: str, 
                        target_id: Optional[int] = None,
                        target_type: Optional[str] = None,
                        action_data: Optional[Dict[str, Any]] = None,
                        result: str = "success",
                        error_message: Optional[str] = None,
                        execution_time: Optional[float] = None):
        """Log agent actions to database"""
        try:
            conn = get_db_connection()
            log_entry = AgentLog(
                agent_name=self.name,
                action_type=action_type,
                target_id=target_id,
                target_type=target_type,
                action_data=action_data or {},
                result=result,
                error_message=error_message,
                execution_time=execution_time
            )
            AgentLogOperations.create_log(conn, log_entry)
            conn.close()
        except Exception as e:
            logger.error(f"Error logging agent action: {e}")
    
    async def run_with_logging(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with automatic logging"""
        start_time = time.time()
        result = {"success": False, "data": {}, "error": None}
        
        try:
            if not self.is_active:
                result["error"] = "Agent is not active"
                return result
            
            # Execute the agent
            execution_result = await self.execute(context)
            result["success"] = True
            result["data"] = execution_result
            
            # Update execution stats
            self.last_execution = datetime.utcnow()
            self.execution_count += 1
            
            # Log successful execution
            execution_time = time.time() - start_time
            await self.log_action(
                action_type="execute",
                action_data={"context_keys": list(context.keys())},
                result="success",
                execution_time=execution_time
            )
            
        except Exception as e:
            result["error"] = str(e)
            execution_time = time.time() - start_time
            
            # Log failed execution
            await self.log_action(
                action_type="execute",
                action_data={"context_keys": list(context.keys())},
                result="failure",
                error_message=str(e),
                execution_time=execution_time
            )
            
            logger.error(f"Agent {self.name} execution failed: {e}")
        
        return result
    
    def activate(self):
        """Activate the agent"""
        self.is_active = True
        logger.info(f"Agent {self.name} activated")
    
    def deactivate(self):
        """Deactivate the agent"""
        self.is_active = False
        logger.info(f"Agent {self.name} deactivated")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count
        }

class AgentCoordinator:
    """Coordinates multiple agents and manages their execution"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_queue = asyncio.Queue()
        self.is_running = False
    
    def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def unregister_agent(self, agent_name: str):
        """Unregister an agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")
    
    async def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific agent"""
        if agent_name not in self.agents:
            return {"success": False, "error": f"Agent {agent_name} not found"}
        
        agent = self.agents[agent_name]
        return await agent.run_with_logging(context)
    
    async def execute_all_agents(self, context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Execute all active agents"""
        results = {}
        
        for agent_name, agent in self.agents.items():
            if agent.is_active:
                results[agent_name] = await agent.run_with_logging(context)
        
        return results
    
    async def execute_agents_parallel(self, agent_names: List[str], context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Execute multiple agents in parallel"""
        tasks = []
        
        for agent_name in agent_names:
            if agent_name in self.agents and self.agents[agent_name].is_active:
                task = self.execute_agent(agent_name, context)
                tasks.append((agent_name, task))
        
        results = {}
        if tasks:
            completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
            
            for (agent_name, _), result in zip(tasks, completed_tasks):
                if isinstance(result, Exception):
                    results[agent_name] = {"success": False, "error": str(result)}
                else:
                    results[agent_name] = result
        
        return results
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        if agent_name in self.agents:
            return self.agents[agent_name].get_status()
        return None
    
    def get_all_agents_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        return {name: agent.get_status() for name, agent in self.agents.items()}
    
    async def start_coordinator(self):
        """Start the agent coordinator"""
        self.is_running = True
        logger.info("Agent coordinator started")
        
        # Start background tasks for periodic agent execution
        await self._start_background_tasks()
    
    async def stop_coordinator(self):
        """Stop the agent coordinator"""
        self.is_running = False
        logger.info("Agent coordinator stopped")
    
    async def _start_background_tasks(self):
        """Start background tasks for automated agent execution"""
        # This would typically include scheduled tasks for different agents
        # For now, we'll implement basic periodic execution
        pass

# Global agent coordinator instance
agent_coordinator = AgentCoordinator()
