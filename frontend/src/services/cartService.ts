import { apiService } from './api';

export interface CartItem {
  id: number;
  product_id: number;
  product_name: string;
  product_price: number;
  quantity: number;
  total_price: number;
  product_images: string[];
  stock_available: number;
}

export interface CartSummary {
  total_items: number;
  subtotal: number;
  tax_amount: number;
  shipping_amount: number;
  total_amount: number;
}

class CartService {
  async getCart(): Promise<CartItem[]> {
    return await apiService.getCart();
  }

  async addToCart(productId: number, quantity: number): Promise<CartItem> {
    return await apiService.addToCart(productId, quantity);
  }

  async updateCartItem(itemId: number, quantity: number): Promise<CartItem> {
    return await apiService.updateCartItem(itemId, quantity);
  }

  async removeFromCart(itemId: number): Promise<void> {
    return await apiService.removeFromCart(itemId);
  }

  async clearCart(): Promise<void> {
    return await apiService.clearCart();
  }

  async getCartSummary(): Promise<CartSummary> {
    return await apiService.getCartSummary();
  }
}

export const cartService = new CartService();
