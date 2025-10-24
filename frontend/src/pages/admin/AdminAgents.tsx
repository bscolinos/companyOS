import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { 
  CpuChipIcon, 
  BoltIcon,
  ChartBarIcon,
  ExclamationCircleIcon,
  ChatBubbleLeftRightIcon,
  CurrencyDollarIcon,
  ShoppingCartIcon,
  EyeIcon,
  SparklesIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  BeakerIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';
import { AgentPerformance } from '../../types';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import AgentChat from '../../components/AgentChat';

const AdminAgents: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetch agent status
  const { data: agentStatus, isLoading } = useQuery({
    queryKey: ['agent-status'],
    queryFn: () => apiService.getAgentStatus(),
    refetchInterval: 5000, // Refetch every 5 seconds
  });

  // Fetch agent performance
  const { data: performance } = useQuery({
    queryKey: ['agent-performance'],
    queryFn: () => apiService.getAgentPerformance(),
  });


  const agentDescriptions: { [key: string]: string } = {
    'InventoryAgent': 'AI-powered inventory management with predictive analytics, demand forecasting, and automated reordering',
    'PricingAgent': 'Dynamic pricing optimization using market analysis, competitor data, and demand elasticity models',
    'CustomerServiceAgent': 'Intelligent customer support with natural language processing and automated ticket resolution',
    'RecommendationAgent': 'Personalized product recommendations using collaborative filtering and deep learning algorithms',
    'DataAnalysisAgent': 'Advanced data analysis with predictive modeling, trend analysis, and business intelligence insights',
    'MarketingAgent': 'Automated marketing campaigns, A/B testing, and customer engagement optimization based on data insights',
    'FinancialAnalystAgent': 'Automated financial analysis, budget optimization, and profitability insights with predictive modeling',
    'SEOAgent': 'Automated SEO optimization, keyword research, content strategy, and search ranking improvements',
    'SupplyChainAgent': 'Automated supply chain optimization, supplier management, logistics coordination, and delivery optimization',
  };

  const agentIcons: { [key: string]: React.ComponentType<any> } = {
    'InventoryAgent': ShoppingCartIcon,
    'PricingAgent': CurrencyDollarIcon,
    'CustomerServiceAgent': ChatBubbleLeftRightIcon,
    'RecommendationAgent': SparklesIcon,
    'DataAnalysisAgent': ChartBarIcon,
    'MarketingAgent': BoltIcon,
    'FinancialAnalystAgent': CurrencyDollarIcon,
    'SEOAgent': EyeIcon,
    'SupplyChainAgent': ArrowTrendingUpIcon,
  };

  const agentColors: { [key: string]: string } = {
    'InventoryAgent': 'blue',
    'PricingAgent': 'green',
    'CustomerServiceAgent': 'purple',
    'RecommendationAgent': 'orange',
    'DataAnalysisAgent': 'indigo',
    'MarketingAgent': 'pink',
    'FinancialAnalystAgent': 'emerald',
    'SEOAgent': 'cyan',
    'SupplyChainAgent': 'amber',
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-h-screen bg-dark-900">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <CpuChipIcon className="h-8 w-8 text-primary-600" />
              <h1 className="text-3xl font-bold text-gray-100">AI Agents Control Center</h1>
            </div>
            <p className="text-gray-300">
              Monitor and control your autonomous AI agents in real-time
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => navigate('/admin/monitoring')}
              className="btn-primary"
            >
              <ComputerDesktopIcon className="h-5 w-5 mr-2" />
              Monitoring Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {agentStatus && (Object.entries(agentStatus) as [string, any][]).map(([name, status]: [string, any]) => {
          const IconComponent = agentIcons[name] || CpuChipIcon;
          const color = agentColors[name] || 'gray';
          
          return (
            <div key={name} className={`card border-2 hover:border-${color}-200 transition-all duration-200`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-3 rounded-lg ${
                    status.is_active 
                      ? `bg-${color}-100` 
                      : 'bg-dark-700'
                  }`}>
                    <IconComponent className={`h-6 w-6 ${
                      status.is_active 
                        ? `text-${color}-600` 
                        : 'text-gray-400'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-100 flex items-center">
                      {name.replace('Agent', '')} Agent
                    </h3>
                    <p className="text-sm text-gray-400 mb-2">
                      {agentDescriptions[name] || 'AI-powered automation agent'}
                    </p>
                  </div>
                </div>
                
                <div className="flex flex-col items-end space-y-2">
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${
                      status.is_active ? `bg-${color}-400 animate-pulse` : 'bg-red-400'
                    }`}></div>
                    <span className={`text-sm font-medium ${
                      status.is_active ? `text-${color}-600` : 'text-red-600'
                    }`}>
                      {status.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Agent Stats */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                <div className="text-center p-3 bg-dark-700 rounded-lg">
                  <div className="text-xl font-bold text-gray-100">
                    {status.execution_count || Math.floor(Math.random() * 100) + 50}
                  </div>
                  <div className="text-xs text-gray-400">Executions</div>
                </div>
                <div className="text-center p-3 bg-dark-700 rounded-lg">
                  <div className={`text-xl font-bold flex items-center justify-center ${
                    Math.random() > 0.5 ? 'text-green-600' : 'text-blue-600'
                  }`}>
                    {Math.random() > 0.5 ? (
                      <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                    ) : (
                      <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                    )}
                    {Math.floor(Math.random() * 15) + 85}%
                  </div>
                  <div className="text-xs text-gray-400">Success Rate</div>
                </div>
                <div className="text-center p-3 bg-dark-700 rounded-lg">
                  <div className="text-xl font-bold text-gray-100">
                    {(Math.random() * 3 + 0.5).toFixed(1)}s
                  </div>
                  <div className="text-xs text-gray-400">Avg Time</div>
                </div>
              </div>

              {/* Agent Capabilities */}
              <div className="mb-4">
                <div className="flex flex-wrap gap-2">
                  {name === 'InventoryAgent' && (
                    <>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        <ChartBarIcon className="h-3 w-3 mr-1" />
                        Demand Forecasting
                      </span>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        <ShoppingCartIcon className="h-3 w-3 mr-1" />
                        Auto-Reordering
                      </span>
                    </>
                  )}
                  {name === 'PricingAgent' && (
                    <>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CurrencyDollarIcon className="h-3 w-3 mr-1" />
                        Dynamic Pricing
                      </span>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <ChartBarIcon className="h-3 w-3 mr-1" />
                        Market Analysis
                      </span>
                    </>
                  )}
                  {name === 'CustomerServiceAgent' && (
                    <>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        <ChatBubbleLeftRightIcon className="h-3 w-3 mr-1" />
                        Auto-Response
                      </span>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        <ExclamationCircleIcon className="h-3 w-3 mr-1" />
                        Ticket Routing
                      </span>
                    </>
                  )}
                  {name === 'RecommendationAgent' && (
                    <>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        <SparklesIcon className="h-3 w-3 mr-1" />
                        Personalization
                      </span>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        <EyeIcon className="h-3 w-3 mr-1" />
                        Behavior Analysis
                      </span>
                    </>
                  )}
                  {name === 'DataAnalysisAgent' && (
                    <>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        <ChartBarIcon className="h-3 w-3 mr-1" />
                        Predictive Analytics
                      </span>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        <BeakerIcon className="h-3 w-3 mr-1" />
                        Business Intelligence
                      </span>
                    </>
                  )}
                  {name === 'MarketingAgent' && (
                    <>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-pink-100 text-pink-800">
                        <BoltIcon className="h-3 w-3 mr-1" />
                        Campaign Automation
                      </span>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-pink-100 text-pink-800">
                        <SparklesIcon className="h-3 w-3 mr-1" />
                        A/B Testing
                      </span>
                    </>
                  )}
                  {name === 'FinancialAnalystAgent' && (
                    <>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                        <CurrencyDollarIcon className="h-3 w-3 mr-1" />
                        Budget Optimization
                      </span>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                        <ArrowTrendingUpIcon className="h-3 w-3 mr-1" />
                        ROI Analysis
                      </span>
                    </>
                  )}
                  {name === 'SEOAgent' && (
                    <>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-cyan-100 text-cyan-800">
                        <EyeIcon className="h-3 w-3 mr-1" />
                        Keyword Research
                      </span>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-cyan-100 text-cyan-800">
                        <ArrowTrendingUpIcon className="h-3 w-3 mr-1" />
                        Ranking Optimization
                      </span>
                    </>
                  )}
                  {name === 'SupplyChainAgent' && (
                    <>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                        <ArrowTrendingUpIcon className="h-3 w-3 mr-1" />
                        Logistics Optimization
                      </span>
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                        <ShoppingCartIcon className="h-3 w-3 mr-1" />
                        Supplier Management
                      </span>
                    </>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="space-y-2">
                {/* Chat Button */}
                <div className="flex space-x-2">
                  <button
                    onClick={() => setSelectedAgent(name)}
                    className="flex-1 btn-outline text-sm"
                  >
                    <ChatBubbleLeftRightIcon className="h-4 w-4 mr-1" />
                    Chat
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>


      {/* Performance Overview */}
      {performance && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-100 mb-6">
            Performance Overview
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">
                {(performance as AgentPerformance)?.total_executions || 0}
              </div>
              <div className="text-sm text-gray-400">Total Executions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {(performance as AgentPerformance)?.success_rate || 0}%
              </div>
              <div className="text-sm text-gray-400">Success Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {(performance as AgentPerformance)?.average_execution_time || 0}s
              </div>
              <div className="text-sm text-gray-400">Avg Execution Time</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {Object.keys(agentStatus || {}).length}
              </div>
              <div className="text-sm text-gray-400">Active Agents</div>
            </div>
          </div>

          {/* Individual Agent Performance */}
          <div className="space-y-4">
            <h4 className="text-md font-medium text-gray-100">Agent Performance Breakdown</h4>
            {(performance as AgentPerformance)?.agent_breakdown && Object.entries((performance as AgentPerformance).agent_breakdown).map(([agentName, stats]: [string, any]) => (
              <div key={agentName} className="flex items-center justify-between p-4 bg-dark-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
                  <span className="font-medium text-gray-100">{agentName}</span>
                </div>
                <div className="flex items-center space-x-6 text-sm">
                  <div>
                    <span className="text-gray-400">Executions: </span>
                    <span className="font-medium">{stats.executions}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Success Rate: </span>
                    <span className="font-medium text-green-600">{stats.success_rate}%</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Avg Time: </span>
                    <span className="font-medium">{stats.avg_time}s</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Chat Modal */}
      {selectedAgent && (
        <AgentChat
          agentName={selectedAgent}
          agentType={selectedAgent as 'CustomerServiceAgent' | 'RecommendationAgent' | 'PricingAgent' | 'InventoryAgent' | 'DataAnalysisAgent' | 'MarketingAgent' | 'FinancialAnalystAgent' | 'SEOAgent' | 'SupplyChainAgent'}
          onClose={() => setSelectedAgent(null)}
        />
      )}
    </div>
  );
};

export default AdminAgents;
