from typing import Dict, Any, List
import asyncio
import logging
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from backend.agents.base_agent import BaseAgent
from backend.database.connection import get_db_connection
from backend.database.models import Product, InventoryLog
from backend.database.operations import ProductOperations, OrderOperations, InventoryLogOperations
from backend.config import settings
import json
import numpy as np

logger = logging.getLogger(__name__)

class InventoryManagementAgent(BaseAgent):
    """AI agent for automated inventory management"""
    
    def __init__(self):
        super().__init__(
            name="InventoryAgent",
            description="Manages inventory levels, predicts demand, and automates restocking"
        )
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.min_stock_threshold = 0.2  # Reorder when stock is 20% of max
        self.demand_prediction_days = 30
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method for inventory management"""
        results = {
            "low_stock_products": [],
            "reorder_suggestions": [],
            "demand_predictions": [],
            "inventory_adjustments": []
        }
        
        try:
            conn = get_db_connection()
            
            # Check for low stock products
            low_stock_products = await self._check_low_stock(conn)
            results["low_stock_products"] = low_stock_products
            
            # Generate reorder suggestions
            reorder_suggestions = await self._generate_reorder_suggestions(conn, low_stock_products)
            results["reorder_suggestions"] = reorder_suggestions
            
            # Predict demand for all products
            demand_predictions = await self._predict_demand(conn)
            results["demand_predictions"] = demand_predictions
            
            # Auto-execute reorders if enabled
            if context.get("auto_execute", True):
                adjustments = await self._execute_automatic_reorders(conn, reorder_suggestions)
                results["inventory_adjustments"] = adjustments
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Inventory agent execution error: {e}")
            raise
        
        return results
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze inventory data and provide insights"""
        try:
            conn = get_db_connection()
            
            # Analyze inventory turnover
            turnover_analysis = await self._analyze_inventory_turnover(conn)
            
            # Analyze seasonal patterns
            seasonal_analysis = await self._analyze_seasonal_patterns(conn)
            
            # Analyze stock-out risks
            stockout_risks = await self._analyze_stockout_risks(conn)
            
            conn.close()
            
            return {
                "turnover_analysis": turnover_analysis,
                "seasonal_analysis": seasonal_analysis,
                "stockout_risks": stockout_risks
            }
            
        except Exception as e:
            logger.error(f"Inventory analysis error: {e}")
            return {"error": str(e)}
    
    async def _check_low_stock(self, conn) -> List[Dict[str, Any]]:
        """Check for products with low stock levels"""
        low_stock_products = []
        
        try:
            # Query products where current stock is below minimum threshold
            products = ProductOperations.get_low_stock_products(conn)
            
            for product in products:
                stock_ratio = product.stock_quantity / max(product.max_stock_level, 1)
                
                low_stock_products.append({
                    "product_id": product.id,
                    "name": product.name,
                    "sku": product.sku,
                    "current_stock": product.stock_quantity,
                    "min_stock_level": product.min_stock_level,
                    "max_stock_level": product.max_stock_level,
                    "stock_ratio": stock_ratio,
                    "urgency": "critical" if stock_ratio < 0.1 else "high" if stock_ratio < 0.2 else "medium"
                })
            
        except Exception as e:
            logger.error(f"Error checking low stock: {e}")
        
        return low_stock_products
    
    async def _generate_reorder_suggestions(self, conn, low_stock_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate intelligent reorder suggestions"""
        suggestions = []
        
        try:
            for product_data in low_stock_products:
                product_id = product_data["product_id"]
                
                # Get historical sales data
                sales_history = await self._get_sales_history(conn, product_id)
                
                # Calculate optimal reorder quantity
                optimal_quantity = await self._calculate_optimal_reorder_quantity(
                    conn, product_id, sales_history
                )
                
                # Get AI-powered demand prediction
                demand_prediction = await self._get_ai_demand_prediction(
                    conn, product_id, sales_history
                )
                
                suggestions.append({
                    "product_id": product_id,
                    "current_stock": product_data["current_stock"],
                    "suggested_reorder_quantity": optimal_quantity,
                    "predicted_demand_30_days": demand_prediction,
                    "reorder_priority": product_data["urgency"],
                    "estimated_days_until_stockout": await self._calculate_days_until_stockout(
                        conn, product_id, sales_history
                    )
                })
                
        except Exception as e:
            logger.error(f"Error generating reorder suggestions: {e}")
        
        return suggestions
    
    async def _predict_demand(self, conn) -> List[Dict[str, Any]]:
        """Predict demand for all products using AI"""
        predictions = []
        
        try:
            # Get all active products using raw SQL since we're using connection instead of SQLAlchemy session
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM products WHERE is_active = TRUE")
            products = cursor.fetchall()
            
            for product_row in products:
                product_id, product_name = product_row
                # Get historical data
                sales_history = await self._get_sales_history(conn, product_id)
                
                # Calculate demand prediction
                if len(sales_history) >= 7:  # Need at least a week of data
                    prediction = await self._get_ai_demand_prediction(conn, product_id, sales_history)
                    
                    # Update product demand score
                    cursor.execute("UPDATE products SET demand_score = %s WHERE id = %s", (prediction, product_id))
                    
                    predictions.append({
                        "product_id": product_id,
                        "name": product_name,
                        "predicted_demand": prediction,
                        "confidence": min(len(sales_history) / 30, 1.0),  # Higher confidence with more data
                        "trend": await self._calculate_demand_trend(sales_history)
                    })
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error predicting demand: {e}")
        
        return predictions
    
    async def _execute_automatic_reorders(self, conn, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute automatic reorders for critical items"""
        adjustments = []
        
        try:
            for suggestion in suggestions:
                # Only auto-reorder critical items
                if suggestion["reorder_priority"] == "critical":
                    product_id = suggestion["product_id"]
                    reorder_quantity = suggestion["suggested_reorder_quantity"]
                    
                    # Get product using raw SQL
                    cursor = conn.cursor()
                    cursor.execute("SELECT name, stock_quantity FROM products WHERE id = %s", (product_id,))
                    product_result = cursor.fetchone()
                    if not product_result:
                        continue
                    
                    product_name, previous_quantity = product_result
                    new_quantity = previous_quantity + reorder_quantity
                    
                    # Update stock
                    cursor.execute("UPDATE products SET stock_quantity = %s WHERE id = %s", (new_quantity, product_id))
                    
                    # Log the change
                    cursor.execute("""
                        INSERT INTO inventory_logs (product_id, change_type, quantity_change, previous_quantity, new_quantity, reason, agent_action)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (product_id, "auto_restock", reorder_quantity, previous_quantity, new_quantity, "Automatic restock by AI agent", True))
                    
                    adjustments.append({
                        "product_id": product_id,
                        "product_name": product_name,
                        "quantity_added": reorder_quantity,
                        "previous_stock": previous_quantity,
                        "new_stock": new_quantity,
                        "action": "auto_restock"
                    })
                    
                    # Log the agent action
                    await self.log_action(
                        action_type="auto_restock",
                        target_id=product_id,
                        target_type="product",
                        action_data={
                            "quantity_added": reorder_quantity,
                            "previous_stock": previous_quantity,
                            "new_stock": new_quantity
                        }
                    )
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error executing automatic reorders: {e}")
            conn.rollback()
        
        return adjustments
    
    async def _get_sales_history(self, conn, product_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get sales history for a product"""
        try:
            return OrderOperations.get_sales_history(conn, product_id, days)
            
        except Exception as e:
            logger.error(f"Error getting sales history: {e}")
            return []
    
    async def _get_ai_demand_prediction(self, conn, product_id: int, sales_history: List[Dict[str, Any]]) -> float:
        """Use AI to predict demand for a product"""
        try:
            if not self.openai_client or not sales_history:
                # Fallback to simple moving average
                if sales_history:
                    recent_sales = [day["quantity_sold"] for day in sales_history[-7:]]
                    return sum(recent_sales) / len(recent_sales) * 30  # 30-day prediction
                return 0.0
            
            # Get product details using raw SQL
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.name, p.sku, p.current_price, p.seasonality_factor, c.name as category_name
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id 
                WHERE p.id = %s
            """, (product_id,))
            product_result = cursor.fetchone()
            if not product_result:
                return 0.0
            
            product_name, sku, current_price, seasonality_factor, category_name = product_result
            
            # Prepare data for AI analysis
            sales_data_str = json.dumps(sales_history[-30:])  # Last 30 days
            
            prompt = f"""
            Analyze the sales data for product "{product_name}" (SKU: {sku}) and predict the demand for the next 30 days.
            
            Historical sales data (last 30 days):
            {sales_data_str}
            
            Product details:
            - Current price: ${current_price}
            - Category: {category_name or 'Unknown'}
            - Seasonality factor: {seasonality_factor}
            
            Consider:
            1. Historical trends
            2. Seasonality patterns
            3. Price elasticity
            4. Market conditions
            
            Provide a single number representing the predicted quantity demand for the next 30 days.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100
            )
            
            # Extract numeric prediction from response
            prediction_text = response.choices[0].message.content.strip()
            
            # Try to extract number from response
            import re
            numbers = re.findall(r'\d+\.?\d*', prediction_text)
            if numbers:
                return float(numbers[0])
            
        except Exception as e:
            logger.error(f"Error getting AI demand prediction: {e}")
        
        # Fallback to simple calculation
        if sales_history:
            recent_sales = [day["quantity_sold"] for day in sales_history[-7:]]
            return sum(recent_sales) / len(recent_sales) * 30
        
        return 0.0
    
    async def _calculate_optimal_reorder_quantity(self, conn, product_id: int, sales_history: List[Dict[str, Any]]) -> int:
        """Calculate optimal reorder quantity using EOQ model"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT max_stock_level, stock_quantity FROM products WHERE id = %s", (product_id,))
            product_result = cursor.fetchone()
            if not product_result:
                return 0
            
            max_stock_level, stock_quantity = product_result
            
            # Calculate average daily demand
            if not sales_history:
                return max_stock_level - stock_quantity
            
            total_demand = sum(day["quantity_sold"] for day in sales_history)
            avg_daily_demand = total_demand / max(len(sales_history), 1)
            
            # Calculate demand variability (standard deviation)
            demands = [day["quantity_sold"] for day in sales_history]
            demand_std = np.std(demands) if len(demands) > 1 else 0
            
            # Safety stock calculation (to handle demand variability)
            lead_time_days = 7  # Assume 7 days lead time
            safety_stock = demand_std * np.sqrt(lead_time_days) * 1.65  # 95% service level
            
            # Reorder point
            reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
            
            # Optimal order quantity (simplified EOQ)
            # In a real system, you'd include ordering costs and holding costs
            target_stock = min(max_stock_level, avg_daily_demand * 60)  # 60 days supply
            current_stock = stock_quantity
            
            optimal_quantity = max(0, int(target_stock - current_stock))
            
            return optimal_quantity
            
        except Exception as e:
            logger.error(f"Error calculating optimal reorder quantity: {e}")
            return 0
    
    async def _calculate_days_until_stockout(self, conn, product_id: int, sales_history: List[Dict[str, Any]]) -> int:
        """Calculate estimated days until stockout"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT stock_quantity FROM products WHERE id = %s", (product_id,))
            product_result = cursor.fetchone()
            if not product_result or not sales_history:
                return 0
            
            stock_quantity = product_result[0]
            
            # Calculate average daily demand from recent history
            recent_sales = sales_history[-7:] if len(sales_history) >= 7 else sales_history
            total_demand = sum(day["quantity_sold"] for day in recent_sales)
            avg_daily_demand = total_demand / max(len(recent_sales), 1)
            
            if avg_daily_demand <= 0:
                return 999  # Very high number if no demand
            
            days_until_stockout = stock_quantity / avg_daily_demand
            return max(0, int(days_until_stockout))
            
        except Exception as e:
            logger.error(f"Error calculating days until stockout: {e}")
            return 0
    
    async def _calculate_demand_trend(self, sales_history: List[Dict[str, Any]]) -> str:
        """Calculate demand trend (increasing, decreasing, stable)"""
        try:
            if len(sales_history) < 7:
                return "insufficient_data"
            
            # Split data into two halves
            mid_point = len(sales_history) // 2
            first_half = sales_history[:mid_point]
            second_half = sales_history[mid_point:]
            
            avg_first = sum(day["quantity_sold"] for day in first_half) / len(first_half)
            avg_second = sum(day["quantity_sold"] for day in second_half) / len(second_half)
            
            change_ratio = (avg_second - avg_first) / max(avg_first, 1)
            
            if change_ratio > 0.2:
                return "increasing"
            elif change_ratio < -0.2:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating demand trend: {e}")
            return "unknown"
    
    async def _analyze_inventory_turnover(self, conn) -> Dict[str, Any]:
        """Analyze inventory turnover rates"""
        # Implementation for inventory turnover analysis
        # This would calculate turnover rates for different products/categories
        return {"message": "Inventory turnover analysis not implemented yet"}
    
    async def _analyze_seasonal_patterns(self, conn) -> Dict[str, Any]:
        """Analyze seasonal demand patterns"""
        # Implementation for seasonal pattern analysis
        return {"message": "Seasonal pattern analysis not implemented yet"}
    
    async def _analyze_stockout_risks(self, conn) -> Dict[str, Any]:
        """Analyze stockout risks across products"""
        # Implementation for stockout risk analysis
        return {"message": "Stockout risk analysis not implemented yet"}
