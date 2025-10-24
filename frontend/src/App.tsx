import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';

// Pages
import HomePage from './pages/HomePage';
import ProductsPage from './pages/ProductsPage';
import ProductDetailPage from './pages/ProductDetailPage';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import OrdersPage from './pages/OrdersPage';
import ProfilePage from './pages/ProfilePage';
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminProducts from './pages/admin/AdminProducts';
import AdminOrders from './pages/admin/AdminOrders';
import AdminAnalytics from './pages/admin/AdminAnalytics';
import AdminAgents from './pages/admin/AdminAgents';
import AdminPricingDemo from './pages/admin/AdminPricingDemo';
import AdminRecommendations from './pages/admin/AdminRecommendations';
import AdminMonitoringDashboard from './pages/admin/AdminMonitoringDashboard';

const App: React.FC = () => {

  return (
    <Router>
      <div className="min-h-screen bg-dark-900 flex flex-col">
        <Navbar />
        
        <main className="flex-1">
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<HomePage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/products/:id" element={<ProductDetailPage />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/checkout" element={<CheckoutPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            
            {/* Admin Routes - Now Public for Demo */}
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/products" element={<AdminProducts />} />
            <Route path="/admin/orders" element={<AdminOrders />} />
            <Route path="/admin/analytics" element={<AdminAnalytics />} />
            <Route path="/admin/agents" element={<AdminAgents />} />
            <Route path="/admin/pricing-demo" element={<AdminPricingDemo />} />
            <Route path="/admin/recommendations" element={<AdminRecommendations />} />
            <Route path="/admin/monitoring" element={<AdminMonitoringDashboard />} />
            
            {/* 404 Page */}
            <Route 
              path="*" 
              element={
                <div className="min-h-screen flex items-center justify-center bg-dark-900">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-gray-100 mb-4">404</h1>
                    <p className="text-gray-400 mb-8">Page not found</p>
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
