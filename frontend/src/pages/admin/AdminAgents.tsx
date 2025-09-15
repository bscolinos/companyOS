import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  CpuChipIcon, 
  PlayIcon, 
  StopIcon, 
  BoltIcon,
  ChartBarIcon,
  ExclamationCircleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { apiService } from '../../services/api';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import toast from 'react-hot-toast';

const AdminAgents: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const queryClient = useQueryClient();

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

  // Execute agent mutation
  const executeAgentMutation = useMutation({
    mutationFn: ({ agentName, context }: { agentName: string; context?: any }) =>
      apiService.executeAgent(agentName, context),
    onSuccess: (data, variables) => {
      toast.success(`${variables.agentName} executed successfully`);
      queryClient.invalidateQueries({ queryKey: ['agent-status'] });
    },
    onError: (error: any, variables) => {
      toast.error(`Failed to execute ${variables.agentName}: ${error.message}`);
    },
  });

  // Execute all agents mutation
  const executeAllMutation = useMutation({
    mutationFn: (context?: any) => apiService.executeAllAgents(context),
    onSuccess: () => {
      toast.success('All agents executed successfully');
      queryClient.invalidateQueries({ queryKey: ['agent-status'] });
    },
    onError: (error: any) => {
      toast.error(`Failed to execute all agents: ${error.message}`);
    },
  });

  // Toggle agent mutation
  const toggleAgentMutation = useMutation({
    mutationFn: ({ agentName, activate }: { agentName: string; activate: boolean }) =>
      activate ? apiService.activateAgent(agentName) : apiService.deactivateAgent(agentName),
    onSuccess: (data, variables) => {
      toast.success(`${variables.agentName} ${variables.activate ? 'activated' : 'deactivated'}`);
      queryClient.invalidateQueries({ queryKey: ['agent-status'] });
    },
    onError: (error: any, variables) => {
      toast.error(`Failed to ${variables.activate ? 'activate' : 'deactivate'} ${variables.agentName}`);
    },
  });

  const agentDescriptions: { [key: string]: string } = {
    'InventoryAgent': 'Manages stock levels, predicts demand, and automates reordering',
    'PricingAgent': 'Optimizes product pricing based on market conditions and demand',
    'CustomerServiceAgent': 'Handles customer inquiries and support tickets automatically',
    'RecommendationAgent': 'Provides personalized product recommendations to users',
  };

  const agentIcons: { [key: string]: React.ComponentType<any> } = {
    'InventoryAgent': ChartBarIcon,
    'PricingAgent': BoltIcon,
    'CustomerServiceAgent': ExclamationCircleIcon,
    'RecommendationAgent': CheckCircleIcon,
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <CpuChipIcon className="h-8 w-8 text-primary-600" />
              <h1 className="text-3xl font-bold text-gray-900">AI Agents Control Center</h1>
            </div>
            <p className="text-gray-600">
              Monitor and control your autonomous AI agents
            </p>
          </div>
          
          <button
            onClick={() => executeAllMutation.mutate()}
            disabled={executeAllMutation.isPending}
            className="btn-primary disabled:opacity-50"
          >
            {executeAllMutation.isPending ? (
              <LoadingSpinner size="sm" className="mr-2" />
            ) : (
              <PlayIcon className="h-5 w-5 mr-2" />
            )}
            Execute All Agents
          </button>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {agentStatus && Object.entries(agentStatus).map(([name, status]: [string, any]) => {
          const IconComponent = agentIcons[name] || CpuChipIcon;
          
          return (
            <div key={name} className="card border-2 hover:border-primary-200 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`p-3 rounded-lg ${status.is_active ? 'bg-green-100' : 'bg-gray-100'}`}>
                    <IconComponent className={`h-6 w-6 ${status.is_active ? 'text-green-600' : 'text-gray-400'}`} />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {name.replace('Agent', '')} Agent
                    </h3>
                    <p className="text-sm text-gray-500">
                      {agentDescriptions[name] || 'AI-powered automation agent'}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${
                    status.is_active ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                  }`}></div>
                  <span className={`text-sm font-medium ${
                    status.is_active ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {status.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              {/* Agent Stats */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {status.execution_count || 0}
                  </div>
                  <div className="text-sm text-gray-500">Executions</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {status.last_execution ? 'Recent' : 'Never'}
                  </div>
                  <div className="text-sm text-gray-500">Last Run</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <button
                  onClick={() => executeAgentMutation.mutate({ agentName: name })}
                  disabled={executeAgentMutation.isPending || !status.is_active}
                  className="flex-1 btn-primary disabled:opacity-50"
                >
                  {executeAgentMutation.isPending ? (
                    <LoadingSpinner size="sm" className="mr-2" />
                  ) : (
                    <PlayIcon className="h-4 w-4 mr-2" />
                  )}
                  Execute
                </button>
                
                <button
                  onClick={() => toggleAgentMutation.mutate({ 
                    agentName: name, 
                    activate: !status.is_active 
                  })}
                  disabled={toggleAgentMutation.isPending}
                  className={`flex-1 ${status.is_active ? 'btn-error' : 'btn-success'} disabled:opacity-50`}
                >
                  {toggleAgentMutation.isPending ? (
                    <LoadingSpinner size="sm" className="mr-2" />
                  ) : status.is_active ? (
                    <StopIcon className="h-4 w-4 mr-2" />
                  ) : (
                    <PlayIcon className="h-4 w-4 mr-2" />
                  )}
                  {status.is_active ? 'Deactivate' : 'Activate'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Performance Overview */}
      {performance && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Performance Overview
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600 mb-2">
                {performance.total_executions || 0}
              </div>
              <div className="text-sm text-gray-500">Total Executions</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                {performance.success_rate || 0}%
              </div>
              <div className="text-sm text-gray-500">Success Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {performance.average_execution_time || 0}s
              </div>
              <div className="text-sm text-gray-500">Avg Execution Time</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                {Object.keys(agentStatus || {}).length}
              </div>
              <div className="text-sm text-gray-500">Active Agents</div>
            </div>
          </div>

          {/* Individual Agent Performance */}
          <div className="space-y-4">
            <h4 className="text-md font-medium text-gray-900">Agent Performance Breakdown</h4>
            {performance.agent_breakdown && Object.entries(performance.agent_breakdown).map(([agentName, stats]: [string, any]) => (
              <div key={agentName} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
                  <span className="font-medium text-gray-900">{agentName}</span>
                </div>
                <div className="flex items-center space-x-6 text-sm">
                  <div>
                    <span className="text-gray-500">Executions: </span>
                    <span className="font-medium">{stats.executions}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Success Rate: </span>
                    <span className="font-medium text-green-600">{stats.success_rate}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Avg Time: </span>
                    <span className="font-medium">{stats.avg_time}s</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminAgents;
