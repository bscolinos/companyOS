import { create } from 'zustand';
import { cartService, CartItem } from '../services/cartService';
import toast from 'react-hot-toast';

interface CartState {
  items: CartItem[];
  isLoading: boolean;
  totalItems: number;
  totalAmount: number;
  fetchCart: () => Promise<void>;
  addToCart: (productId: number, quantity: number) => Promise<void>;
  updateQuantity: (itemId: number, quantity: number) => Promise<void>;
  removeItem: (itemId: number) => Promise<void>;
  clearCart: () => Promise<void>;
  getCartSummary: () => Promise<void>;
}

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  isLoading: false,
  totalItems: 0,
  totalAmount: 0,

  fetchCart: async () => {
    set({ isLoading: true });
    try {
      const items = await cartService.getCart();
      const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);
      const totalAmount = items.reduce((sum, item) => sum + item.total_price, 0);
      
      set({ 
        items, 
        totalItems, 
        totalAmount, 
        isLoading: false 
      });
    } catch (error: any) {
      set({ isLoading: false });
      console.error('Failed to fetch cart:', error);
    }
  },

  addToCart: async (productId: number, quantity: number) => {
    try {
      await cartService.addToCart(productId, quantity);
      await get().fetchCart(); // Refresh cart
      toast.success('Added to cart!');
    } catch (error: any) {
      toast.error(error.message || 'Failed to add to cart');
    }
  },

  updateQuantity: async (itemId: number, quantity: number) => {
    try {
      if (quantity <= 0) {
        await get().removeItem(itemId);
        return;
      }
      
      await cartService.updateCartItem(itemId, quantity);
      await get().fetchCart(); // Refresh cart
    } catch (error: any) {
      toast.error(error.message || 'Failed to update quantity');
    }
  },

  removeItem: async (itemId: number) => {
    try {
      await cartService.removeFromCart(itemId);
      await get().fetchCart(); // Refresh cart
      toast.success('Item removed from cart');
    } catch (error: any) {
      toast.error(error.message || 'Failed to remove item');
    }
  },

  clearCart: async () => {
    try {
      await cartService.clearCart();
      set({ items: [], totalItems: 0, totalAmount: 0 });
      toast.success('Cart cleared');
    } catch (error: any) {
      toast.error(error.message || 'Failed to clear cart');
    }
  },

  getCartSummary: async () => {
    try {
      const summary = await cartService.getCartSummary();
      set({ 
        totalItems: summary.total_items,
        totalAmount: summary.total_amount
      });
    } catch (error: any) {
      console.error('Failed to get cart summary:', error);
    }
  },
}));
