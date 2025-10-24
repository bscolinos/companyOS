import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCartStore } from '../../stores/cartStore';
import { 
  ShoppingCartIcon, 
  UserIcon, 
  Bars3Icon, 
  XMarkIcon,
  MagnifyingGlassIcon,
  CpuChipIcon,
  ChartBarIcon,
  CogIcon
} from '@heroicons/react/24/outline';

const Navbar: React.FC = () => {
  const { totalItems, fetchCart } = useCartStore();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  React.useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/products?search=${encodeURIComponent(searchQuery)}`);
      setSearchQuery('');
    }
  };

  return (
    <nav className="bg-dark-800 shadow-lg border-b border-dark-700 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <CpuChipIcon className="h-8 w-8 text-primary-600" />
            <span className="text-xl font-bold text-gray-100">
              AI Commerce
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className="text-gray-300 hover:text-primary-400 font-medium transition-colors"
            >
              Home
            </Link>
            <Link
              to="/products"
              className="text-gray-300 hover:text-primary-400 font-medium transition-colors"
            >
              Products
            </Link>

            {/* Search Bar */}
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-64 pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 text-gray-100 placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
            </form>
          </div>

          {/* Right Side Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Cart Icon */}
            <Link
              to="/cart"
              className="relative p-2 text-gray-300 hover:text-primary-400 transition-colors"
            >
              <ShoppingCartIcon className="h-6 w-6" />
              {totalItems > 0 && (
                <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {totalItems > 99 ? '99+' : totalItems}
                </span>
              )}
            </Link>

            {/* Demo Navigation Menu */}
            <div className="relative group">
              <button className="flex items-center space-x-1 text-gray-300 hover:text-primary-400 transition-colors">
                <CogIcon className="h-6 w-6" />
                <span className="font-medium">Demo</span>
              </button>

              {/* Dropdown */}
              <div className="absolute right-0 mt-2 w-48 bg-dark-800 border border-dark-700 rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                <div className="py-1">
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-700 flex items-center space-x-2"
                  >
                    <UserIcon className="h-4 w-4" />
                    <span>Profile</span>
                  </Link>
                  <Link
                    to="/orders"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-700"
                  >
                    Orders
                  </Link>
                  <hr className="my-1 border-dark-600" />
                  <Link
                    to="/admin"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-700 flex items-center space-x-2"
                  >
                    <ChartBarIcon className="h-4 w-4" />
                    <span>Admin Dashboard</span>
                  </Link>
                  <Link
                    to="/admin/agents"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-700 flex items-center space-x-2"
                  >
                    <CpuChipIcon className="h-4 w-4" />
                    <span>AI Agents</span>
                  </Link>
                  <Link
                    to="/admin/analytics"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-700"
                  >
                    Analytics
                  </Link>
                  <hr className="my-1 border-dark-600" />
                  <div className="px-4 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wide">
                    AI Demos
                  </div>
                  <Link
                    to="/admin/pricing-demo"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-700"
                  >
                    🎯 Dynamic Pricing
                  </Link>
                  <Link
                    to="/admin/recommendations"
                    className="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-700"
                  >
                    ✨ Recommendations
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-md text-gray-300 hover:text-primary-400 transition-colors"
            >
              {isMenuOpen ? (
                <XMarkIcon className="h-6 w-6" />
              ) : (
                <Bars3Icon className="h-6 w-6" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-dark-700">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {/* Mobile Search */}
              <form onSubmit={handleSearch} className="mb-4">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 text-gray-100 placeholder-gray-400 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                  <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                </div>
              </form>

              {/* Mobile Navigation Links */}
              <Link
                to="/"
                className="block px-3 py-2 text-base font-medium text-gray-300 hover:text-primary-400 hover:bg-dark-700 rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                Home
              </Link>
              <Link
                to="/products"
                className="block px-3 py-2 text-base font-medium text-gray-300 hover:text-primary-400 hover:bg-dark-700 rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                Products
              </Link>
              <Link
                to="/cart"
                className="block px-3 py-2 text-base font-medium text-gray-300 hover:text-primary-400 hover:bg-dark-700 rounded-md flex items-center justify-between"
                onClick={() => setIsMenuOpen(false)}
              >
                <span>Cart</span>
                {totalItems > 0 && (
                  <span className="bg-primary-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {totalItems > 99 ? '99+' : totalItems}
                  </span>
                )}
              </Link>
              
              <hr className="my-2" />
              <div className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Demo Pages
              </div>
              
              <Link
                to="/profile"
                className="block px-3 py-2 text-base font-medium text-gray-300 hover:text-primary-400 hover:bg-dark-700 rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                Profile
              </Link>
              <Link
                to="/orders"
                className="block px-3 py-2 text-base font-medium text-gray-300 hover:text-primary-400 hover:bg-dark-700 rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                Orders
              </Link>
              <Link
                to="/admin"
                className="block px-3 py-2 text-base font-medium text-gray-300 hover:text-primary-400 hover:bg-dark-700 rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                Admin Dashboard
              </Link>
              <Link
                to="/admin/agents"
                className="block px-3 py-2 text-base font-medium text-gray-300 hover:text-primary-400 hover:bg-dark-700 rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                AI Agents
              </Link>
              <Link
                to="/admin/analytics"
                className="block px-3 py-2 text-base font-medium text-gray-300 hover:text-primary-400 hover:bg-dark-700 rounded-md"
                onClick={() => setIsMenuOpen(false)}
              >
                Analytics
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;