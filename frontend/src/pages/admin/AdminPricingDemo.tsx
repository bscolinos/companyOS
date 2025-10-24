import React, { useState, useEffect } from 'react';
import {
  CurrencyDollarIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  BoltIcon,
  EyeIcon,
  PlayIcon,
  PauseIcon,
  BeakerIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

interface Product {
  id: number;
  name: string;
  category: string;
  currentPrice: number;
  originalPrice: number;
  suggestedPrice: number;
  demand: number;
  competition: number;
  elasticity: number;
  margin: number;
  sales: number;
  trend: 'up' | 'down' | 'stable';
  confidence: number;
  reason: string;
}

const AdminPricingDemo: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [marketConditions, setMarketConditions] = useState({
    trend: 'bullish',
    demandIndex: 85,
    competitionLevel: 'moderate',
    seasonalFactor: 1.12
  });

  // Initialize demo products
  useEffect(() => {
    const demoProducts: Product[] = [
      {
        id: 1,
        name: 'Wireless Bluetooth Earbuds',
        category: 'Electronics',
        currentPrice: 79.99,
        originalPrice: 79.99,
        suggestedPrice: 84.99,
        demand: 92,
        competition: 78,
        elasticity: -1.2,
        margin: 35,
        sales: 145,
        trend: 'up',
        confidence: 0.89,
        reason: 'High demand, low competitor pricing, strong sales velocity'
      },
      {
        id: 2,
        name: 'Smart Home Security Camera',
        category: 'Home & Garden',
        currentPrice: 149.99,
        originalPrice: 149.99,
        suggestedPrice: 139.99,
        demand: 67,
        competition: 85,
        elasticity: -0.8,
        margin: 28,
        sales: 89,
        trend: 'down',
        confidence: 0.76,
        reason: 'Increased competition, price sensitive segment'
      },
      {
        id: 3,
        name: 'Organic Cotton T-Shirt',
        category: 'Fashion',
        currentPrice: 24.99,
        originalPrice: 24.99,
        suggestedPrice: 27.99,
        demand: 88,
        competition: 45,
        elasticity: -1.8,
        margin: 42,
        sales: 203,
        trend: 'up',
        confidence: 0.94,
        reason: 'Sustainable products trending, low competition'
      },
      {
        id: 4,
        name: 'Stainless Steel Water Bottle',
        category: 'Sports & Outdoors',
        currentPrice: 19.99,
        originalPrice: 19.99,
        suggestedPrice: 19.99,
        demand: 75,
        competition: 82,
        elasticity: -1.1,
        margin: 38,
        sales: 167,
        trend: 'stable',
        confidence: 0.65,
        reason: 'Optimal price point, maintain current pricing'
      },
      {
        id: 5,
        name: 'LED Desk Lamp with USB Charging',
        category: 'Home & Office',
        currentPrice: 45.99,
        originalPrice: 45.99,
        suggestedPrice: 49.99,
        demand: 83,
        competition: 62,
        elasticity: -0.9,
        margin: 31,
        sales: 124,
        trend: 'up',
        confidence: 0.82,
        reason: 'Back-to-office trend, unique features justify premium'
      },
      {
        id: 6,
        name: 'Yoga Mat Premium',
        category: 'Sports & Outdoors',
        currentPrice: 34.99,
        originalPrice: 34.99,
        suggestedPrice: 31.99,
        demand: 58,
        competition: 91,
        elasticity: -1.5,
        margin: 25,
        sales: 78,
        trend: 'down',
        confidence: 0.71,
        reason: 'High competition, seasonal decline in fitness products'
      }
    ];
    setProducts(demoProducts);
  }, []);

  // Simulate real-time price optimization
  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      setProducts(prevProducts => 
        prevProducts.map(product => {
          // Simulate market changes
          const demandChange = (Math.random() - 0.5) * 10;
          const competitionChange = (Math.random() - 0.5) * 8;
          const newDemand = Math.max(30, Math.min(100, product.demand + demandChange));
          const newCompetition = Math.max(30, Math.min(100, product.competition + competitionChange));
          
          // Calculate new suggested price based on changes
          let priceMultiplier = 1;
          if (newDemand > 80 && newCompetition < 70) {
            priceMultiplier = 1.05; // Increase price
          } else if (newDemand < 60 || newCompetition > 85) {
            priceMultiplier = 0.96; // Decrease price
          }
          
          const newSuggestedPrice = Math.round(product.originalPrice * priceMultiplier * 100) / 100;
          const newTrend = newSuggestedPrice > product.currentPrice ? 'up' : 
                          newSuggestedPrice < product.currentPrice ? 'down' : 'stable';
          
          return {
            ...product,
            demand: Math.round(newDemand),
            competition: Math.round(newCompetition),
            suggestedPrice: newSuggestedPrice,
            trend: newTrend,
            confidence: Math.max(0.6, Math.min(0.95, Math.random() * 0.4 + 0.6))
          };
        })
      );

      // Update market conditions
      setMarketConditions(prev => ({
        ...prev,
        demandIndex: Math.max(60, Math.min(95, prev.demandIndex + (Math.random() - 0.5) * 5)),
        seasonalFactor: Math.max(0.9, Math.min(1.3, prev.seasonalFactor + (Math.random() - 0.5) * 0.05))
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, [isRunning]);

  const applyPriceChange = (productId: number) => {
    setProducts(prevProducts =>
      prevProducts.map(product =>
        product.id === productId
          ? { ...product, currentPrice: product.suggestedPrice }
          : product
      )
    );
    toast.success('Price updated successfully! 💰');
  };

  const applyAllPriceChanges = () => {
    setProducts(prevProducts =>
      prevProducts.map(product => ({
        ...product,
        currentPrice: product.suggestedPrice
      }))
    );
    toast.success('All prices updated! 🚀 Total optimization impact: +12.3% revenue');
  };

  const getPriceChangePercent = (current: number, suggested: number) => {
    return ((suggested - current) / current * 100);
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up':
        return <ArrowTrendingUpIcon className="h-4 w-4 text-green-600" />;
      case 'down':
        return <ArrowTrendingDownIcon className="h-4 w-4 text-red-600" />;
      default:
        return <div className="h-4 w-4 bg-gray-400 rounded-full"></div>;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
              <h1 className="text-3xl font-bold text-gray-900">Dynamic Pricing Demo</h1>
              {isRunning && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 animate-pulse">
                  <BoltIcon className="h-4 w-4 mr-1" />
                  Live Optimization
                </span>
              )}
            </div>
            <p className="text-gray-600">
              Watch AI-powered pricing optimization in action with real-time market analysis
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => setIsRunning(!isRunning)}
              className={`btn-primary ${isRunning ? 'bg-red-600 hover:bg-red-700' : ''}`}
            >
              {isRunning ? (
                <>
                  <PauseIcon className="h-5 w-5 mr-2" />
                  Stop Demo
                </>
              ) : (
                <>
                  <PlayIcon className="h-5 w-5 mr-2" />
                  Start Demo
                </>
              )}
            </button>
            
            <button
              onClick={applyAllPriceChanges}
              className="btn-success"
            >
              <CheckCircleIcon className="h-5 w-5 mr-2" />
              Apply All Changes
            </button>
          </div>
        </div>
      </div>

      {/* Market Conditions Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Market Trend</p>
              <p className="text-2xl font-bold text-green-600 capitalize">{marketConditions.trend}</p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-green-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Demand Index</p>
              <p className="text-2xl font-bold text-blue-600">{Math.round(marketConditions.demandIndex)}</p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Competition</p>
              <p className="text-2xl font-bold text-orange-600 capitalize">{marketConditions.competitionLevel}</p>
            </div>
            <EyeIcon className="h-8 w-8 text-orange-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Seasonal Factor</p>
              <p className="text-2xl font-bold text-purple-600">{marketConditions.seasonalFactor.toFixed(2)}x</p>
            </div>
            <SparklesIcon className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {products.map((product) => {
          const priceChangePercent = getPriceChangePercent(product.currentPrice, product.suggestedPrice);
          const hasSignificantChange = Math.abs(priceChangePercent) >= 1;
          
          return (
            <div
              key={product.id}
              className={`card hover:shadow-lg transition-all duration-200 ${
                hasSignificantChange ? 'ring-2 ring-green-100 border-green-200' : ''
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">{product.name}</h3>
                  <p className="text-sm text-gray-500 mb-2">{product.category}</p>
                  
                  {/* Current vs Suggested Price */}
                  <div className="flex items-center space-x-4 mb-3">
                    <div>
                      <p className="text-xs text-gray-500">Current</p>
                      <p className="text-lg font-bold text-gray-900">${product.currentPrice}</p>
                    </div>
                    <ArrowTrendingRightIcon className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">Suggested</p>
                      <p className={`text-lg font-bold ${
                        product.suggestedPrice > product.currentPrice ? 'text-green-600' : 
                        product.suggestedPrice < product.currentPrice ? 'text-red-600' : 'text-gray-900'
                      }`}>
                        ${product.suggestedPrice}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="flex flex-col items-end space-y-2">
                  {getTrendIcon(product.trend)}
                  <span className={`text-sm font-medium ${getConfidenceColor(product.confidence)}`}>
                    {Math.round(product.confidence * 100)}%
                  </span>
                </div>
              </div>

              {/* Price Change Indicator */}
              {hasSignificantChange && (
                <div className={`mb-4 p-2 rounded-lg ${
                  priceChangePercent > 0 ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className={`text-sm font-medium ${
                      priceChangePercent > 0 ? 'text-green-700' : 'text-red-700'
                    }`}>
                      {priceChangePercent > 0 ? '+' : ''}{priceChangePercent.toFixed(1)}% change
                    </span>
                    {priceChangePercent > 0 ? (
                      <ArrowTrendingUpIcon className="h-4 w-4 text-green-600" />
                    ) : (
                      <ArrowTrendingDownIcon className="h-4 w-4 text-red-600" />
                    )}
                  </div>
                </div>
              )}

              {/* Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center p-2 bg-gray-50 rounded">
                  <div className="text-lg font-bold text-blue-600">{product.demand}</div>
                  <div className="text-xs text-gray-500">Demand</div>
                </div>
                <div className="text-center p-2 bg-gray-50 rounded">
                  <div className="text-lg font-bold text-orange-600">{product.competition}</div>
                  <div className="text-xs text-gray-500">Competition</div>
                </div>
              </div>

              {/* AI Reasoning */}
              <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                <div className="flex items-start space-x-2">
                  <SparklesIcon className="h-4 w-4 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-xs text-blue-600 font-medium mb-1">AI Analysis</p>
                    <p className="text-xs text-blue-700">{product.reason}</p>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <button
                  onClick={() => setSelectedProduct(product)}
                  className="flex-1 btn-outline text-sm"
                >
                  <EyeIcon className="h-4 w-4 mr-1" />
                  Details
                </button>
                
                {hasSignificantChange && (
                  <button
                    onClick={() => applyPriceChange(product.id)}
                    className={`flex-1 text-sm ${
                      priceChangePercent > 0 ? 'btn-success' : 'btn-error'
                    }`}
                  >
                    <CheckCircleIcon className="h-4 w-4 mr-1" />
                    Apply
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-4/5 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-900">{selectedProduct.name}</h3>
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Detailed Metrics */}
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Pricing Analysis</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Current Price</span>
                      <span className="font-medium">${selectedProduct.currentPrice}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Suggested Price</span>
                      <span className="font-medium text-green-600">${selectedProduct.suggestedPrice}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Price Elasticity</span>
                      <span className="font-medium">{selectedProduct.elasticity}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Profit Margin</span>
                      <span className="font-medium">{selectedProduct.margin}%</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Market Metrics</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Demand Score</span>
                      <span className="font-medium">{selectedProduct.demand}/100</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Competition Level</span>
                      <span className="font-medium">{selectedProduct.competition}/100</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Sales Velocity</span>
                      <span className="font-medium">{selectedProduct.sales} units/month</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">AI Confidence</span>
                      <span className={`font-medium ${getConfidenceColor(selectedProduct.confidence)}`}>
                        {Math.round(selectedProduct.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* AI Recommendation */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg mb-6">
                <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
                  <SparklesIcon className="h-5 w-5 text-blue-600 mr-2" />
                  AI Recommendation
                </h4>
                <p className="text-gray-700">{selectedProduct.reason}</p>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    applyPriceChange(selectedProduct.id);
                    setSelectedProduct(null);
                  }}
                  className="flex-1 btn-primary"
                >
                  Apply Price Change
                </button>
                <button
                  onClick={() => setSelectedProduct(null)}
                  className="flex-1 btn-outline"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper component for arrow icon
const ArrowTrendingRightIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
  </svg>
);

export default AdminPricingDemo;
