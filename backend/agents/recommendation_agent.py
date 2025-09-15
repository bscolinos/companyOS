from typing import Dict, Any, List, Optional, Tuple
import asyncio
import logging
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import numpy as np
from backend.agents.base_agent import BaseAgent
from backend.database.connection import get_db_connection
from backend.config import settings
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
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"user_id": user_id, "recommendations": [], "error": "User not found"}
            
            # Get user's purchase history
            user_orders = await self._get_user_purchase_history(db, user_id)
            
            # Get user's browsing behavior (cart items, reviews)
            user_behavior = await self._get_user_behavior(db, user_id)
            
            # Generate recommendations using multiple algorithms
            collaborative_recs = await self._collaborative_filtering(db, user_id, user_orders)
            content_based_recs = await self._content_based_filtering(db, user_orders, user_behavior)
            ai_powered_recs = await self._ai_powered_recommendations(db, user_id, user_orders, user_behavior)
            
            # Combine and rank recommendations
            combined_recs = await self._combine_recommendations([
                ("collaborative", collaborative_recs),
                ("content_based", content_based_recs),
                ("ai_powered", ai_powered_recs)
            ])
            
            # Filter and limit results
            final_recommendations = await self._filter_and_rank_recommendations(
                db, user_id, combined_recs, limit
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
    
    async def _generate_batch_recommendations(self, db: Session, limit_users: int = 100) -> List[Dict[str, Any]]:
        """Generate recommendations for multiple users"""
        batch_recommendations = []
        
        try:
            # Get recently active users
            active_users = db.query(User.id).join(
                Order, User.id == Order.user_id
            ).filter(
                Order.created_at >= datetime.utcnow() - timedelta(days=30)
            ).distinct().limit(limit_users).all()
            
            for user_tuple in active_users:
                user_id = user_tuple[0]
                user_recs = await self._generate_user_recommendations(db, user_id, 5)
                batch_recommendations.append(user_recs)
            
        except Exception as e:
            logger.error(f"Error generating batch recommendations: {e}")
        
        return batch_recommendations
    
    async def _get_user_purchase_history(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Get user's purchase history"""
        try:
            orders = db.query(Order).filter(
                and_(
                    Order.user_id == user_id,
                    Order.status.in_(['processing', 'shipped', 'delivered'])
                )
            ).order_by(desc(Order.created_at)).all()
            
            purchase_history = []
            for order in orders:
                order_items = db.query(OrderItem).filter(
                    OrderItem.order_id == order.id
                ).all()
                
                for item in order_items:
                    purchase_history.append({
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": float(item.unit_price),
                        "order_date": order.created_at.isoformat(),
                        "order_id": order.id
                    })
            
            return purchase_history
            
        except Exception as e:
            logger.error(f"Error getting purchase history for user {user_id}: {e}")
            return []
    
    async def _get_user_behavior(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Get user's browsing and interaction behavior"""
        try:
            # Get cart items (shows interest)
            cart_items = db.query(CartItem).filter(
                CartItem.user_id == user_id
            ).all()
            
            # Get reviews (shows preferences)
            reviews = db.query(Review).filter(
                Review.user_id == user_id
            ).all()
            
            return {
                "cart_items": [
                    {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "added_at": item.created_at.isoformat()
                    }
                    for item in cart_items
                ],
                "reviews": [
                    {
                        "product_id": review.product_id,
                        "rating": review.rating,
                        "sentiment_score": review.sentiment_score or 0,
                        "created_at": review.created_at.isoformat()
                    }
                    for review in reviews
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting user behavior for user {user_id}: {e}")
            return {"cart_items": [], "reviews": []}
    
    async def _collaborative_filtering(self, db: Session, user_id: int, user_orders: List[Dict[str, Any]]) -> List[Tuple[int, float]]:
        """Collaborative filtering recommendations"""
        try:
            if not user_orders:
                return []
            
            # Get products the user has purchased
            user_products = set(order["product_id"] for order in user_orders)
            
            # Find similar users (users who bought similar products)
            similar_users = db.query(
                OrderItem.order_id,
                func.count(OrderItem.product_id).label('common_products')
            ).join(
                Order, OrderItem.order_id == Order.id
            ).filter(
                and_(
                    OrderItem.product_id.in_(user_products),
                    Order.user_id != user_id,
                    Order.status.in_(['processing', 'shipped', 'delivered'])
                )
            ).group_by(
                OrderItem.order_id
            ).having(
                func.count(OrderItem.product_id) >= 2  # At least 2 common products
            ).order_by(
                desc('common_products')
            ).limit(50).all()
            
            # Get order IDs of similar users
            similar_order_ids = [row.order_id for row in similar_users]
            
            if not similar_order_ids:
                return []
            
            # Get products bought by similar users that current user hasn't bought
            recommended_products = db.query(
                OrderItem.product_id,
                func.count(OrderItem.product_id).label('frequency'),
                func.avg(OrderItem.unit_price).label('avg_price')
            ).filter(
                and_(
                    OrderItem.order_id.in_(similar_order_ids),
                    ~OrderItem.product_id.in_(user_products)
                )
            ).group_by(
                OrderItem.product_id
            ).order_by(
                desc('frequency')
            ).limit(20).all()
            
            # Calculate recommendation scores
            recommendations = []
            max_frequency = max([prod.frequency for prod in recommended_products], default=1)
            
            for product in recommended_products:
                # Score based on frequency among similar users
                score = product.frequency / max_frequency
                recommendations.append((product.product_id, score))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error in collaborative filtering: {e}")
            return []
    
    async def _content_based_filtering(self, db: Session, user_orders: List[Dict[str, Any]], user_behavior: Dict[str, Any]) -> List[Tuple[int, float]]:
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
            
            # Get products user has interacted with
            interested_products = db.query(Product).filter(
                Product.id.in_(interested_product_ids)
            ).all()
            
            # Extract categories and tags
            preferred_categories = set()
            preferred_tags = set()
            
            for product in interested_products:
                if product.category_id:
                    preferred_categories.add(product.category_id)
                
                if product.tags:
                    preferred_tags.update(product.tags)
            
            # Find similar products
            similar_products = db.query(Product).filter(
                and_(
                    Product.is_active == True,
                    ~Product.id.in_(interested_product_ids),
                    or_(
                        Product.category_id.in_(preferred_categories) if preferred_categories else False,
                        # Could add tag matching here if needed
                    )
                )
            ).limit(30).all()
            
            # Calculate similarity scores
            recommendations = []
            for product in similar_products:
                score = 0.0
                
                # Category similarity
                if product.category_id in preferred_categories:
                    score += 0.7
                
                # Tag similarity (if implemented)
                if product.tags and preferred_tags:
                    common_tags = set(product.tags) & preferred_tags
                    if common_tags:
                        score += 0.3 * (len(common_tags) / len(preferred_tags))
                
                # Price range similarity
                user_avg_price = sum(order["price"] for order in user_orders) / len(user_orders) if user_orders else 0
                if user_avg_price > 0:
                    price_diff = abs(float(product.current_price) - user_avg_price) / user_avg_price
                    if price_diff < 0.5:  # Within 50% of average price
                        score += 0.2
                
                if score > self.min_recommendation_score:
                    recommendations.append((product.id, score))
            
            return sorted(recommendations, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            logger.error(f"Error in content-based filtering: {e}")
            return []
    
    async def _ai_powered_recommendations(self, db: Session, user_id: int, user_orders: List[Dict[str, Any]], user_behavior: Dict[str, Any]) -> List[Tuple[int, float]]:
        """AI-powered recommendations using OpenAI"""
        try:
            if not self.openai_client:
                return []
            
            # Get user profile
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            # Get top products for recommendation
            top_products = db.query(Product).filter(
                Product.is_active == True
            ).order_by(
                desc(Product.demand_score)
            ).limit(50).all()
            
            # Prepare context for AI
            user_context = {
                "purchase_history": user_orders[-10:],  # Last 10 purchases
                "cart_items": user_behavior["cart_items"],
                "reviews": user_behavior["reviews"][-5:],  # Last 5 reviews
            }
            
            products_context = [
                {
                    "id": product.id,
                    "name": product.name,
                    "price": float(product.current_price),
                    "category": product.category.name if product.category else "Unknown",
                    "demand_score": product.demand_score,
                    "tags": product.tags or []
                }
                for product in top_products[:20]  # Limit for AI processing
            ]
            
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
    
    async def _filter_and_rank_recommendations(self, db: Session, user_id: int, recommendations: List[Tuple[int, float]], limit: int) -> List[Dict[str, Any]]:
        """Filter and rank final recommendations"""
        try:
            if not recommendations:
                return []
            
            # Get product details
            product_ids = [rec[0] for rec in recommendations[:limit * 2]]  # Get more to filter
            products = db.query(Product).filter(
                and_(
                    Product.id.in_(product_ids),
                    Product.is_active == True,
                    Product.stock_quantity > 0  # Only recommend in-stock items
                )
            ).all()
            
            # Create product lookup
            product_lookup = {product.id: product for product in products}
            
            # Filter and format recommendations
            final_recommendations = []
            
            for product_id, score in recommendations:
                if len(final_recommendations) >= limit:
                    break
                
                if product_id not in product_lookup:
                    continue
                
                product = product_lookup[product_id]
                
                final_recommendations.append({
                    "product_id": product.id,
                    "name": product.name,
                    "price": float(product.current_price),
                    "category": product.category.name if product.category else None,
                    "recommendation_score": round(score, 3),
                    "stock_quantity": product.stock_quantity,
                    "is_featured": product.is_featured,
                    "images": product.images or []
                })
            
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Error filtering recommendations: {e}")
            return []
    
    async def _identify_cross_sell_opportunities(self, db: Session) -> List[Dict[str, Any]]:
        """Identify cross-selling opportunities"""
        # Implementation for cross-sell analysis
        return []
    
    async def _update_trending_products(self, db: Session) -> List[Dict[str, Any]]:
        """Update trending products based on recent activity"""
        # Implementation for trending products
        return []
    
    async def _analyze_recommendation_performance(self, db: Session) -> Dict[str, Any]:
        """Analyze how well recommendations are performing"""
        # Implementation for performance analysis
        return {"message": "Recommendation performance analysis not implemented yet"}
    
    async def _analyze_recommendation_accuracy(self, db: Session) -> Dict[str, Any]:
        """Analyze recommendation accuracy"""
        # Implementation for accuracy analysis
        return {"message": "Recommendation accuracy analysis not implemented yet"}
    
    async def _analyze_recommendation_engagement(self, db: Session) -> Dict[str, Any]:
        """Analyze user engagement with recommendations"""
        # Implementation for engagement analysis
        return {"message": "Recommendation engagement analysis not implemented yet"}
    
    async def _analyze_product_affinity(self, db: Session) -> Dict[str, Any]:
        """Analyze product affinity patterns"""
        # Implementation for affinity analysis
        return {"message": "Product affinity analysis not implemented yet"}
