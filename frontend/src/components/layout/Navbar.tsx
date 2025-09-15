import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';
import { useCartStore } from '../../stores/cartStore';
import { 
  ShoppingCartIcon, 
  UserIcon, 
  Bars3Icon, 
  XMarkIcon,
  MagnifyingGlassIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline';

const Navbar: React.FC = () => {
  const { user, logout } = useAuthStore();
  const { totalItems, fetchCart } = useCartStore();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  React.useEffect(() => {
    if (user) {
      fetchCart();
    }
  }, [user, fetchCart]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/products?search=${encodeURIComponent(searchQuery)}`);
      setSearchQuery('');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <CpuChipIcon className="h-8 w-8 text-primary-600" />
              <span className="text-xl font-bold text-gray-900">
                AI Commerce
              </span>
            </Link>
          </div>

          {/* Search Bar - Desktop */}
          <div className="hidden md:flex flex-1 max-w-lg mx-8">
            <form onSubmit={handleSearch} className="w-full">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              </div>
            </form>
          </div>

          {/* Navigation Links - Desktop */}
          <div className="hidden md:flex items-center space-x-6">
            <Link
              to="/products"
              className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
            >
              Products
            </Link>

            {user ? (
              <>
                {/* Cart */}
                <Link
                  to="/cart"
                  className="relative p-2 text-gray-700 hover:text-primary-600 transition-colors"
                >
                  <ShoppingCartIcon className="h-6 w-6" />
                  {totalItems > 0 && (
                    <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {totalItems > 99 ? '99+' : totalItems}
                    </span>
                  )}
                </Link>

                {/* User Menu */}
                <div className="relative group">
                  <button className="flex items-center space-x-1 text-gray-700 hover:text-primary-600 transition-colors">
                    <UserIcon className="h-6 w-6" />
                    <span className="font-medium">{user.first_name}</span>
                  </button>

                  {/* Dropdown */}
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                    <div className="py-1">
                      <Link
                        to="/profile"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Profile
                      </Link>
                      <Link
                        to="/orders"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Orders
                      </Link>
                      {user.is_admin && (
                        <>
                          <hr className="my-1" />
                          <Link
                            to="/admin"
                            className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          >
                            Admin Dashboard
                          </Link>
                          <Link
                            to="/admin/agents"
                            className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                          >
                            <CpuChipIcon className="h-4 w-4" />
                            <span>AI Agents</span>
                          </Link>
                        </>
                      )}
                      <hr className="my-1" />
                      <button
                        onClick={handleLogout}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        Logout
                      </button>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="btn-primary"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-md text-gray-700 hover:text-primary-600 transition-colors"
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
          <div className="md:hidden border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {/* Mobile Search */}
              <form onSubmit={handleSearch} className="mb-4">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Search products..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                </div>
              </form>

              <Link
                to="/products"
                className="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                onClick={() => setIsMenuOpen(false)}
              >
                Products
              </Link>

              {user ? (
                <>
                  <Link
                    to="/cart"
                    className="flex items-center px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <ShoppingCartIcon className="h-5 w-5 mr-2" />
                    Cart {totalItems > 0 && `(${totalItems})`}
                  </Link>
                  <Link
                    to="/profile"
                    className="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Profile
                  </Link>
                  <Link
                    to="/orders"
                    className="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Orders
                  </Link>
                  {user.is_admin && (
                    <>
                      <Link
                        to="/admin"
                        className="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        Admin Dashboard
                      </Link>
                      <Link
                        to="/admin/agents"
                        className="flex items-center px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        <CpuChipIcon className="h-5 w-5 mr-2" />
                        AI Agents
                      </Link>
                    </>
                  )}
                  <button
                    onClick={() => {
                      handleLogout();
                      setIsMenuOpen(false);
                    }}
                    className="block w-full text-left px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="block px-3 py-2 text-gray-700 hover:text-primary-600 font-medium"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="block px-3 py-2 text-primary-600 hover:text-primary-700 font-medium"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
