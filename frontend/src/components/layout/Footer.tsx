import React from 'react';
import { Link } from 'react-router-dom';
import { CpuChipIcon } from '@heroicons/react/24/outline';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Logo and Description */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <CpuChipIcon className="h-8 w-8 text-primary-400" />
              <span className="text-xl font-bold">AI Commerce</span>
            </div>
            <p className="text-gray-400 mb-4 max-w-md">
              Experience the future of ecommerce with our AI-powered platform. 
              Automated inventory management, dynamic pricing, and personalized 
              shopping experiences powered by intelligent agents.
            </p>
            <div className="flex items-center space-x-2">
              <CpuChipIcon className="h-5 w-5 text-primary-400 animate-pulse" />
              <span className="text-sm text-gray-400">Powered by AI Agents</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link 
                  to="/products" 
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Products
                </Link>
              </li>
              <li>
                <Link 
                  to="/products?is_featured=true" 
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Featured
                </Link>
              </li>
              <li>
                <Link 
                  to="/cart" 
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Shopping Cart
                </Link>
              </li>
              <li>
                <Link 
                  to="/orders" 
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Order History
                </Link>
              </li>
            </ul>
          </div>

          {/* AI Features */}
          <div>
            <h3 className="text-lg font-semibold mb-4">AI Features</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span>Smart Inventory Management</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span>Dynamic Pricing</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                <span>Personalized Recommendations</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                <span>AI Customer Service</span>
              </li>
              <li className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                <span>Automated Order Processing</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="text-gray-400 text-sm">
            © 2024 AI Commerce. All rights reserved.
          </div>
          <div className="flex items-center space-x-4 mt-4 md:mt-0">
            <span className="text-gray-400 text-sm">Built with</span>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium">FastAPI</span>
              <span className="text-gray-400">•</span>
              <span className="text-sm font-medium">React</span>
              <span className="text-gray-400">•</span>
              <span className="text-sm font-medium">SingleStore</span>
              <span className="text-gray-400">•</span>
              <span className="text-sm font-medium">OpenAI</span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Status Indicator */}
      <div className="bg-gray-800 border-t border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-center space-x-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-gray-400">AI Agents Active</span>
            </div>
            <div className="text-gray-600">|</div>
            <div className="flex items-center space-x-2">
              <CpuChipIcon className="h-4 w-4 text-primary-400" />
              <span className="text-gray-400">Autonomous Operations Enabled</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
