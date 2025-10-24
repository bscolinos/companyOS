import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  CpuChipIcon, 
  ShoppingBagIcon, 
  ChartBarIcon, 
  UserGroupIcon,
  SparklesIcon,
  ArrowRightIcon,
  BoltIcon,
  ShieldCheckIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { apiService } from '../services/api';
import { Product } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const HomePage: React.FC = () => {
  // Fetch featured products
  const { data: featuredProducts, isLoading: productsLoading, error: productsError } = useQuery({
    queryKey: ['featured-products'],
    queryFn: () => apiService.getFeaturedProducts(),
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch AI agent status
  const { data: agentStatus } = useQuery({
    queryKey: ['agent-status'],
    queryFn: () => apiService.getAgentStatus(),
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 1,
    staleTime: 30 * 1000, // 30 seconds
  });

  const features = [
    {
      icon: CpuChipIcon,
      title: 'AI-Powered Inventory',
      description: 'Automated stock management with predictive analytics and smart reordering.',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      icon: ChartBarIcon,
      title: 'Dynamic Pricing',
      description: 'Real-time price optimization based on demand, competition, and market conditions.',
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      icon: SparklesIcon,
      title: 'Smart Recommendations',
      description: 'Personalized product suggestions powered by machine learning algorithms.',
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      icon: UserGroupIcon,
      title: 'AI Customer Service',
      description: 'Automated support with intelligent response generation and issue resolution.',
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  const stats = [
    { label: 'Products Managed', value: '10,000+', icon: ShoppingBagIcon },
    { label: 'AI Decisions/Hour', value: '50,000+', icon: BoltIcon },
    { label: 'Uptime', value: '99.9%', icon: ShieldCheckIcon },
    { label: 'Avg Response Time', value: '<100ms', icon: ClockIcon },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-dark-950 via-dark-900 to-primary-900 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-50"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center">
            <div className="flex justify-center mb-8">
              <div className="relative">
                <CpuChipIcon className="h-20 w-20 text-white ai-glow animate-pulse" />
                <div className="absolute -inset-4 bg-white opacity-20 rounded-full animate-ping"></div>
              </div>
            </div>
            
            <h1 className="text-4xl lg:text-6xl font-bold mb-6 text-balance">
              The Future of
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                AI-Powered Commerce
              </span>
            </h1>
            
            <p className="text-xl lg:text-2xl text-gray-200 mb-8 max-w-3xl mx-auto text-balance">
              Experience fully automated ecommerce with intelligent agents managing inventory, 
              pricing, recommendations, and customer service in real-time.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/products"
                className="inline-flex items-center px-8 py-4 bg-primary-600 text-white font-semibold rounded-lg shadow-lg hover:bg-primary-700 transition-all duration-200 transform hover:scale-105"
              >
                <ShoppingBagIcon className="h-5 w-5 mr-2" />
                Shop Now
                <ArrowRightIcon className="h-5 w-5 ml-2" />
              </Link>
              
              <Link
                to="/admin/agents"
                className="inline-flex items-center px-8 py-4 border-2 border-primary-400 text-primary-400 font-semibold rounded-lg hover:bg-primary-400 hover:text-dark-900 transition-all duration-200"
              >
                <CpuChipIcon className="h-5 w-5 mr-2" />
                View AI Agents
              </Link>
            </div>
          </div>
        </div>
        
        {/* Floating AI Status Indicators */}
        <div className="absolute bottom-8 left-8 right-8">
          <div className="flex justify-center space-x-8">
            {agentStatus && Object.keys(agentStatus).length > 0 ? (
              (Object.entries(agentStatus) as [string, any][]).slice(0, 4).map(([name, status]: [string, any]) => (
                <div key={name} className="flex items-center space-x-2 text-sm">
                  <div className={`w-2 h-2 rounded-full ${status.is_active ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                  <span className="text-gray-300">{name.replace('Agent', '')}</span>
                </div>
              ))
            ) : (
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                <span className="text-gray-300">AI Agents Initializing...</span>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-dark-850">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-100 mb-4">
              Powered by Intelligent Agents
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Our AI agents work 24/7 to optimize every aspect of your shopping experience
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center group">
                <div className={`inline-flex items-center justify-center w-16 h-16 ${feature.bgColor} rounded-full mb-6 group-hover:scale-110 transition-transform duration-200`}>
                  <feature.icon className={`h-8 w-8 ${feature.color}`} />
                </div>
                <h3 className="text-xl font-semibold text-gray-100 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-dark-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 rounded-full mb-4">
                  <stat.icon className="h-6 w-6 text-primary-600" />
                </div>
                <div className="text-3xl font-bold text-gray-100 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-400">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-20 bg-dark-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-12">
            <div>
              <h2 className="text-3xl font-bold text-gray-100 mb-2">
                Featured Products
              </h2>
              <p className="text-gray-400">
                AI-curated selection based on demand and trends
              </p>
            </div>
            <Link
              to="/products?is_featured=true"
              className="btn-outline"
            >
              View All
            </Link>
          </div>
          
          {productsLoading ? (
            <div className="flex justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : productsError ? (
            <div className="text-center py-12">
              <ShoppingBagIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-100 mb-2">Products Coming Soon</h3>
              <p className="text-gray-400">We're setting up our AI-powered product catalog.</p>
            </div>
          ) : featuredProducts && featuredProducts.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {(featuredProducts as Product[]).slice(0, 4).map((product: Product) => (
                <Link
                  key={product.id}
                  to={`/products/${product.id}`}
                  className="card-hover group"
                >
                  <div className="aspect-w-1 aspect-h-1 mb-4 overflow-hidden rounded-lg bg-gray-100">
                    {product.images && product.images[0] ? (
                      <img
                        src={product.images[0]}
                        alt={product.name}
                        className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
                      />
                    ) : (
                      <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                        <ShoppingBagIcon className="h-12 w-12 text-gray-400" />
                      </div>
                    )}
                  </div>
                  
                  <h3 className="font-semibold text-gray-100 mb-2 group-hover:text-primary-400 transition-colors">
                    {product.name}
                  </h3>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-primary-600">
                      ${product.price}
                    </span>
                    <div className="flex items-center space-x-1 text-sm text-gray-500">
                      <SparklesIcon className="h-4 w-4" />
                      <span>AI Optimized</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <ShoppingBagIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-100 mb-2">No Products Available</h3>
              <p className="text-gray-400">Check back soon for amazing AI-optimized products!</p>
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-700 to-secondary-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <CpuChipIcon className="h-16 w-16 mx-auto mb-6 animate-pulse" />
          <h2 className="text-3xl lg:text-4xl font-bold mb-4">
            Ready to Experience AI Commerce?
          </h2>
          <p className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
            Join the future of ecommerce with intelligent automation and personalized experiences.
          </p>
          <Link
            to="/register"
            className="inline-flex items-center px-8 py-4 bg-white text-primary-700 font-semibold rounded-lg shadow-lg hover:bg-gray-100 transition-all duration-200 transform hover:scale-105"
          >
            Get Started Today
            <ArrowRightIcon className="h-5 w-5 ml-2" />
          </Link>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
