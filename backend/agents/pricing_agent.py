from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import httpx
from backend.agents.base_agent import BaseAgent
from backend.database.connection import get_db_connection
from backend.config import settings
import json
import numpy as np
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

class PricingOptimizationAgent(BaseAgent):
    """AI agent for dynamic pricing optimization"""
    
    def __init__(self):
        super().__init__(
            name="PricingAgent",
            description="Optimizes product pricing based on demand, competition, and market conditions"
        )
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.max_price_change_percent = 0.20  # Maximum 20% price change per adjustment
        self.min_profit_margin = 0.15  # Minimum 15% profit margin
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method for pricing optimization"""
        results = {
            "price_adjustments": [],
            "market_analysis": {},
            "demand_elasticity_updates": [],
            "profit_optimization": {}
        }
        
        try:
            conn = get_db_connection()
            
            # Analyze market conditions
            market_analysis = await self._analyze_market_conditions(conn)
            results["market_analysis"] = market_analysis
            
            # Calculate demand elasticity for products
            elasticity_updates = await self._calculate_demand_elasticity(conn)
            results["demand_elasticity_updates"] = elasticity_updates
            
            # Generate price optimization suggestions
            price_adjustments = await self._optimize_prices(conn, market_analysis)
            results["price_adjustments"] = price_adjustments
            
            # Auto-execute price changes if enabled
            if context.get("auto_execute", True):
                executed_changes = await self._execute_price_changes(conn, price_adjustments)
                results["executed_changes"] = executed_changes
            
            # Analyze profit optimization opportunities
            profit_analysis = await self._analyze_profit_optimization(conn)
            results["profit_optimization"] = profit_analysis
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Pricing agent execution error: {e}")
            raise
        
        return results
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pricing data and provide insights"""
        try:
            db = get_db_session()
            
            # Analyze price performance
            price_performance = await self._analyze_price_performance(db)
            
            # Analyze competitive positioning
            competitive_analysis = await self._analyze_competitive_positioning(db)
            
            # Analyze revenue impact
            revenue_impact = await self._analyze_revenue_impact(db)
            
            db.close()
            
            return {
                "price_performance": price_performance,
                "competitive_analysis": competitive_analysis,
                "revenue_impact": revenue_impact
            }
            
        except Exception as e:
            logger.error(f"Pricing analysis error: {e}")
            return {"error": str(e)}
    
    async def _analyze_market_conditions(self, db: Session) -> Dict[str, Any]:
        """Analyze current market conditions affecting pricing"""
        try:
            # Get overall sales trends
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            # Calculate total revenue and order trends
            revenue_data = db.query(
                func.date(Order.created_at).label('date'),
                func.sum(Order.total_amount).label('revenue'),
                func.count(Order.id).label('order_count'),
                func.avg(Order.total_amount).label('avg_order_value')
            ).filter(
                and_(
                    Order.created_at >= start_date,
                    Order.status.in_(['processing', 'shipped', 'delivered'])
                )
            ).group_by(
                func.date(Order.created_at)
            ).all()
            
            # Calculate market trends
            if len(revenue_data) >= 7:
                recent_week = revenue_data[-7:]
                previous_week = revenue_data[-14:-7] if len(revenue_data) >= 14 else revenue_data[:7]
                
                recent_avg_revenue = sum(day.revenue or 0 for day in recent_week) / len(recent_week)
                previous_avg_revenue = sum(day.revenue or 0 for day in previous_week) / len(previous_week)
                
                revenue_trend = ((recent_avg_revenue - previous_avg_revenue) / max(previous_avg_revenue, 1)) * 100
                
                recent_avg_orders = sum(day.order_count or 0 for day in recent_week) / len(recent_week)
                previous_avg_orders = sum(day.order_count or 0 for day in previous_week) / len(previous_week)
                
                order_trend = ((recent_avg_orders - previous_avg_orders) / max(previous_avg_orders, 1)) * 100
            else:
                revenue_trend = 0
                order_trend = 0
            
            # Get top-selling products
            top_products = db.query(
                Product.id,
                Product.name,
                Product.current_price,
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
                Product.id, Product.name, Product.current_price
            ).order_by(
                desc(func.sum(OrderItem.quantity))
            ).limit(10).all()
            
            return {
                "revenue_trend_percent": round(revenue_trend, 2),
                "order_trend_percent": round(order_trend, 2),
                "market_sentiment": "bullish" if revenue_trend > 5 else "bearish" if revenue_trend < -5 else "neutral",
                "top_selling_products": [
                    {
                        "product_id": product.id,
                        "name": product.name,
                        "current_price": float(product.current_price),
                        "units_sold": int(product.total_sold),
                        "revenue": float(product.total_revenue)
                    }
                    for product in top_products
                ],
                "analysis_period_days": 30
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market conditions: {e}")
            return {"error": str(e)}
    
    async def _calculate_demand_elasticity(self, db: Session) -> List[Dict[str, Any]]:
        """Calculate price elasticity of demand for products"""
        elasticity_updates = []
        
        try:
            # Get products with recent price changes
            products_with_price_history = db.query(Product).join(
                PriceHistory, Product.id == PriceHistory.product_id
            ).filter(
                PriceHistory.created_at >= datetime.utcnow() - timedelta(days=60)
            ).distinct().all()
            
            for product in products_with_price_history:
                elasticity = await self._calculate_product_elasticity(db, product.id)
                
                if elasticity is not None:
                    # Update product elasticity
                    product.price_elasticity = elasticity
                    
                    elasticity_updates.append({
                        "product_id": product.id,
                        "name": product.name,
                        "price_elasticity": elasticity,
                        "interpretation": self._interpret_elasticity(elasticity)
                    })
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error calculating demand elasticity: {e}")
        
        return elasticity_updates
    
    async def _calculate_product_elasticity(self, db: Session, product_id: int) -> Optional[float]:
        """Calculate price elasticity for a specific product"""
        try:
            # Get price history and corresponding sales data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=60)
            
            # Get price changes
            price_changes = db.query(PriceHistory).filter(
                and_(
                    PriceHistory.product_id == product_id,
                    PriceHistory.created_at >= start_date
                )
            ).order_by(PriceHistory.created_at).all()
            
            if len(price_changes) < 2:
                return None
            
            # Calculate elasticity for each price change period
            elasticities = []
            
            for i in range(1, len(price_changes)):
                prev_change = price_changes[i-1]
                curr_change = price_changes[i]
                
                # Get sales data for periods before and after price change
                period_before_start = prev_change.created_at
                period_before_end = curr_change.created_at
                period_after_start = curr_change.created_at
                period_after_end = min(period_after_start + timedelta(days=14), end_date)
                
                # Sales before price change
                sales_before = db.query(func.sum(OrderItem.quantity)).join(
                    Order, OrderItem.order_id == Order.id
                ).filter(
                    and_(
                        OrderItem.product_id == product_id,
                        Order.created_at >= period_before_start,
                        Order.created_at < period_before_end,
                        Order.status.in_(['processing', 'shipped', 'delivered'])
                    )
                ).scalar() or 0
                
                # Sales after price change
                sales_after = db.query(func.sum(OrderItem.quantity)).join(
                    Order, OrderItem.order_id == Order.id
                ).filter(
                    and_(
                        OrderItem.product_id == product_id,
                        Order.created_at >= period_after_start,
                        Order.created_at < period_after_end,
                        Order.status.in_(['processing', 'shipped', 'delivered'])
                    )
                ).scalar() or 0
                
                # Calculate elasticity
                if sales_before > 0 and prev_change.old_price > 0:
                    price_change_percent = (curr_change.new_price - prev_change.old_price) / prev_change.old_price
                    demand_change_percent = (sales_after - sales_before) / sales_before
                    
                    if price_change_percent != 0:
                        elasticity = demand_change_percent / price_change_percent
                        elasticities.append(elasticity)
            
            # Return average elasticity
            if elasticities:
                return sum(elasticities) / len(elasticities)
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating product elasticity: {e}")
            return None
    
    def _interpret_elasticity(self, elasticity: float) -> str:
        """Interpret price elasticity value"""
        if elasticity < -1:
            return "elastic"  # Demand is sensitive to price changes
        elif elasticity > -1 and elasticity < 0:
            return "inelastic"  # Demand is less sensitive to price changes
        elif elasticity > 0:
            return "giffen_good"  # Unusual case where higher price increases demand
        else:
            return "perfectly_inelastic"  # Demand doesn't change with price
    
    async def _optimize_prices(self, db: Session, market_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimal pricing suggestions"""
        price_adjustments = []
        
        try:
            # Get all active products
            products = db.query(Product).filter(Product.is_active == True).all()
            
            for product in products:
                optimization = await self._calculate_optimal_price(db, product, market_analysis)
                
                if optimization and optimization["suggested_price"] != product.current_price:
                    price_adjustments.append({
                        "product_id": product.id,
                        "name": product.name,
                        "current_price": float(product.current_price),
                        "suggested_price": optimization["suggested_price"],
                        "price_change_percent": optimization["price_change_percent"],
                        "expected_impact": optimization["expected_impact"],
                        "reasoning": optimization["reasoning"],
                        "confidence": optimization["confidence"]
                    })
            
        except Exception as e:
            logger.error(f"Error optimizing prices: {e}")
        
        return price_adjustments
    
    async def _calculate_optimal_price(self, db: Session, product: Product, market_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate optimal price for a specific product"""
        try:
            # Get recent sales data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=30)
            
            sales_data = db.query(
                func.sum(OrderItem.quantity).label('total_sold'),
                func.avg(OrderItem.unit_price).label('avg_selling_price'),
                func.count(OrderItem.id).label('order_count')
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                and_(
                    OrderItem.product_id == product.id,
                    Order.created_at >= start_date,
                    Order.status.in_(['processing', 'shipped', 'delivered'])
                )
            ).first()
            
            if not sales_data or not sales_data.total_sold:
                return None
            
            # Calculate current performance metrics
            current_demand = float(sales_data.total_sold)
            current_price = float(product.current_price)
            cost_price = float(product.cost_price) if product.cost_price else current_price * 0.6
            
            # Use AI to determine optimal price if available
            if self.openai_client:
                ai_suggestion = await self._get_ai_price_suggestion(
                    product, sales_data, market_analysis
                )
                if ai_suggestion:
                    return ai_suggestion
            
            # Fallback to mathematical optimization
            return await self._mathematical_price_optimization(
                product, current_demand, current_price, cost_price, market_analysis
            )
            
        except Exception as e:
            logger.error(f"Error calculating optimal price for product {product.id}: {e}")
            return None
    
    async def _get_ai_price_suggestion(self, product: Product, sales_data, market_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get AI-powered price suggestion"""
        try:
            # Prepare context for AI
            context = {
                "product_name": product.name,
                "current_price": float(product.current_price),
                "cost_price": float(product.cost_price) if product.cost_price else None,
                "stock_quantity": product.stock_quantity,
                "demand_score": product.demand_score,
                "price_elasticity": product.price_elasticity,
                "recent_sales": {
                    "total_sold": int(sales_data.total_sold),
                    "avg_selling_price": float(sales_data.avg_selling_price or 0),
                    "order_count": int(sales_data.order_count)
                },
                "market_conditions": market_analysis
            }
            
            prompt = f"""
            As a pricing optimization AI, analyze the following product data and suggest an optimal price:
            
            Product: {product.name}
            Current Price: ${product.current_price}
            Cost Price: ${product.cost_price or 'Unknown'}
            Stock Level: {product.stock_quantity} units
            Recent Sales (30 days): {sales_data.total_sold} units sold
            Price Elasticity: {product.price_elasticity}
            
            Market Conditions:
            - Revenue Trend: {market_analysis.get('revenue_trend_percent', 0)}%
            - Market Sentiment: {market_analysis.get('market_sentiment', 'neutral')}
            
            Consider:
            1. Profit maximization
            2. Market demand
            3. Competitive positioning
            4. Inventory levels
            5. Price elasticity
            
            Provide a JSON response with:
            {{
                "suggested_price": <number>,
                "reasoning": "<explanation>",
                "confidence": <0-1>,
                "expected_impact": "<positive/negative/neutral>"
            }}
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse AI response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                ai_data = json.loads(json_match.group())
                
                suggested_price = float(ai_data["suggested_price"])
                current_price = float(product.current_price)
                
                # Validate suggested price
                price_change_percent = ((suggested_price - current_price) / current_price) * 100
                
                # Apply safety limits
                if abs(price_change_percent) > self.max_price_change_percent * 100:
                    # Limit price change
                    if price_change_percent > 0:
                        suggested_price = current_price * (1 + self.max_price_change_percent)
                    else:
                        suggested_price = current_price * (1 - self.max_price_change_percent)
                    price_change_percent = ((suggested_price - current_price) / current_price) * 100
                
                # Ensure minimum profit margin
                min_price = float(product.cost_price or current_price * 0.6) * (1 + self.min_profit_margin)
                if suggested_price < min_price:
                    suggested_price = min_price
                    price_change_percent = ((suggested_price - current_price) / current_price) * 100
                
                return {
                    "suggested_price": round(suggested_price, 2),
                    "price_change_percent": round(price_change_percent, 2),
                    "reasoning": ai_data.get("reasoning", "AI optimization"),
                    "confidence": min(ai_data.get("confidence", 0.5), 1.0),
                    "expected_impact": ai_data.get("expected_impact", "neutral")
                }
            
        except Exception as e:
            logger.error(f"Error getting AI price suggestion: {e}")
        
        return None
    
    async def _mathematical_price_optimization(self, product: Product, current_demand: float, 
                                             current_price: float, cost_price: float, 
                                             market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Mathematical price optimization fallback"""
        try:
            # Simple profit maximization model
            elasticity = product.price_elasticity or -1.5  # Default elasticity
            
            # Calculate optimal price using elasticity
            if elasticity < 0 and elasticity != -1:
                # Optimal price = (elasticity * cost_price) / (elasticity + 1)
                optimal_price = (elasticity * cost_price) / (elasticity + 1)
            else:
                # Fallback to cost-plus pricing with market adjustment
                markup = 0.5  # 50% markup
                market_multiplier = 1.0
                
                if market_analysis.get("market_sentiment") == "bullish":
                    market_multiplier = 1.1
                elif market_analysis.get("market_sentiment") == "bearish":
                    market_multiplier = 0.95
                
                optimal_price = cost_price * (1 + markup) * market_multiplier
            
            # Apply constraints
            optimal_price = max(optimal_price, cost_price * (1 + self.min_profit_margin))
            
            # Limit price change
            max_change = current_price * self.max_price_change_percent
            if optimal_price > current_price + max_change:
                optimal_price = current_price + max_change
            elif optimal_price < current_price - max_change:
                optimal_price = current_price - max_change
            
            price_change_percent = ((optimal_price - current_price) / current_price) * 100
            
            return {
                "suggested_price": round(optimal_price, 2),
                "price_change_percent": round(price_change_percent, 2),
                "reasoning": "Mathematical optimization based on elasticity and market conditions",
                "confidence": 0.7,
                "expected_impact": "positive" if price_change_percent > 0 else "negative" if price_change_percent < 0 else "neutral"
            }
            
        except Exception as e:
            logger.error(f"Error in mathematical price optimization: {e}")
            return {
                "suggested_price": current_price,
                "price_change_percent": 0,
                "reasoning": "No change recommended due to calculation error",
                "confidence": 0.1,
                "expected_impact": "neutral"
            }
    
    async def _execute_price_changes(self, db: Session, price_adjustments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute automatic price changes for high-confidence suggestions"""
        executed_changes = []
        
        try:
            for adjustment in price_adjustments:
                # Only auto-execute high-confidence, small changes
                if (adjustment["confidence"] >= 0.8 and 
                    abs(adjustment["price_change_percent"]) <= 10):  # Max 10% auto change
                    
                    product_id = adjustment["product_id"]
                    new_price = adjustment["suggested_price"]
                    
                    # Get product
                    product = db.query(Product).filter(Product.id == product_id).first()
                    if not product:
                        continue
                    
                    # Record price history
                    price_history = PriceHistory(
                        product_id=product_id,
                        old_price=product.current_price,
                        new_price=new_price,
                        change_reason=f"AI optimization: {adjustment['reasoning']}",
                        agent_action=True,
                        market_data={
                            "confidence": adjustment["confidence"],
                            "expected_impact": adjustment["expected_impact"]
                        }
                    )
                    
                    # Update product price
                    product.current_price = new_price
                    
                    db.add(price_history)
                    
                    executed_changes.append({
                        "product_id": product_id,
                        "product_name": product.name,
                        "old_price": float(price_history.old_price),
                        "new_price": new_price,
                        "change_percent": adjustment["price_change_percent"],
                        "reasoning": adjustment["reasoning"]
                    })
                    
                    # Log the agent action
                    await self.log_action(
                        action_type="price_update",
                        target_id=product_id,
                        target_type="product",
                        action_data={
                            "old_price": float(price_history.old_price),
                            "new_price": new_price,
                            "change_percent": adjustment["price_change_percent"],
                            "confidence": adjustment["confidence"]
                        }
                    )
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error executing price changes: {e}")
            db.rollback()
        
        return executed_changes
    
    async def _analyze_profit_optimization(self, db: Session) -> Dict[str, Any]:
        """Analyze profit optimization opportunities"""
        # Implementation for profit analysis
        return {"message": "Profit optimization analysis not implemented yet"}
    
    async def _analyze_price_performance(self, db: Session) -> Dict[str, Any]:
        """Analyze price change performance"""
        # Implementation for price performance analysis
        return {"message": "Price performance analysis not implemented yet"}
    
    async def _analyze_competitive_positioning(self, db: Session) -> Dict[str, Any]:
        """Analyze competitive price positioning"""
        # Implementation for competitive analysis
        return {"message": "Competitive positioning analysis not implemented yet"}
    
    async def _analyze_revenue_impact(self, db: Session) -> Dict[str, Any]:
        """Analyze revenue impact of price changes"""
        # Implementation for revenue impact analysis
        return {"message": "Revenue impact analysis not implemented yet"}
