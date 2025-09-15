import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  CpuChipIcon, 
  ShoppingBagIcon, 
  CurrencyDollarIcon, 
  UsersIcon,
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';

const AdminDashboard: React.FC = () => {
  // Fetch dashboard analytics
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['dashboard-analytics'],
    queryFn: () => apiService.getDashboardAnalytics(30),
  });

  // Fetch AI agent status
  const { data: agentStatus } = useQuery({
    queryKey: ['agent-status'],
    queryFn: () => apiService.getAgentStatus(),
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Revenue',
      value: `$${analytics?.revenue?.total_revenue?.toLocaleString() || '0'}`,
      change: '+12.5%',
      changeType: 'positive',
      icon: CurrencyDollarIcon,
    },
    {
      name: 'Total Orders',
      value: analytics?.revenue?.total_orders?.toLocaleString() || '0',
      change: '+8.2%',
      changeType: 'positive',
      icon: ShoppingBagIcon,
    },
    {
      name: 'Total Users',
      value: analytics?.users?.total_users?.toLocaleString() || '0',
      change: `+${analytics?.users?.growth_rate || 0}%`,
      changeType: 'positive',
      icon: UsersIcon,
    },
    {
      name: 'Low Stock Alerts',
      value: analytics?.products?.low_stock_products || '0',
      change: analytics?.products?.stock_alert_rate ? `${analytics.products.stock_alert_rate}%` : '0%',
      changeType: 'negative',
      icon: ExclamationTriangleIcon,
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <CpuChipIcon className="h-8 w-8 text-primary-600" />
          <h1 className="text-3xl font-bold text-gray-900">AI Commerce Dashboard</h1>
        </div>
        <p className="text-gray-600">
          Monitor your AI-powered ecommerce platform performance
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                <div className="flex items-baseline">
                  <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                  <p className={`ml-2 text-sm font-medium ${
                    stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stat.change}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* AI Agents Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <CpuChipIcon className="h-6 w-6 mr-2 text-primary-600" />
            AI Agents Status
          </h3>
          <div className="space-y-4">
            {agentStatus && Object.entries(agentStatus).map(([name, status]: [string, any]) => (
              <div key={name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    status.is_active ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                  }`}></div>
                  <span className="font-medium text-gray-900">
                    {name.replace('Agent', '')}
                  </span>
                </div>
                <div className="text-sm text-gray-500">
                  {status.execution_count || 0} executions
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Selling Products */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <ChartBarIcon className="h-6 w-6 mr-2 text-primary-600" />
            Top Selling Products
          </h3>
          <div className="space-y-4">
            {analytics?.top_selling_products?.map((product: any, index: number) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">{product.name}</p>
                  <p className="text-sm text-gray-500">{product.units_sold} units sold</p>
                </div>
                <p className="font-semibold text-green-600">
                  ${product.revenue.toLocaleString()}
                </p>
              </div>
            )) || (
              <p className="text-gray-500 text-center py-4">No data available</p>
            )}
          </div>
        </div>
      </div>

      {/* AI Performance Overview */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          AI Performance Overview
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {analytics?.ai_agents?.performance?.map((agent: any) => (
            <div key={agent.agent_name} className="text-center p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">
                {agent.agent_name.replace('Agent', '')}
              </h4>
              <div className="text-2xl font-bold text-primary-600 mb-1">
                {agent.success_rate}%
              </div>
              <p className="text-sm text-gray-500">
                {agent.executions} executions
              </p>
            </div>
          )) || (
            <div className="col-span-3 text-center py-8">
              <p className="text-gray-500">No AI performance data available</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
