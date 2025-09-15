import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import LoadingSpinner from './components/ui/LoadingSpinner';

// Pages
import HomePage from './pages/HomePage';
import ProductsPage from './pages/ProductsPage';
import ProductDetailPage from './pages/ProductDetailPage';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import OrdersPage from './pages/OrdersPage';
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminProducts from './pages/admin/AdminProducts';
import AdminOrders from './pages/admin/AdminOrders';
import AdminAnalytics from './pages/admin/AdminAnalytics';
import AdminAgents from './pages/admin/AdminAgents';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode; adminOnly?: boolean }> = ({ 
  children, 
  adminOnly = false 
}) => {
  const { user, isLoading } = useAuthStore();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <LoginPage />;
  }

  if (adminOnly && !user.is_admin) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600">You don't have permission to access this page.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};

const App: React.FC = () => {
  const { initializeAuth, isLoading } = useAuthStore();

  React.useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Navbar />
        
        <main className="flex-1">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/products/:id" element={<ProductDetailPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            
            {/* Protected Routes */}
            <Route 
              path="/cart" 
              element={
                <ProtectedRoute>
                  <CartPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/checkout" 
              element={
                <ProtectedRoute>
                  <CheckoutPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/orders" 
              element={
                <ProtectedRoute>
                  <OrdersPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              } 
            />
            
            {/* Admin Routes */}
            <Route 
              path="/admin" 
              element={
                <ProtectedRoute adminOnly>
                  <AdminDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/products" 
              element={
                <ProtectedRoute adminOnly>
                  <AdminProducts />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/orders" 
              element={
                <ProtectedRoute adminOnly>
                  <AdminOrders />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/analytics" 
              element={
                <ProtectedRoute adminOnly>
                  <AdminAnalytics />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/agents" 
              element={
                <ProtectedRoute adminOnly>
                  <AdminAgents />
                </ProtectedRoute>
              } 
            />
            
            {/* 404 Page */}
            <Route 
              path="*" 
              element={
                <div className="min-h-screen flex items-center justify-center bg-gray-50">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                    <p className="text-gray-600 mb-8">Page not found</p>
                    <a 
                      href="/" 
                      className="btn-primary"
                    >
                      Go Home
                    </a>
                  </div>
                </div>
              } 
            />
          </Routes>
        </main>
        
        <Footer />
      </div>
    </Router>
  );
};

export default App;
