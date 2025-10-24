from typing import Dict, Any, List, Optional
import json
from database.models import *
from database.connection import get_db_connection

class DatabaseOperations:
    """Database operations using SingleStore native driver"""
    
    @staticmethod
    def dict_to_json(data: Optional[Dict[str, Any]]) -> Optional[str]:
        """Convert dictionary to JSON string"""
        return json.dumps(data) if data else None
    
    @staticmethod
    def json_to_dict(data: Optional[str]) -> Optional[Dict[str, Any]]:
        """Convert JSON string to dictionary"""
        return json.loads(data) if data else None
    
    @staticmethod
    def list_to_json(data: Optional[List]) -> Optional[str]:
        """Convert list to JSON string"""
        return json.dumps(data) if data else None
    
    @staticmethod
    def json_to_list(data: Optional[str]) -> Optional[List]:
        """Convert JSON string to list"""
        return json.loads(data) if data else None

class UserOperations:
    @staticmethod
    def create_user(conn, user: User) -> int:
        """Create a new user"""
        cursor = conn.cursor()
        sql = """
        INSERT INTO users (email, username, hashed_password, first_name, last_name, phone, is_active, is_admin)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            user.email, user.username, user.hashed_password, user.first_name,
            user.last_name, user.phone, user.is_active, user.is_admin
        ))
        conn.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_user_by_email(conn, email: str) -> Optional[User]:
        """Get user by email"""
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if row:
            return User(
                id=row[0], email=row[1], username=row[2], hashed_password=row[3],
                first_name=row[4], last_name=row[5], phone=row[6],
                is_active=row[7], is_admin=row[8], created_at=row[9], updated_at=row[10]
            )
        return None
    
    @staticmethod
    def get_user_by_id(conn, user_id: int) -> Optional[User]:
        """Get user by ID"""
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(
                id=row[0], email=row[1], username=row[2], hashed_password=row[3],
                first_name=row[4], last_name=row[5], phone=row[6],
                is_active=row[7], is_admin=row[8], created_at=row[9], updated_at=row[10]
            )
        return None

class ProductOperations:
    @staticmethod
    def create_product(conn, product: Product) -> int:
        """Create a new product"""
        cursor = conn.cursor()
        sql = """
        INSERT INTO products (name, description, sku, category_id, base_price, current_price, cost_price,
                             stock_quantity, min_stock_level, max_stock_level, weight, dimensions, images, tags,
                             is_active, is_featured, demand_score, price_elasticity, seasonality_factor)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            product.name, product.description, product.sku, product.category_id,
            product.base_price, product.current_price, product.cost_price,
            product.stock_quantity, product.min_stock_level, product.max_stock_level,
            product.weight, DatabaseOperations.dict_to_json(product.dimensions),
            DatabaseOperations.list_to_json(product.images), DatabaseOperations.list_to_json(product.tags),
            product.is_active, product.is_featured, product.demand_score,
            product.price_elasticity, product.seasonality_factor
        ))
        conn.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_products(conn, limit: int = 100, offset: int = 0, category_id: Optional[int] = None,
                    search: Optional[str] = None, is_featured: Optional[bool] = None) -> List[Product]:
        """Get products with filtering"""
        cursor = conn.cursor()
        
        where_conditions = ["is_active = 1"]
        params = []
        
        if category_id:
            where_conditions.append("category_id = %s")
            params.append(category_id)
        
        if search:
            where_conditions.append("(name LIKE %s OR description LIKE %s OR sku LIKE %s)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if is_featured is not None:
            where_conditions.append("is_featured = %s")
            params.append(is_featured)
        
        where_clause = " AND ".join(where_conditions)
        sql = f"""
        SELECT * FROM products 
        WHERE {where_clause}
        ORDER BY is_featured DESC, demand_score DESC, created_at DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        cursor.execute(sql, params)
        products = []
        for row in cursor.fetchall():
            products.append(Product(
                id=row[0], name=row[1], description=row[2], sku=row[3], category_id=row[4],
                base_price=float(row[5]), current_price=float(row[6]), cost_price=float(row[7]) if row[7] else None,
                stock_quantity=row[8], min_stock_level=row[9], max_stock_level=row[10],
                weight=float(row[11]) if row[11] else None,
                dimensions=row[12] if isinstance(row[12], dict) else DatabaseOperations.json_to_dict(row[12]),
                images=row[13] if isinstance(row[13], list) else DatabaseOperations.json_to_list(row[13]),
                tags=row[14] if isinstance(row[14], list) else DatabaseOperations.json_to_list(row[14]),
                is_active=row[15], is_featured=row[16], demand_score=float(row[17]),
                price_elasticity=float(row[18]), seasonality_factor=float(row[19]),
                created_at=row[20], updated_at=row[21]
            ))
        return products
    
    @staticmethod
    def get_product_by_id(conn, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = %s AND is_active = 1", (product_id,))
        row = cursor.fetchone()
        if row:
            return Product(
                id=row[0], name=row[1], description=row[2], sku=row[3], category_id=row[4],
                base_price=float(row[5]), current_price=float(row[6]), cost_price=float(row[7]) if row[7] else None,
                stock_quantity=row[8], min_stock_level=row[9], max_stock_level=row[10],
                weight=float(row[11]) if row[11] else None,
                dimensions=row[12] if isinstance(row[12], dict) else DatabaseOperations.json_to_dict(row[12]),
                images=row[13] if isinstance(row[13], list) else DatabaseOperations.json_to_list(row[13]),
                tags=row[14] if isinstance(row[14], list) else DatabaseOperations.json_to_list(row[14]),
                is_active=row[15], is_featured=row[16], demand_score=float(row[17]),
                price_elasticity=float(row[18]), seasonality_factor=float(row[19]),
                created_at=row[20], updated_at=row[21]
            )
        return None
    
    @staticmethod
    def update_product_stock(conn, product_id: int, new_quantity: int) -> bool:
        """Update product stock quantity"""
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET stock_quantity = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (new_quantity, product_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    
    @staticmethod
    def update_product_price(conn, product_id: int, new_price: float) -> bool:
        """Update product price"""
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET current_price = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (new_price, product_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    
    @staticmethod
    def get_low_stock_products(conn) -> List[Product]:
        """Get products with low stock"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM products 
            WHERE is_active = 1 AND stock_quantity <= min_stock_level
            ORDER BY stock_quantity ASC
        """)
        products = []
        for row in cursor.fetchall():
            products.append(Product(
                id=row[0], name=row[1], description=row[2], sku=row[3], category_id=row[4],
                base_price=float(row[5]), current_price=float(row[6]), cost_price=float(row[7]) if row[7] else None,
                stock_quantity=row[8], min_stock_level=row[9], max_stock_level=row[10],
                weight=float(row[11]) if row[11] else None,
                dimensions=row[12] if isinstance(row[12], dict) else DatabaseOperations.json_to_dict(row[12]),
                images=row[13] if isinstance(row[13], list) else DatabaseOperations.json_to_list(row[13]),
                tags=row[14] if isinstance(row[14], list) else DatabaseOperations.json_to_list(row[14]),
                is_active=row[15], is_featured=row[16], demand_score=float(row[17]),
                price_elasticity=float(row[18]), seasonality_factor=float(row[19]),
                created_at=row[20], updated_at=row[21]
            ))
        return products

class OrderOperations:
    @staticmethod
    def create_order(conn, order: Order) -> int:
        """Create a new order"""
        cursor = conn.cursor()
        sql = """
        INSERT INTO orders (user_id, order_number, status, total_amount, tax_amount, shipping_amount,
                           discount_amount, shipping_address, billing_address, shipping_method,
                           payment_method, payment_status, risk_score, priority_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            order.user_id, order.order_number, order.status, order.total_amount,
            order.tax_amount, order.shipping_amount, order.discount_amount,
            DatabaseOperations.dict_to_json(order.shipping_address),
            DatabaseOperations.dict_to_json(order.billing_address),
            order.shipping_method, order.payment_method, order.payment_status,
            order.risk_score, order.priority_score
        ))
        conn.commit()
        return cursor.lastrowid
    
    @staticmethod
    def create_order_item(conn, order_item: OrderItem) -> int:
        """Create order item"""
        cursor = conn.cursor()
        sql = """
        INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            order_item.order_id, order_item.product_id, order_item.quantity,
            order_item.unit_price, order_item.total_price
        ))
        conn.commit()
        return cursor.lastrowid
    
    @staticmethod
    def get_user_orders(conn, user_id: int, limit: int = 50, offset: int = 0) -> List[Order]:
        """Get orders for a user"""
        cursor = conn.cursor()
        sql = """
        SELECT * FROM orders WHERE user_id = %s 
        ORDER BY created_at DESC LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (user_id, limit, offset))
        orders = []
        for row in cursor.fetchall():
            orders.append(Order(
                id=row[0], user_id=row[1], order_number=row[2], status=row[3],
                total_amount=float(row[4]), tax_amount=float(row[5]), shipping_amount=float(row[6]),
                discount_amount=float(row[7]), shipping_address=DatabaseOperations.json_to_dict(row[8]),
                billing_address=DatabaseOperations.json_to_dict(row[9]), shipping_method=row[10],
                tracking_number=row[11], payment_method=row[12], payment_status=row[13],
                payment_id=row[14], risk_score=float(row[15]), priority_score=float(row[16]),
                created_at=row[17], updated_at=row[18], shipped_at=row[19], delivered_at=row[20]
            ))
        return orders
    
    @staticmethod
    def get_sales_history(conn, product_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get sales history for a product"""
        cursor = conn.cursor()
        sql = """
        SELECT DATE(o.created_at) as date, 
               SUM(oi.quantity) as quantity_sold,
               COUNT(oi.id) as order_count
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE oi.product_id = %s 
          AND o.created_at >= DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)
          AND o.status IN ('processing', 'shipped', 'delivered')
        GROUP BY DATE(o.created_at)
        ORDER BY date DESC
        """
        cursor.execute(sql, (product_id, days))
        
        sales_history = []
        for row in cursor.fetchall():
            sales_history.append({
                "date": str(row[0]),
                "quantity_sold": int(row[1] or 0),
                "order_count": int(row[2] or 0)
            })
        return sales_history

class AgentLogOperations:
    @staticmethod
    def create_log(conn, log: AgentLog) -> int:
        """Create agent log entry"""
        cursor = conn.cursor()
        sql = """
        INSERT INTO agent_logs (agent_name, action_type, target_id, target_type, action_data,
                               result, error_message, execution_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            log.agent_name, log.action_type, log.target_id, log.target_type,
            DatabaseOperations.dict_to_json(log.action_data), log.result,
            log.error_message, log.execution_time
        ))
        conn.commit()
        return cursor.lastrowid

class InventoryLogOperations:
    @staticmethod
    def create_log(conn, log: InventoryLog) -> int:
        """Create inventory log entry"""
        cursor = conn.cursor()
        sql = """
        INSERT INTO inventory_logs (product_id, change_type, quantity_change, previous_quantity,
                                   new_quantity, reason, agent_action)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            log.product_id, log.change_type, log.quantity_change,
            log.previous_quantity, log.new_quantity, log.reason, log.agent_action
        ))
        conn.commit()
        return cursor.lastrowid

class PriceHistoryOperations:
    @staticmethod
    def create_log(conn, log: PriceHistory) -> int:
        """Create price history entry"""
        cursor = conn.cursor()
        sql = """
        INSERT INTO price_history (product_id, old_price, new_price, change_reason, agent_action, market_data)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            log.product_id, log.old_price, log.new_price, log.change_reason,
            log.agent_action, DatabaseOperations.dict_to_json(log.market_data)
        ))
        conn.commit()
        return cursor.lastrowid

class CartOperations:
    @staticmethod
    def get_user_cart(conn, user_id: int) -> List[Dict[str, Any]]:
        """Get user's cart items with product details"""
        cursor = conn.cursor()
        sql = """
        SELECT c.id, c.product_id, p.name, p.current_price, c.quantity, 
               (p.current_price * c.quantity) as total_price, p.images, p.stock_quantity
        FROM cart_items c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = %s AND p.is_active = 1
        ORDER BY c.created_at DESC
        """
        cursor.execute(sql, (user_id,))
        
        cart_items = []
        for row in cursor.fetchall():
            cart_items.append({
                "id": row[0],
                "product_id": row[1],
                "product_name": row[2],
                "product_price": float(row[3]),
                "quantity": row[4],
                "total_price": float(row[5]),
                "product_images": DatabaseOperations.json_to_list(row[6]) or [],
                "stock_available": row[7]
            })
        return cart_items
    
    @staticmethod
    def add_to_cart(conn, user_id: int, product_id: int, quantity: int) -> int:
        """Add item to cart"""
        cursor = conn.cursor()
        
        # Check if item already exists
        cursor.execute("SELECT id, quantity FROM cart_items WHERE user_id = %s AND product_id = %s", 
                      (user_id, product_id))
        existing = cursor.fetchone()
        
        if existing:
            # Update quantity
            new_quantity = existing[1] + quantity
            cursor.execute("UPDATE cart_items SET quantity = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                          (new_quantity, existing[0]))
            conn.commit()
            return existing[0]
        else:
            # Create new item
            cursor.execute("INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                          (user_id, product_id, quantity))
            conn.commit()
            return cursor.lastrowid
