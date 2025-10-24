import { apiService } from './api';
import { CartItem, CartSummary } from '../types';

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
