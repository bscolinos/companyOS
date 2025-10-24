from typing import Dict, Any, List, Optional, Tuple
import asyncio
import logging
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import numpy as np
from agents.base_agent import BaseAgent
from database.connection import get_db_connection
from database.models import User, Product, Order, OrderItem, CartItem, Review, Category
from database.operations import UserOperations, ProductOperations, OrderOperations, CartOperations, DatabaseOperations
from config import settings
import json
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class RecommendationAgent(BaseAgent):
    """AI agent for personalized product recommendations"""
    
    def __init__(self):
        super().__init__(
            name="RecommendationAgent",
            description="Provides personalized product recommendations and cross-selling suggestions"
        )
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.min_recommendation_score = 0.3  # Minimum score to recommend a product
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method for recommendation generation"""
        results = {
            "user_recommendations": [],
            "cross_sell_opportunities": [],
            "trending_products": [],
            "recommendation_performance": {}
        }
        
        try:
            conn = get_db_connection()
            
            # Generate recommendations for active users
            if context.get("user_id"):
                # Single user recommendation
                user_recs = await self._generate_user_recommendations(conn, context["user_id"])
                results["user_recommendations"] = [user_recs]
            else:
                # Batch recommendations for recent users
                user_recs = await self._generate_batch_recommendations(conn)
                results["user_recommendations"] = user_recs
            
            # Identify cross-selling opportunities
            cross_sell = await self._identify_cross_sell_opportunities(conn)
            results["cross_sell_opportunities"] = cross_sell
            
            # Update trending products
            trending = await self._update_trending_products(conn)
            results["trending_products"] = trending
            
            # Analyze recommendation performance
            performance = await self._analyze_recommendation_performance(conn)
            results["recommendation_performance"] = performance
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Recommendation agent execution error: {e}")
            raise
        
        return results
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze recommendation data and provide insights"""
        try:
            conn = get_db_connection()
            
            # Analyze recommendation accuracy
            accuracy_analysis = await self._analyze_recommendation_accuracy(conn)
            
            # Analyze user engagement with recommendations
            engagement_analysis = await self._analyze_recommendation_engagement(conn)
            
            # Analyze product affinity patterns
            affinity_analysis = await self._analyze_product_affinity(conn)
            
            conn.close()
            
            return {
                "accuracy_metrics": accuracy_analysis,
                "engagement_metrics": engagement_analysis,
                "affinity_patterns": affinity_analysis
            }
            
        except Exception as e:
            logger.error(f"Recommendation analysis error: {e}")
            return {"error": str(e)}
    
    async def get_recommendations_for_user(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a specific user"""
        try:
            conn = get_db_connection()
            recommendations = await self._generate_user_recommendations(conn, user_id, limit)
            conn.close()
            return recommendations.get("recommendations", [])
        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {e}")
            return []
    
    async def _generate_user_recommendations(self, conn, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """Generate personalized recommendations for a user"""
        try:
            user = UserOperations.get_user_by_id(conn, user_id)
            if not user:
                return {"user_id": user_id, "recommendations": [], "error": "User not found"}
            
            # Get user's purchase history
            user_orders = await self._get_user_purchase_history(conn, user_id)
            
            # Get user's browsing behavior (cart items, reviews)
            user_behavior = await self._get_user_behavior(conn, user_id)
            
            # Generate recommendations using multiple algorithms
            collaborative_recs = await self._collaborative_filtering(conn, user_id, user_orders)
            content_based_recs = await self._content_based_filtering(conn, user_orders, user_behavior)
            ai_powered_recs = await self._ai_powered_recommendations(conn, user_id, user_orders, user_behavior)
            
            # Combine and rank recommendations
            combined_recs = await self._combine_recommendations([
                ("collaborative", collaborative_recs),
                ("content_based", content_based_recs),
                ("ai_powered", ai_powered_recs)
            ])
            
            # Filter and limit results
            final_recommendations = await self._filter_and_rank_recommendations(
                conn, user_id, combined_recs, limit
            )
            
            # Log the recommendation generation
            await self.log_action(
                action_type="generate_recommendations",
                target_id=user_id,
                target_type="user",
                action_data={
                    "recommendation_count": len(final_recommendations),
                    "algorithms_used": ["collaborative", "content_based", "ai_powered"]
                }
            )
            
            return {
                "user_id": user_id,
                "recommendations": final_recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return {"user_id": user_id, "recommendations": [], "error": str(e)}
    
    async def _generate_batch_recommendations(self, conn, limit_users: int = 100) -> List[Dict[str, Any]]:
        """Generate recommendations for multiple users"""
        batch_recommendations = []
        
        try:
            # Get recently active users
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT u.id 
                FROM users u
                JOIN orders o ON u.id = o.user_id
                WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                LIMIT %s
            """, (limit_users,))
            
            active_users = cursor.fetchall()
            
            for user_row in active_users:
                user_id = user_row[0]
                user_recs = await self._generate_user_recommendations(conn, user_id, 5)
                batch_recommendations.append(user_recs)
            
        except Exception as e:
            logger.error(f"Error generating batch recommendations: {e}")
        
        return batch_recommendations
    
    async def _get_user_purchase_history(self, conn, user_id: int) -> List[Dict[str, Any]]:
        """Get user's purchase history"""
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT oi.product_id, oi.quantity, oi.unit_price, o.created_at, o.id
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE o.user_id = %s AND o.status IN ('processing', 'shipped', 'delivered')
                ORDER BY o.created_at DESC
            """, (user_id,))
            
            purchase_history = []
            for row in cursor.fetchall():
                purchase_history.append({
                    "product_id": row[0],
                    "quantity": row[1],
                    "price": float(row[2]),
                    "order_date": row[3].isoformat() if row[3] else None,
                    "order_id": row[4]
                })
            
            return purchase_history
            
        except Exception as e:
            logger.error(f"Error getting purchase history for user {user_id}: {e}")
            return []
    
    async def _get_user_behavior(self, conn, user_id: int) -> Dict[str, Any]:
        """Get user's browsing and interaction behavior"""
        try:
            cursor = conn.cursor()
            
            # Get cart items (shows interest)
            cursor.execute("""
                SELECT product_id, quantity, created_at
                FROM cart_items
                WHERE user_id = %s
            """, (user_id,))
            cart_rows = cursor.fetchall()
            
            # Get reviews (shows preferences)
            cursor.execute("""
                SELECT product_id, rating, sentiment_score, created_at
                FROM reviews
                WHERE user_id = %s
            """, (user_id,))
            review_rows = cursor.fetchall()
            
            return {
                "cart_items": [
                    {
                        "product_id": row[0],
                        "quantity": row[1],
                        "added_at": row[2].isoformat() if row[2] else None
                    }
                    for row in cart_rows
                ],
                "reviews": [
                    {
                        "product_id": row[0],
                        "rating": row[1],
                        "sentiment_score": row[2] or 0,
                        "created_at": row[3].isoformat() if row[3] else None
                    }
                    for row in review_rows
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user behavior for user {user_id}: {e}")
            return {"cart_items": [], "reviews": []}
    
    async def _collaborative_filtering(self, conn, user_id: int, user_orders: List[Dict[str, Any]]) -> List[Tuple[int, float]]:
        """Collaborative filtering recommendations"""
        try:
            if not user_orders:
                return []
            
            # Get products the user has purchased
            user_products = set(order["product_id"] for order in user_orders)
            user_product_list = list(user_products)
            
            if not user_product_list:
                return []
            
            cursor = conn.cursor()
            
            # Find similar users (users who bought similar products)
            placeholders = ','.join(['%s'] * len(user_product_list))
            cursor.execute(f"""
                SELECT oi.order_id, COUNT(oi.product_id) as common_products
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.id
                WHERE oi.product_id IN ({placeholders})
                  AND o.user_id != %s
                  AND o.status IN ('processing', 'shipped', 'delivered')
                GROUP BY oi.order_id
                HAVING COUNT(oi.product_id) >= 2
                ORDER BY common_products DESC
                LIMIT 50
            """, user_product_list + [user_id])
            
            similar_order_ids = [row[0] for row in cursor.fetchall()]
            
            if not similar_order_ids:
                return []
            
            # Get products bought by similar users that current user hasn't bought
            order_placeholders = ','.join(['%s'] * len(similar_order_ids))
            product_placeholders = ','.join(['%s'] * len(user_product_list))
            
            cursor.execute(f"""
                SELECT oi.product_id, COUNT(oi.product_id) as frequency, AVG(oi.unit_price) as avg_price
                FROM order_items oi
                WHERE oi.order_id IN ({order_placeholders})
                  AND oi.product_id NOT IN ({product_placeholders})
                GROUP BY oi.product_id
                ORDER BY frequency DESC
                LIMIT 20
            """, similar_order_ids + user_product_list)
            
            recommended_products = cursor.fetchall()
            
            # Calculate recommendation scores
            recommendations = []
            max_frequency = max([prod[1] for prod in recommended_products], default=1)
            
            for product in recommended_products:
                # Score based on frequency among similar users
                score = product[1] / max_frequency
                recommendations.append((product[0], score))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in collaborative filtering: {e}")
            return []
    
    async def _content_based_filtering(self, conn, user_orders: List[Dict[str, Any]], user_behavior: Dict[str, Any]) -> List[Tuple[int, float]]:
        """Content-based filtering recommendations"""
        try:
            if not user_orders and not user_behavior["cart_items"]:
                return []
            
            # Get categories and attributes of products user has interacted with
            interested_product_ids = set()
            
            # From purchase history
            for order in user_orders:
                interested_product_ids.add(order["product_id"])
            
            # From cart items
            for item in user_behavior["cart_items"]:
                interested_product_ids.add(item["product_id"])
            
            if not interested_product_ids:
                return []
            
            cursor = conn.cursor()
            
            # Get products user has interacted with
            interested_product_list = list(interested_product_ids)
            placeholders = ','.join(['%s'] * len(interested_product_list))
            cursor.execute(f"""
                SELECT id, category_id, tags, current_price
                FROM products
                WHERE id IN ({placeholders})
            """, interested_product_list)
            
            interested_products = cursor.fetchall()
            
            # Extract categories and tags
            preferred_categories = set()
            preferred_tags = set()
            
            for product in interested_products:
                if product[1]:  # category_id
                    preferred_categories.add(product[1])
                
                if product[2]:  # tags
                    tags = DatabaseOperations.json_to_list(product[2]) if isinstance(product[2], str) else product[2]
                    if tags:
                        preferred_tags.update(tags)
            
            # Find similar products
            category_conditions = []
            params = []
            
            if preferred_categories:
                category_placeholders = ','.join(['%s'] * len(preferred_categories))
                category_conditions.append(f"category_id IN ({category_placeholders})")
                params.extend(list(preferred_categories))
            
            # Exclude already interacted products
            product_placeholders = ','.join(['%s'] * len(interested_product_list))
            params.extend(interested_product_list)
            
            where_clause = " OR ".join(category_conditions) if category_conditions else "1=0"
            
            cursor.execute(f"""
                SELECT id, category_id, tags, current_price
                FROM products
                WHERE is_active = 1 
                  AND id NOT IN ({product_placeholders})
                  AND ({where_clause})
                LIMIT 30
            """, params)
            
            similar_products = cursor.fetchall()
            
            # Calculate similarity scores
            recommendations = []
            user_avg_price = sum(order["price"] for order in user_orders) / len(user_orders) if user_orders else 0
            
            for product in similar_products:
                score = 0.0
                product_id, category_id, tags_json, current_price = product
                
                # Category similarity
                if category_id in preferred_categories:
                    score += 0.7
                
                # Tag similarity
                if tags_json and preferred_tags:
                    product_tags = DatabaseOperations.json_to_list(tags_json) if isinstance(tags_json, str) else tags_json
                    if product_tags:
                        common_tags = set(product_tags) & preferred_tags
                        if common_tags:
                            score += 0.3 * (len(common_tags) / len(preferred_tags))
                
                # Price range similarity
                if user_avg_price > 0:
                    price_diff = abs(float(current_price) - user_avg_price) / user_avg_price
                    if price_diff < 0.5:  # Within 50% of average price
                        score += 0.2
                
                if score > self.min_recommendation_score:
                    recommendations.append((product_id, score))
            
            return sorted(recommendations, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"Error in content-based filtering: {e}")
            return []
    
    async def _ai_powered_recommendations(self, conn, user_id: int, user_orders: List[Dict[str, Any]], user_behavior: Dict[str, Any]) -> List[Tuple[int, float]]:
        """AI-powered recommendations using OpenAI"""
        try:
            if not self.openai_client:
                return []
            
            # Get user profile
            user = UserOperations.get_user_by_id(conn, user_id)
            if not user:
                return []
            
            cursor = conn.cursor()
            
            # Get top products for recommendation
            cursor.execute("""
                SELECT p.id, p.name, p.current_price, p.demand_score, p.tags, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = 1
                ORDER BY p.demand_score DESC
                LIMIT 50
            """)
            
            top_products = cursor.fetchall()
            
            # Prepare context for AI
            user_context = {
                "purchase_history": user_orders[-10:],  # Last 10 purchases
                "cart_items": user_behavior["cart_items"],
                "reviews": user_behavior["reviews"][-5:],  # Last 5 reviews
            }
            
            products_context = []
            for product in top_products[:20]:  # Limit for AI processing
                product_id, name, current_price, demand_score, tags_json, category_name = product
                tags = DatabaseOperations.json_to_list(tags_json) if tags_json else []
                
                products_context.append({
                    "id": product_id,
                    "name": name,
                    "price": float(current_price),
                    "category": category_name or "Unknown",
                    "demand_score": demand_score,
                    "tags": tags
                })
            
            prompt = f"""
            Analyze the user's behavior and recommend products from the available list.
            
            User Behavior:
            {json.dumps(user_context, indent=2)}
            
            Available Products:
            {json.dumps(products_context, indent=2)}
            
            Provide recommendations based on:
            1. Purchase patterns
            2. Price preferences
            3. Category interests
            4. Review sentiments
            5. Current trends
            
            Return a JSON array of recommended product IDs with scores (0-1):
            [
                {{"product_id": 123, "score": 0.8, "reason": "matches purchase history"}},
                ...
            ]
            
            Limit to top 10 recommendations.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            
            # Parse AI response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON array
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                ai_recommendations = json.loads(json_match.group())
                return [
                    (rec["product_id"], min(max(rec["score"], 0), 1))
                    for rec in ai_recommendations
                    if isinstance(rec.get("product_id"), int) and isinstance(rec.get("score"), (int, float))
                ]
            
        except Exception as e:
            logger.error(f"Error in AI-powered recommendations: {e}")
        
        return []
    
    async def _combine_recommendations(self, algorithm_results: List[Tuple[str, List[Tuple[int, float]]]]) -> List[Tuple[int, float]]:
        """Combine recommendations from multiple algorithms"""
        try:
            # Weight different algorithms
            algorithm_weights = {
                "collaborative": 0.4,
                "content_based": 0.3,
                "ai_powered": 0.3
            }
            
            combined_scores = defaultdict(float)
            
            for algorithm_name, recommendations in algorithm_results:
                weight = algorithm_weights.get(algorithm_name, 0.33)
                
                for product_id, score in recommendations:
                    combined_scores[product_id] += score * weight
            
            # Sort by combined score
            return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"Error combining recommendations: {e}")
            return []
    
    async def _filter_and_rank_recommendations(self, conn, user_id: int, recommendations: List[Tuple[int, float]], limit: int) -> List[Dict[str, Any]]:
        """Filter and rank final recommendations"""
        try:
            if not recommendations:
                return []
            
            # Get product details
            product_ids = [rec[0] for rec in recommendations[:limit * 2]]  # Get more to filter
            
            if not product_ids:
                return []
            
            cursor = conn.cursor()
            placeholders = ','.join(['%s'] * len(product_ids))
            cursor.execute(f"""
                SELECT p.id, p.name, p.current_price, p.stock_quantity, p.is_featured, 
                       p.images, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id IN ({placeholders})
                  AND p.is_active = 1
                  AND p.stock_quantity > 0
            """, product_ids)
            
            products = cursor.fetchall()
            
            # Create product lookup
            product_lookup = {}
            for product in products:
                product_id, name, current_price, stock_quantity, is_featured, images_json, category_name = product
                images = DatabaseOperations.json_to_list(images_json) if images_json else []
                
                product_lookup[product_id] = {
                    "id": product_id,
                    "name": name,
                    "current_price": current_price,
                    "stock_quantity": stock_quantity,
                    "is_featured": is_featured,
                    "images": images,
                    "category_name": category_name
                }
            
            # Filter and format recommendations
            final_recommendations = []
            
            for product_id, score in recommendations:
                if len(final_recommendations) >= limit:
                    break
                
                if product_id not in product_lookup:
                    continue
                
                product = product_lookup[product_id]
                
                final_recommendations.append({
                    "product_id": product["id"],
                    "name": product["name"],
                    "price": float(product["current_price"]),
                    "category": product["category_name"],
                    "recommendation_score": round(score, 3),
                    "stock_quantity": product["stock_quantity"],
                    "is_featured": product["is_featured"],
                    "images": product["images"]
                })
            
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error filtering recommendations: {e}")
            return []
    
    async def _identify_cross_sell_opportunities(self, conn) -> List[Dict[str, Any]]:
        """Identify cross-selling opportunities"""
        try:
            cursor = conn.cursor()
            
            # Find frequently bought together products
            cursor.execute("""
                SELECT 
                    oi1.product_id as product1_id,
                    oi2.product_id as product2_id,
                    COUNT(*) as frequency,
                    p1.name as product1_name,
                    p2.name as product2_name
                FROM order_items oi1
                JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
                JOIN products p1 ON oi1.product_id = p1.id
                JOIN products p2 ON oi2.product_id = p2.id
                JOIN orders o ON oi1.order_id = o.id
                WHERE o.status IN ('processing', 'shipped', 'delivered')
                  AND o.created_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)
                  AND p1.is_active = 1 AND p2.is_active = 1
                GROUP BY oi1.product_id, oi2.product_id
                HAVING frequency >= 3
                ORDER BY frequency DESC
                LIMIT 50
            """)
            
            cross_sell_opportunities = []
            for row in cursor.fetchall():
                cross_sell_opportunities.append({
                    "product1_id": row[0],
                    "product2_id": row[1],
                    "frequency": row[2],
                    "product1_name": row[3],
                    "product2_name": row[4],
                    "confidence": min(row[2] / 10.0, 1.0)  # Normalize confidence score
                })
            
            return cross_sell_opportunities
            
        except Exception as e:
            logger.error(f"Error identifying cross-sell opportunities: {e}")
            return []
    
    async def _update_trending_products(self, conn) -> List[Dict[str, Any]]:
        """Update trending products based on recent activity"""
        try:
            cursor = conn.cursor()
            
            # Get trending products based on recent sales
            cursor.execute("""
                SELECT 
                    p.id,
                    p.name,
                    p.current_price,
                    COUNT(oi.id) as recent_sales,
                    SUM(oi.quantity) as total_quantity,
                    AVG(r.rating) as avg_rating
                FROM products p
                JOIN order_items oi ON p.id = oi.product_id
                JOIN orders o ON oi.order_id = o.id
                LEFT JOIN reviews r ON p.id = r.product_id
                WHERE o.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                  AND o.status IN ('processing', 'shipped', 'delivered')
                  AND p.is_active = 1
                GROUP BY p.id
                HAVING recent_sales >= 2
                ORDER BY recent_sales DESC, total_quantity DESC
                LIMIT 20
            """)
            
            trending_products = []
            for row in cursor.fetchall():
                trending_products.append({
                    "product_id": row[0],
                    "name": row[1],
                    "price": float(row[2]),
                    "recent_sales": row[3],
                    "total_quantity": row[4],
                    "avg_rating": float(row[5]) if row[5] else 0,
                    "trend_score": row[3] * (row[4] or 1)  # Sales count * quantity
                })
            
            return trending_products
            
        except Exception as e:
            logger.error(f"Error updating trending products: {e}")
            return []
    
    async def _analyze_recommendation_performance(self, conn) -> Dict[str, Any]:
        """Analyze how well recommendations are performing"""
        try:
            cursor = conn.cursor()
            
            # This would require tracking recommendation clicks/purchases
            # For now, return basic metrics
            cursor.execute("""
                SELECT COUNT(*) as total_orders, AVG(total_amount) as avg_order_value
                FROM orders 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                  AND status IN ('processing', 'shipped', 'delivered')
            """)
            
            row = cursor.fetchone()
            return {
                "total_orders_30d": row[0] if row else 0,
                "avg_order_value_30d": float(row[1]) if row and row[1] else 0,
                "message": "Basic performance metrics - full recommendation tracking not implemented yet"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing recommendation performance: {e}")
            return {"error": str(e)}
    
    async def _analyze_recommendation_accuracy(self, conn) -> Dict[str, Any]:
        """Analyze recommendation accuracy"""
        try:
            # This would require tracking which recommendations were clicked/purchased
            return {"message": "Recommendation accuracy analysis requires click/purchase tracking implementation"}
            
        except Exception as e:
            logger.error(f"Error analyzing recommendation accuracy: {e}")
            return {"error": str(e)}
    
    async def _analyze_recommendation_engagement(self, conn) -> Dict[str, Any]:
        """Analyze user engagement with recommendations"""
        try:
            # This would require tracking recommendation interactions
            return {"message": "Recommendation engagement analysis requires interaction tracking implementation"}
            
        except Exception as e:
            logger.error(f"Error analyzing recommendation engagement: {e}")
            return {"error": str(e)}
    
    async def _analyze_product_affinity(self, conn) -> Dict[str, Any]:
        """Analyze product affinity patterns"""
        try:
            cursor = conn.cursor()
            
            # Analyze category affinity
            cursor.execute("""
                SELECT 
                    c1.name as category1,
                    c2.name as category2,
                    COUNT(*) as co_purchases
                FROM order_items oi1
                JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id != oi2.product_id
                JOIN products p1 ON oi1.product_id = p1.id
                JOIN products p2 ON oi2.product_id = p2.id
                JOIN categories c1 ON p1.category_id = c1.id
                JOIN categories c2 ON p2.category_id = c2.id
                JOIN orders o ON oi1.order_id = o.id
                WHERE o.status IN ('processing', 'shipped', 'delivered')
                  AND o.created_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)
                  AND c1.id < c2.id
                GROUP BY c1.id, c2.id
                HAVING co_purchases >= 5
                ORDER BY co_purchases DESC
                LIMIT 20
            """)
            
            category_affinities = []
            for row in cursor.fetchall():
                category_affinities.append({
                    "category1": row[0],
                    "category2": row[1],
                    "co_purchases": row[2]
                })
            
            return {
                "category_affinities": category_affinities,
                "analysis_period": "90 days"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing product affinity: {e}")
            return {"error": str(e)}
