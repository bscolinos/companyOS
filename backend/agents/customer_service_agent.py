from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from backend.agents.base_agent import BaseAgent
from backend.database.connection import get_db_connection
from backend.config import settings
import json
import re

logger = logging.getLogger(__name__)

class CustomerServiceAgent(BaseAgent):
    """AI agent for automated customer service"""
    
    def __init__(self):
        super().__init__(
            name="CustomerServiceAgent",
            description="Handles customer inquiries, support tickets, and automated responses"
        )
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.auto_resolve_threshold = 0.8  # Auto-resolve tickets with 80%+ confidence
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method for customer service"""
        results = {
            "processed_interactions": [],
            "auto_resolved_tickets": [],
            "escalated_tickets": [],
            "customer_insights": {}
        }
        
        try:
            db = get_db_session()
            
            # Process pending customer interactions
            processed_interactions = await self._process_pending_interactions(db)
            results["processed_interactions"] = processed_interactions
            
            # Auto-resolve simple tickets
            auto_resolved = await self._auto_resolve_tickets(db)
            results["auto_resolved_tickets"] = auto_resolved
            
            # Identify tickets that need escalation
            escalated = await self._identify_escalation_tickets(db)
            results["escalated_tickets"] = escalated
            
            # Generate customer insights
            insights = await self._generate_customer_insights(db)
            results["customer_insights"] = insights
            
            db.close()
            
        except Exception as e:
            logger.error(f"Customer service agent execution error: {e}")
            raise
        
        return results
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer service data and provide insights"""
        try:
            db = get_db_session()
            
            # Analyze response times
            response_analysis = await self._analyze_response_times(db)
            
            # Analyze customer satisfaction
            satisfaction_analysis = await self._analyze_customer_satisfaction(db)
            
            # Analyze common issues
            issue_analysis = await self._analyze_common_issues(db)
            
            db.close()
            
            return {
                "response_times": response_analysis,
                "satisfaction_scores": satisfaction_analysis,
                "common_issues": issue_analysis
            }
            
        except Exception as e:
            logger.error(f"Customer service analysis error: {e}")
            return {"error": str(e)}
    
    async def handle_customer_inquiry(self, user_id: int, message: str, interaction_type: str = "chat") -> Dict[str, Any]:
        """Handle a specific customer inquiry"""
        try:
            db = get_db_session()
            
            # Create interaction record
            interaction = CustomerInteraction(
                user_id=user_id,
                interaction_type=interaction_type,
                message=message,
                status="open"
            )
            
            # Generate AI response
            ai_response = await self._generate_ai_response(db, user_id, message)
            
            if ai_response:
                interaction.response = ai_response["response"]
                interaction.agent_handled = True
                
                # Auto-resolve if confidence is high
                if ai_response["confidence"] >= self.auto_resolve_threshold:
                    interaction.status = "resolved"
                    interaction.resolved_at = datetime.utcnow()
                
            db.add(interaction)
            db.commit()
            
            # Log the action
            await self.log_action(
                action_type="handle_inquiry",
                target_id=interaction.id,
                target_type="customer_interaction",
                action_data={
                    "user_id": user_id,
                    "interaction_type": interaction_type,
                    "auto_resolved": interaction.status == "resolved",
                    "confidence": ai_response.get("confidence", 0) if ai_response else 0
                }
            )
            
            db.close()
            
            return {
                "interaction_id": interaction.id,
                "response": interaction.response,
                "status": interaction.status,
                "confidence": ai_response.get("confidence", 0) if ai_response else 0
            }
            
        except Exception as e:
            logger.error(f"Error handling customer inquiry: {e}")
            return {"error": str(e)}
    
    async def _process_pending_interactions(self, db: Session) -> List[Dict[str, Any]]:
        """Process pending customer interactions"""
        processed = []
        
        try:
            # Get open interactions without responses
            pending_interactions = db.query(CustomerInteraction).filter(
                and_(
                    CustomerInteraction.status == "open",
                    CustomerInteraction.response.is_(None)
                )
            ).limit(50).all()  # Process in batches
            
            for interaction in pending_interactions:
                try:
                    # Generate AI response
                    ai_response = await self._generate_ai_response(
                        db, interaction.user_id, interaction.message
                    )
                    
                    if ai_response:
                        interaction.response = ai_response["response"]
                        interaction.agent_handled = True
                        
                        # Auto-resolve if confidence is high
                        if ai_response["confidence"] >= self.auto_resolve_threshold:
                            interaction.status = "resolved"
                            interaction.resolved_at = datetime.utcnow()
                        else:
                            interaction.status = "in_progress"
                        
                        processed.append({
                            "interaction_id": interaction.id,
                            "user_id": interaction.user_id,
                            "message": interaction.message[:100] + "..." if len(interaction.message) > 100 else interaction.message,
                            "response": interaction.response[:100] + "..." if len(interaction.response) > 100 else interaction.response,
                            "status": interaction.status,
                            "confidence": ai_response["confidence"]
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing interaction {interaction.id}: {e}")
                    continue
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error processing pending interactions: {e}")
        
        return processed
    
    async def _generate_ai_response(self, db: Session, user_id: int, message: str) -> Optional[Dict[str, Any]]:
        """Generate AI response to customer message"""
        try:
            if not self.openai_client:
                return await self._generate_template_response(message)
            
            # Get user context
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            # Get user's recent orders
            recent_orders = db.query(Order).filter(
                and_(
                    Order.user_id == user_id,
                    Order.created_at >= datetime.utcnow() - timedelta(days=90)
                )
            ).order_by(desc(Order.created_at)).limit(5).all()
            
            # Build context
            user_context = {
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "recent_orders": [
                    {
                        "order_number": order.order_number,
                        "status": order.status,
                        "total": float(order.total_amount),
                        "date": order.created_at.isoformat()
                    }
                    for order in recent_orders
                ]
            }
            
            # Create prompt
            prompt = f"""
            You are a helpful customer service representative for an ecommerce platform. 
            Respond to the customer's message professionally and helpfully.
            
            Customer Information:
            - Name: {user_context['name']}
            - Email: {user_context['email']}
            - Recent Orders: {json.dumps(user_context['recent_orders'], indent=2)}
            
            Customer Message: "{message}"
            
            Guidelines:
            1. Be friendly and professional
            2. Use the customer's name if appropriate
            3. Reference their order history if relevant
            4. Provide specific, actionable help
            5. If you can't fully resolve the issue, explain next steps
            6. Keep response concise but complete
            
            Provide a JSON response with:
            {{
                "response": "<your response>",
                "confidence": <0-1 confidence score>,
                "category": "<inquiry category>",
                "requires_escalation": <true/false>
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                ai_data = json.loads(json_match.group())
                return {
                    "response": ai_data.get("response", "I apologize, but I'm having trouble processing your request right now."),
                    "confidence": min(max(ai_data.get("confidence", 0.5), 0), 1),
                    "category": ai_data.get("category", "general"),
                    "requires_escalation": ai_data.get("requires_escalation", False)
                }
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
        
        return await self._generate_template_response(message)
    
    async def _generate_template_response(self, message: str) -> Dict[str, Any]:
        """Generate template response when AI is not available"""
        message_lower = message.lower()
        
        # Simple keyword matching for common inquiries
        if any(word in message_lower for word in ["order", "status", "tracking"]):
            return {
                "response": "Thank you for your inquiry about your order. I'd be happy to help you check your order status. Could you please provide your order number?",
                "confidence": 0.6,
                "category": "order_inquiry",
                "requires_escalation": False
            }
        elif any(word in message_lower for word in ["return", "refund", "exchange"]):
            return {
                "response": "I understand you'd like to return or exchange an item. Our return policy allows returns within 30 days of purchase. Please provide your order number and I'll help you process the return.",
                "confidence": 0.7,
                "category": "return_request",
                "requires_escalation": False
            }
        elif any(word in message_lower for word in ["shipping", "delivery", "when will"]):
            return {
                "response": "I can help you with shipping information. Could you please provide your order number so I can check the delivery status and estimated arrival time?",
                "confidence": 0.6,
                "category": "shipping_inquiry",
                "requires_escalation": False
            }
        elif any(word in message_lower for word in ["cancel", "change order"]):
            return {
                "response": "I'll help you with your order modification request. Please provide your order number and let me know what changes you'd like to make.",
                "confidence": 0.5,
                "category": "order_modification",
                "requires_escalation": True
            }
        else:
            return {
                "response": "Thank you for contacting us. I've received your message and will make sure you get the help you need. A customer service representative will respond to you shortly.",
                "confidence": 0.3,
                "category": "general",
                "requires_escalation": True
            }
    
    async def _auto_resolve_tickets(self, db: Session) -> List[Dict[str, Any]]:
        """Auto-resolve tickets that meet criteria"""
        auto_resolved = []
        
        try:
            # Get tickets that can be auto-resolved
            resolvable_tickets = db.query(CustomerInteraction).filter(
                and_(
                    CustomerInteraction.status == "in_progress",
                    CustomerInteraction.agent_handled == True,
                    CustomerInteraction.response.isnot(None),
                    CustomerInteraction.created_at <= datetime.utcnow() - timedelta(hours=24)  # At least 24 hours old
                )
            ).limit(20).all()
            
            for ticket in resolvable_tickets:
                # Simple auto-resolution logic
                # In a real system, this would be more sophisticated
                if ticket.priority in ["low", "medium"]:
                    ticket.status = "resolved"
                    ticket.resolved_at = datetime.utcnow()
                    ticket.satisfaction_score = 4  # Assume good satisfaction for auto-resolved
                    
                    auto_resolved.append({
                        "interaction_id": ticket.id,
                        "user_id": ticket.user_id,
                        "subject": ticket.subject or "General Inquiry",
                        "resolution_time_hours": (datetime.utcnow() - ticket.created_at).total_seconds() / 3600
                    })
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error auto-resolving tickets: {e}")
        
        return auto_resolved
    
    async def _identify_escalation_tickets(self, db: Session) -> List[Dict[str, Any]]:
        """Identify tickets that need human escalation"""
        escalated = []
        
        try:
            # Get tickets that need escalation
            escalation_tickets = db.query(CustomerInteraction).filter(
                and_(
                    CustomerInteraction.status.in_(["open", "in_progress"]),
                    CustomerInteraction.created_at <= datetime.utcnow() - timedelta(hours=48)  # Open for 48+ hours
                )
            ).all()
            
            for ticket in escalation_tickets:
                # Check escalation criteria
                needs_escalation = (
                    ticket.priority == "urgent" or
                    (datetime.utcnow() - ticket.created_at).total_seconds() > 48 * 3600 or
                    "complaint" in (ticket.message or "").lower() or
                    "manager" in (ticket.message or "").lower()
                )
                
                if needs_escalation:
                    ticket.priority = "urgent"
                    
                    escalated.append({
                        "interaction_id": ticket.id,
                        "user_id": ticket.user_id,
                        "subject": ticket.subject or "Escalated Inquiry",
                        "priority": ticket.priority,
                        "open_duration_hours": (datetime.utcnow() - ticket.created_at).total_seconds() / 3600,
                        "reason": "Long response time or urgent keywords detected"
                    })
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error identifying escalation tickets: {e}")
        
        return escalated
    
    async def _generate_customer_insights(self, db: Session) -> Dict[str, Any]:
        """Generate insights about customer service performance"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # Get metrics
            total_interactions = db.query(CustomerInteraction).filter(
                CustomerInteraction.created_at >= start_date
            ).count()
            
            resolved_interactions = db.query(CustomerInteraction).filter(
                and_(
                    CustomerInteraction.created_at >= start_date,
                    CustomerInteraction.status == "resolved"
                )
            ).count()
            
            ai_handled = db.query(CustomerInteraction).filter(
                and_(
                    CustomerInteraction.created_at >= start_date,
                    CustomerInteraction.agent_handled == True
                )
            ).count()
            
            avg_satisfaction = db.query(func.avg(CustomerInteraction.satisfaction_score)).filter(
                and_(
                    CustomerInteraction.created_at >= start_date,
                    CustomerInteraction.satisfaction_score.isnot(None)
                )
            ).scalar() or 0
            
            # Calculate resolution rate
            resolution_rate = (resolved_interactions / max(total_interactions, 1)) * 100
            ai_automation_rate = (ai_handled / max(total_interactions, 1)) * 100
            
            return {
                "total_interactions": total_interactions,
                "resolution_rate_percent": round(resolution_rate, 2),
                "ai_automation_rate_percent": round(ai_automation_rate, 2),
                "average_satisfaction": round(avg_satisfaction, 2),
                "analysis_period_days": 30
            }
            
        except Exception as e:
            logger.error(f"Error generating customer insights: {e}")
            return {"error": str(e)}
    
    async def _analyze_response_times(self, db: Session) -> Dict[str, Any]:
        """Analyze customer service response times"""
        # Implementation for response time analysis
        return {"message": "Response time analysis not implemented yet"}
    
    async def _analyze_customer_satisfaction(self, db: Session) -> Dict[str, Any]:
        """Analyze customer satisfaction metrics"""
        # Implementation for satisfaction analysis
        return {"message": "Customer satisfaction analysis not implemented yet"}
    
    async def _analyze_common_issues(self, db: Session) -> Dict[str, Any]:
        """Analyze common customer issues"""
        # Implementation for issue analysis
        return {"message": "Common issues analysis not implemented yet"}
