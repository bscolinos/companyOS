import React, { useState, useEffect } from 'react';
import {
  SparklesIcon,
  UserIcon,
  ShoppingBagIcon,
  HeartIcon,
  EyeIcon,
  PlayIcon,
  PauseIcon,
  BeakerIcon,
  ChartBarIcon,
  ArrowTrendingUpIcon,
  CpuChipIcon,
  UserGroupIcon,
  StarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

interface User {
  id: number;
  name: string;
  email: string;
  avatar: string;
  segment: string;
  preferences: string[];
  purchaseHistory: number;
  lastActive: string;
}

interface Product {
  id: number;
  name: string;
  category: string;
  price: number;
  rating: number;
  image: string;
  tags: string[];
}

interface Recommendation {
  id: string;
  userId: number;
  productId: number;
  score: number;
  reason: string;
  algorithm: 'collaborative' | 'content_based' | 'ai_powered' | 'hybrid';
  confidence: number;
  timestamp: Date;
}

const AdminRecommendations: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [metrics, setMetrics] = useState({
    totalRecommendations: 0,
    clickThroughRate: 0,
    conversionRate: 0,
    avgConfidence: 0
  });

  // Initialize demo data
  useEffect(() => {
    const demoUsers: User[] = [
      {
        id: 1,
        name: 'Sarah Chen',
        email: 'sarah@example.com',
        avatar: '👩‍💻',
        segment: 'Tech Enthusiast',
        preferences: ['Electronics', 'Gadgets', 'Smart Home'],
        purchaseHistory: 12,
        lastActive: '2 hours ago'
      },
      {
        id: 2,
        name: 'Mike Rodriguez',
        email: 'mike@example.com',
        avatar: '🏃‍♂️',
        segment: 'Fitness Focused',
        preferences: ['Sports', 'Health', 'Outdoors'],
        purchaseHistory: 8,
        lastActive: '1 day ago'
      },
      {
        id: 3,
        name: 'Emma Johnson',
        email: 'emma@example.com',
        avatar: '👩‍🎨',
        segment: 'Creative Professional',
        preferences: ['Art', 'Design', 'Home Decor'],
        purchaseHistory: 15,
        lastActive: '30 minutes ago'
      },
      {
        id: 4,
        name: 'David Kim',
        email: 'david@example.com',
        avatar: '👨‍🍳',
        segment: 'Home Chef',
        preferences: ['Kitchen', 'Cooking', 'Food'],
        purchaseHistory: 6,
        lastActive: '3 hours ago'
      },
      {
        id: 5,
        name: 'Lisa Thompson',
        email: 'lisa@example.com',
        avatar: '👩‍🌾',
        segment: 'Eco Conscious',
        preferences: ['Sustainable', 'Organic', 'Green Living'],
        purchaseHistory: 10,
        lastActive: '1 hour ago'
      }
    ];

    const demoProducts: Product[] = [
      { id: 1, name: 'Smart Watch Pro', category: 'Electronics', price: 299.99, rating: 4.8, image: '⌚', tags: ['smart', 'fitness', 'tech'] },
      { id: 2, name: 'Wireless Earbuds', category: 'Electronics', price: 149.99, rating: 4.6, image: '🎧', tags: ['audio', 'wireless', 'portable'] },
      { id: 3, name: 'Yoga Mat Premium', category: 'Sports', price: 79.99, rating: 4.7, image: '🧘', tags: ['yoga', 'fitness', 'wellness'] },
      { id: 4, name: 'Organic Coffee Beans', category: 'Food', price: 24.99, rating: 4.9, image: '☕', tags: ['organic', 'coffee', 'fair-trade'] },
      { id: 5, name: 'LED Desk Lamp', category: 'Home Office', price: 89.99, rating: 4.5, image: '💡', tags: ['lighting', 'office', 'adjustable'] },
      { id: 6, name: 'Bamboo Cutting Board', category: 'Kitchen', price: 34.99, rating: 4.8, image: '🔪', tags: ['bamboo', 'sustainable', 'kitchen'] },
      { id: 7, name: 'Canvas Art Print', category: 'Home Decor', price: 59.99, rating: 4.4, image: '🖼️', tags: ['art', 'decor', 'wall'] },
      { id: 8, name: 'Protein Powder', category: 'Health', price: 49.99, rating: 4.6, image: '💪', tags: ['protein', 'fitness', 'nutrition'] }
    ];

    setUsers(demoUsers);
    setProducts(demoProducts);
    setSelectedUser(demoUsers[0]);
  }, []);

  // Generate recommendations for selected user
  const generateRecommendations = (user: User) => {
    const userPrefs = user.preferences;
    const newRecommendations: Recommendation[] = [];
    
    // Collaborative filtering recommendations
    const collaborativeProducts = products.filter(p => 
      userPrefs.some(pref => p.tags.includes(pref.toLowerCase()) || p.category.toLowerCase().includes(pref.toLowerCase()))
    ).slice(0, 3);

    collaborativeProducts.forEach((product, index) => {
      newRecommendations.push({
        id: `collab-${user.id}-${product.id}`,
        userId: user.id,
        productId: product.id,
        score: 0.8 + Math.random() * 0.2,
        reason: 'Users with similar interests also bought this',
        algorithm: 'collaborative',
        confidence: 0.75 + Math.random() * 0.2,
        timestamp: new Date()
      });
    });

    // Content-based recommendations
    const contentProducts = products.filter(p => 
      !collaborativeProducts.includes(p) && 
      (userPrefs.some(pref => p.name.toLowerCase().includes(pref.toLowerCase())) || 
       p.rating > 4.5)
    ).slice(0, 2);

    contentProducts.forEach(product => {
      newRecommendations.push({
        id: `content-${user.id}-${product.id}`,
        userId: user.id,
        productId: product.id,
        score: 0.7 + Math.random() * 0.25,
        reason: 'Matches your interests and preferences',
        algorithm: 'content_based',
        confidence: 0.7 + Math.random() * 0.25,
        timestamp: new Date()
      });
    });

    // AI-powered recommendations
    const aiProducts = products.filter(p => 
      !collaborativeProducts.includes(p) && !contentProducts.includes(p)
    ).slice(0, 2);

    aiProducts.forEach(product => {
      newRecommendations.push({
        id: `ai-${user.id}-${product.id}`,
        userId: user.id,
        productId: product.id,
        score: 0.6 + Math.random() * 0.3,
        reason: 'AI detected emerging trend in your segment',
        algorithm: 'ai_powered',
        confidence: 0.6 + Math.random() * 0.3,
        timestamp: new Date()
      });
    });

    return newRecommendations.sort((a, b) => b.score - a.score);
  };

  // Real-time recommendation updates
  useEffect(() => {
    if (!isRunning || !selectedUser) return;

    const interval = setInterval(() => {
      const newRecommendations = generateRecommendations(selectedUser);
      setRecommendations(newRecommendations);
      
      // Update metrics
      setMetrics(prev => ({
        totalRecommendations: prev.totalRecommendations + Math.floor(Math.random() * 5) + 1,
        clickThroughRate: Math.max(8, Math.min(25, prev.clickThroughRate + (Math.random() - 0.5) * 2)),
        conversionRate: Math.max(2, Math.min(8, prev.conversionRate + (Math.random() - 0.5) * 0.5)),
        avgConfidence: newRecommendations.reduce((sum, rec) => sum + rec.confidence, 0) / newRecommendations.length
      }));

      toast.success(`🎯 Generated ${newRecommendations.length} new recommendations for ${selectedUser.name}`);
    }, 5000);

    return () => clearInterval(interval);
  }, [isRunning, selectedUser, products]);

  // Initial recommendations for selected user
  useEffect(() => {
    if (selectedUser) {
      const initialRecommendations = generateRecommendations(selectedUser);
      setRecommendations(initialRecommendations);
      
      setMetrics({
        totalRecommendations: 1247,
        clickThroughRate: 18.5,
        conversionRate: 4.2,
        avgConfidence: initialRecommendations.reduce((sum, rec) => sum + rec.confidence, 0) / initialRecommendations.length
      });
    }
  }, [selectedUser]);

  const getAlgorithmColor = (algorithm: string) => {
    const colors = {
      collaborative: 'blue',
      content_based: 'green',
      ai_powered: 'purple',
      hybrid: 'orange'
    };
    return colors[algorithm as keyof typeof colors] || 'gray';
  };

  const getAlgorithmIcon = (algorithm: string) => {
    const icons = {
      collaborative: UserGroupIcon,
      content_based: ChartBarIcon,
      ai_powered: CpuChipIcon,
      hybrid: SparklesIcon
    };
    return icons[algorithm as keyof typeof icons] || SparklesIcon;
  };

  const getProductById = (productId: number) => {
    return products.find(p => p.id === productId);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <SparklesIcon className="h-8 w-8 text-purple-600" />
              <h1 className="text-3xl font-bold text-gray-900">AI Recommendations Engine</h1>
              {isRunning && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 animate-pulse">
                  <CpuChipIcon className="h-4 w-4 mr-1" />
                  Live Personalization
                </span>
              )}
            </div>
            <p className="text-gray-600">
              Real-time personalized product recommendations powered by machine learning
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
          </div>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Recommendations</p>
              <p className="text-2xl font-bold text-purple-600">{metrics.totalRecommendations.toLocaleString()}</p>
            </div>
            <SparklesIcon className="h-8 w-8 text-purple-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Click-Through Rate</p>
              <p className="text-2xl font-bold text-blue-600">{metrics.clickThroughRate.toFixed(1)}%</p>
            </div>
            <EyeIcon className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Conversion Rate</p>
              <p className="text-2xl font-bold text-green-600">{metrics.conversionRate.toFixed(1)}%</p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Avg Confidence</p>
              <p className="text-2xl font-bold text-orange-600">{(metrics.avgConfidence * 100).toFixed(0)}%</p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-orange-600" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* User Selection */}
        <div className="lg:col-span-1">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <UserIcon className="h-5 w-5 mr-2 text-gray-600" />
              Select Customer
            </h3>
            
            <div className="space-y-3">
              {users.map(user => (
                <div
                  key={user.id}
                  onClick={() => setSelectedUser(user)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedUser?.id === user.id 
                      ? 'bg-purple-50 border border-purple-200' 
                      : 'hover:bg-gray-50 border border-transparent'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">{user.avatar}</div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{user.name}</h4>
                      <p className="text-sm text-gray-500">{user.segment}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-400">{user.purchaseHistory} orders</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-400">{user.lastActive}</span>
                      </div>
                    </div>
                    {selectedUser?.id === user.id && (
                      <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                    )}
                  </div>
                  
                  {/* User Preferences */}
                  <div className="mt-2 flex flex-wrap gap-1">
                    {user.preferences.slice(0, 3).map(pref => (
                      <span key={pref} className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                        {pref}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <SparklesIcon className="h-5 w-5 mr-2 text-purple-600" />
                Personalized Recommendations
                {selectedUser && (
                  <span className="ml-2 text-sm text-gray-500">for {selectedUser.name}</span>
                )}
              </h3>
              
              {isRunning && (
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <ClockIcon className="h-4 w-4 animate-spin" />
                  <span>Updating...</span>
                </div>
              )}
            </div>

            {selectedUser ? (
              <div className="space-y-4">
                {recommendations.map(recommendation => {
                  const product = getProductById(recommendation.productId);
                  const AlgorithmIcon = getAlgorithmIcon(recommendation.algorithm);
                  const algorithmColor = getAlgorithmColor(recommendation.algorithm);
                  
                  if (!product) return null;
                  
                  return (
                    <div
                      key={recommendation.id}
                      className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start space-x-4">
                        {/* Product Image */}
                        <div className="text-4xl">{product.image}</div>
                        
                        {/* Product Info */}
                        <div className="flex-1">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <h4 className="font-semibold text-gray-900">{product.name}</h4>
                              <p className="text-sm text-gray-500">{product.category}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-bold text-lg text-gray-900">${product.price}</p>
                              <div className="flex items-center space-x-1">
                                <StarIcon className="h-4 w-4 text-yellow-400 fill-current" />
                                <span className="text-sm text-gray-600">{product.rating}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Recommendation Score & Algorithm */}
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center space-x-2">
                              <div className={`p-1 rounded-full bg-${algorithmColor}-100`}>
                                <AlgorithmIcon className={`h-4 w-4 text-${algorithmColor}-600`} />
                              </div>
                              <span className="text-sm text-gray-600 capitalize">
                                {recommendation.algorithm.replace('_', ' ')}
                              </span>
                            </div>
                            
                            <div className="flex items-center space-x-4">
                              <div className="text-right">
                                <span className="text-xs text-gray-500">Score</span>
                                <div className={`text-sm font-bold text-${algorithmColor}-600`}>
                                  {Math.round(recommendation.score * 100)}%
                                </div>
                              </div>
                              <div className="text-right">
                                <span className="text-xs text-gray-500">Confidence</span>
                                <div className="text-sm font-bold text-gray-900">
                                  {Math.round(recommendation.confidence * 100)}%
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          {/* AI Reasoning */}
                          <div className={`bg-${algorithmColor}-50 p-3 rounded-lg mb-3`}>
                            <div className="flex items-start space-x-2">
                              <CpuChipIcon className={`h-4 w-4 text-${algorithmColor}-600 mt-0.5`} />
                              <div>
                                <p className={`text-xs text-${algorithmColor}-600 font-medium mb-1`}>
                                  AI Analysis
                                </p>
                                <p className={`text-xs text-${algorithmColor}-700`}>
                                  {recommendation.reason}
                                </p>
                              </div>
                            </div>
                          </div>
                          
                          {/* Product Tags */}
                          <div className="flex flex-wrap gap-1 mb-3">
                            {product.tags.map(tag => (
                              <span key={tag} className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                                #{tag}
                              </span>
                            ))}
                          </div>
                          
                          {/* Action Buttons */}
                          <div className="flex space-x-2">
                            <button className="btn-primary text-sm">
                              <ShoppingBagIcon className="h-4 w-4 mr-1" />
                              Add to Cart
                            </button>
                            <button className="btn-outline text-sm">
                              <HeartIcon className="h-4 w-4 mr-1" />
                              Save
                            </button>
                            <button className="btn-outline text-sm">
                              <EyeIcon className="h-4 w-4 mr-1" />
                              View Details
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
                
                {recommendations.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <SparklesIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Generating Recommendations
                    </h3>
                    <p>AI is analyzing user preferences and behavior patterns...</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <UserIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Select a Customer
                </h3>
                <p>Choose a customer from the list to see personalized recommendations.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminRecommendations;
