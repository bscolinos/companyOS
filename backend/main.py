from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from backend.database.connection import init_database, test_connection
from backend.agents.base_agent import agent_coordinator
from backend.agents.inventory_agent import InventoryManagementAgent
from backend.agents.pricing_agent import PricingOptimizationAgent
from backend.agents.customer_service_agent import CustomerServiceAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.api import auth, products, orders, users, agents, analytics
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Ecommerce Platform...")
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Test database connection
    if not test_connection():
        logger.error("Database connection test failed")
        raise Exception("Database connection failed")
    
    # Initialize and register AI agents
    try:
        inventory_agent = InventoryManagementAgent()
        pricing_agent = PricingOptimizationAgent()
        customer_service_agent = CustomerServiceAgent()
        recommendation_agent = RecommendationAgent()
        
        agent_coordinator.register_agent(inventory_agent)
        agent_coordinator.register_agent(pricing_agent)
        agent_coordinator.register_agent(customer_service_agent)
        agent_coordinator.register_agent(recommendation_agent)
        
        await agent_coordinator.start_coordinator()
        logger.info("AI agents initialized and registered successfully")
        
    except Exception as e:
        logger.error(f"Agent initialization failed: {e}")
        raise
    
    # Start background tasks
    asyncio.create_task(start_background_tasks())
    
    logger.info("AI Ecommerce Platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Ecommerce Platform...")
    await agent_coordinator.stop_coordinator()
    logger.info("AI Ecommerce Platform shut down complete")

# Create FastAPI app
app = FastAPI(
    title="AI-Powered Ecommerce Platform",
    description="A fully automated ecommerce platform powered by AI agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(agents.router, prefix="/api/agents", tags=["AI Agents"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Powered Ecommerce Platform API",
        "version": "1.0.0",
        "status": "running",
        "agents_active": len(agent_coordinator.agents),
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = test_connection()
    agent_status = agent_coordinator.get_all_agents_status()
    
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "agents": {
            "total": len(agent_status),
            "active": sum(1 for agent in agent_status.values() if agent["is_active"]),
            "details": agent_status
        },
        "timestamp": "2024-01-01T00:00:00Z"  # Would use datetime.utcnow() in real app
    }

async def start_background_tasks():
    """Start background tasks for automated agent execution"""
    logger.info("Starting background tasks...")
    
    # Schedule periodic agent execution
    while True:
        try:
            # Run agents every 30 minutes
            await asyncio.sleep(30 * 60)  # 30 minutes
            
            # Execute all agents with empty context (automated execution)
            logger.info("Executing automated agent tasks...")
            results = await agent_coordinator.execute_all_agents({
                "auto_execute": True,
                "scheduled_run": True
            })
            
            # Log results
            for agent_name, result in results.items():
                if result["success"]:
                    logger.info(f"Agent {agent_name} executed successfully")
                else:
                    logger.error(f"Agent {agent_name} execution failed: {result.get('error')}")
                    
        except Exception as e:
            logger.error(f"Background task execution error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
