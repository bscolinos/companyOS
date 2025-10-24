import React, { useState, useEffect } from 'react';
import { 
  ComputerDesktopIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  ArrowPathIcon,
  ChartBarIcon,
  CpuChipIcon,
  CircleStackIcon,
  ShieldCheckIcon,
  XCircleIcon,
  BoltIcon,
  EyeIcon,
  SparklesIcon,
  CurrencyDollarIcon,
  ShoppingCartIcon,
  ChatBubbleLeftRightIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';

interface AgentExecution {
  id: string;
  agentName: string;
  operation: string;
  status: 'running' | 'completed' | 'stopped' | 'failed';
  startTime: Date;
  duration: number;
  dataProcessed: number;
}

interface DataOperation {
  id: string;
  table: string;
  operation: 'INSERT' | 'SELECT' | 'UPDATE' | 'DELETE';
  recordsAffected: number;
  timestamp: Date;
  agent: string;
}

interface MonitoringAlert {
  id: string;
  agentName: string;
  reason: string;
  timestamp: Date;
  severity: 'low' | 'medium' | 'high';
  details: {
    description: string;
    affectedOperations: string[];
    confidenceScore?: number;
    accuracy?: number;
    dataQuality?: number;
    recommendation: string;
    impact: string;
  };
}

const AdminMonitoringDashboard: React.FC = () => {
  // Initialize with pre-populated data to simulate ongoing monitoring
  const [selectedAlert, setSelectedAlert] = useState<MonitoringAlert | null>(null);

  const generateAlert = (agentName: string): MonitoringAlert => {
    const alertTypes = [
      {
        reason: 'Low confidence score detected',
        description: 'AI model predictions showing reduced confidence levels below acceptable threshold',
        operations: ['Prediction Generation', 'Model Inference', 'Data Classification'],
        recommendation: 'Review training data quality and consider model retraining',
        impact: 'Reduced prediction accuracy may affect business decisions',
        severity: 'medium' as const,
        confidenceScore: Math.floor(Math.random() * 30) + 45 // 45-75%
      },
      {
        reason: 'Data quality degradation',
        description: 'Input data quality metrics have fallen below monitoring thresholds',
        operations: ['Data Ingestion', 'Feature Engineering', 'Data Validation'],
        recommendation: 'Investigate data sources and implement data quality checks',
        impact: 'Poor data quality may lead to unreliable AI predictions',
        severity: 'high' as const,
        dataQuality: Math.floor(Math.random() * 25) + 60 // 60-85%
      },
      {
        reason: 'Model accuracy drift detected',
        description: 'Significant deviation from baseline accuracy metrics observed',
        operations: ['Model Evaluation', 'Performance Monitoring', 'Prediction Validation'],
        recommendation: 'Analyze recent data patterns and consider model recalibration',
        impact: 'Declining accuracy affects reliability of automated decisions',
        severity: 'high' as const,
        accuracy: Math.floor(Math.random() * 15) + 75 // 75-90%
      },
      {
        reason: 'Anomalous prediction patterns',
        description: 'Unusual clustering or distribution of model predictions detected',
        operations: ['Anomaly Detection', 'Pattern Analysis', 'Statistical Monitoring'],
        recommendation: 'Review input data for unexpected changes or patterns',
        impact: 'May indicate data shift or concept drift affecting performance',
        severity: 'medium' as const
      },
      {
        reason: 'Feature importance shift',
        description: 'Significant changes in feature importance rankings detected',
        operations: ['Feature Analysis', 'Model Interpretation', 'Importance Tracking'],
        recommendation: 'Investigate underlying data changes and validate feature relevance',
        impact: 'May indicate concept drift or data distribution changes',
        severity: 'low' as const
      },
      {
        reason: 'Prediction latency spike',
        description: 'Model inference time has exceeded performance thresholds',
        operations: ['Inference Pipeline', 'Performance Monitoring', 'Resource Allocation'],
        recommendation: 'Optimize model architecture or increase computational resources',
        impact: 'Delayed predictions may affect real-time decision making',
        severity: 'medium' as const
      }
    ];
    
    // 70% chance of low confidence score alert, 30% chance of other alerts
    const alertType = Math.random() < 0.7 
      ? alertTypes[0] // Low confidence score (first in array)
      : alertTypes[Math.floor(Math.random() * (alertTypes.length - 1)) + 1]; // Any other alert
    
    return {
      id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      agentName,
      reason: alertType.reason,
      timestamp: new Date(),
      severity: alertType.severity,
      details: {
        description: alertType.description,
        affectedOperations: alertType.operations,
        confidenceScore: alertType.confidenceScore,
        accuracy: alertType.accuracy,
        dataQuality: alertType.dataQuality,
        recommendation: alertType.recommendation,
        impact: alertType.impact
      }
    };
  };
  
  const [executions, setExecutions] = useState<AgentExecution[]>(() => {
    const agentNames = [
      'InventoryAgent', 'PricingAgent', 'CustomerServiceAgent', 'RecommendationAgent',
      'DataAnalysisAgent', 'MarketingAgent', 'FinancialAnalystAgent', 'SEOAgent', 'SupplyChainAgent'
    ];

    const operations = [
      'Analyzing inventory levels', 'Processing customer data', 'Optimizing pricing strategy',
      'Generating recommendations', 'Updating product catalog', 'Processing orders',
      'Analyzing market trends', 'Optimizing supply chain', 'Managing customer queries',
      'Forecasting demand', 'Calculating ROI', 'SEO optimization'
    ];

    const initialExecutions: AgentExecution[] = [];
    const now = new Date();

    // Generate some running executions (1-3)
    for (let i = 0; i < 1 + Math.floor(Math.random() * 3); i++) {
      const agent = agentNames[Math.floor(Math.random() * agentNames.length)];
      const operation = operations[Math.floor(Math.random() * operations.length)];
      const startTime = new Date(now.getTime() - Math.random() * 15000); // Started up to 15 seconds ago
      const duration = (now.getTime() - startTime.getTime()) / 1000;
      
      initialExecutions.push({
        id: `exec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-${i}`,
        agentName: agent,
        operation,
        status: 'running',
        startTime,
        duration,
        dataProcessed: Math.floor(Math.random() * 50000) + 10000
      });
    }

    // Generate some completed executions (15-20)
    for (let i = 0; i < 15 + Math.floor(Math.random() * 6); i++) {
      const agent = agentNames[Math.floor(Math.random() * agentNames.length)];
      const operation = operations[Math.floor(Math.random() * operations.length)];
      const completedTime = new Date(now.getTime() - Math.random() * 1800000); // Completed up to 30 minutes ago
      const duration = 3 + Math.random() * 12; // 3-15 seconds
      
      initialExecutions.push({
        id: `exec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-comp-${i}`,
        agentName: agent,
        operation,
        status: 'completed',
        startTime: new Date(completedTime.getTime() - duration * 1000),
        duration,
        dataProcessed: Math.floor(Math.random() * 50000) + 10000
      });
    }

    // Generate some stopped executions (2-4)
    for (let i = 0; i < 2 + Math.floor(Math.random() * 3); i++) {
      const agent = agentNames[Math.floor(Math.random() * agentNames.length)];
      const operation = operations[Math.floor(Math.random() * operations.length)];
      const stoppedTime = new Date(now.getTime() - Math.random() * 900000); // Stopped up to 15 minutes ago
      const duration = 1 + Math.random() * 3;
      
      initialExecutions.push({
        id: `exec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-stop-${i}`,
        agentName: agent,
        operation,
        status: 'stopped',
        startTime: new Date(stoppedTime.getTime() - duration * 1000),
        duration,
        dataProcessed: Math.floor(Math.random() * 30000) + 5000
      });
    }

    // Sort by most recent first
    return initialExecutions.sort((a, b) => b.startTime.getTime() - a.startTime.getTime());
  });

  const [dataOps, setDataOps] = useState<DataOperation[]>(() => {
    const agentNames = [
      'InventoryAgent', 'PricingAgent', 'CustomerServiceAgent', 'RecommendationAgent',
      'DataAnalysisAgent', 'MarketingAgent', 'FinancialAnalystAgent', 'SEOAgent', 'SupplyChainAgent'
    ];
    const tables = ['products', 'orders', 'customers', 'inventory', 'analytics', 'pricing', 'recommendations'];
    const initialDataOps: DataOperation[] = [];
    const now = new Date();

    // Generate 20-30 initial data operations from recent executions
    for (let i = 0; i < 20 + Math.floor(Math.random() * 11); i++) {
      const agent = agentNames[Math.floor(Math.random() * agentNames.length)];
      const table = tables[Math.floor(Math.random() * tables.length)];
      // 90% SELECT, 10% INSERT/UPDATE, no DELETE
      const rand = Math.random();
      const operation = rand < 0.9 ? 'SELECT' : (rand < 0.95 ? 'INSERT' : 'UPDATE');
      const timestamp = new Date(now.getTime() - Math.random() * 1800000); // Up to 30 minutes ago
      
      initialDataOps.push({
        id: `data-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-${i}`,
        table,
        operation,
        recordsAffected: Math.floor(Math.random() * 25000) + 5000,
        timestamp,
        agent
      });
    }

    // Sort by most recent first
    return initialDataOps.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  });

  const [alerts, setAlerts] = useState<MonitoringAlert[]>(() => {
    const agentNames = [
      'InventoryAgent', 'PricingAgent', 'CustomerServiceAgent', 'RecommendationAgent',
      'DataAnalysisAgent', 'MarketingAgent', 'FinancialAnalystAgent', 'SEOAgent', 'SupplyChainAgent'
    ];
    
    const initialAlerts: MonitoringAlert[] = [];
    const now = new Date();

    // Generate 1-3 initial alerts using the generateAlert function (fewer for slower pace)
    for (let i = 0; i < 1 + Math.floor(Math.random() * 3); i++) {
      const agent = agentNames[Math.floor(Math.random() * agentNames.length)];
      const timestamp = new Date(now.getTime() - Math.random() * 900000); // Up to 15 minutes ago
      
      // Generate alert and override timestamp
      const alert = generateAlert(agent);
      alert.timestamp = timestamp;
      alert.id = `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}-${i}`;
      
      initialAlerts.push(alert);
    }

    // Sort by most recent first
    return initialAlerts.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  });


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

  useEffect(() => {
    const agentNames = [
      'InventoryAgent', 'PricingAgent', 'CustomerServiceAgent', 'RecommendationAgent',
      'DataAnalysisAgent', 'MarketingAgent', 'FinancialAnalystAgent', 'SEOAgent', 'SupplyChainAgent'
    ];

    const operations = [
      'Analyzing inventory levels', 'Processing customer data', 'Optimizing pricing strategy',
      'Generating recommendations', 'Updating product catalog', 'Processing orders',
      'Analyzing market trends', 'Optimizing supply chain', 'Managing customer queries',
      'Forecasting demand', 'Calculating ROI', 'SEO optimization'
    ];

    const tables = ['products', 'orders', 'customers', 'inventory', 'analytics', 'pricing', 'recommendations'];

    const generateExecution = (): AgentExecution => {
      const agent = agentNames[Math.floor(Math.random() * agentNames.length)];
      const operation = operations[Math.floor(Math.random() * operations.length)];
      
      return {
        id: `exec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        agentName: agent,
        operation,
        status: 'running',
        startTime: new Date(),
        duration: 0,
        dataProcessed: Math.floor(Math.random() * 50000) + 10000 // 10K-60K records
      };
    };

    const generateDataOperation = (agent: string): DataOperation => {
      const table = tables[Math.floor(Math.random() * tables.length)];
      // 90% SELECT, 10% INSERT/UPDATE, no DELETE
      const rand = Math.random();
      const operation = rand < 0.9 ? 'SELECT' : (rand < 0.95 ? 'INSERT' : 'UPDATE');
      
      return {
        id: `data-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        table,
        operation,
        recordsAffected: Math.floor(Math.random() * 25000) + 5000, // 5K-30K records
        timestamp: new Date(),
        agent
      };
    };

    const interval = setInterval(() => {
      // Add new executions to maintain 1-3 running at all times
      setExecutions(prev => {
        const runningCount = prev.filter(e => e.status === 'running').length;
        
        // Always ensure at least 1 running, and randomly add up to 3
        if (runningCount === 0 || (runningCount < 3 && Math.random() < 0.4)) {
          const newExecution = generateExecution();
          return [newExecution, ...prev.slice(0, 49)]; // Keep last 50
        }
        
        return prev;
      });

      // Update existing executions
      setExecutions(prev => prev.map(exec => {
        if (exec.status === 'running') {
          // Increment duration by 2 seconds for each update
          const newDuration = exec.duration + 2;
          
          // Generate database operations while running (30% chance every 2 seconds)
          if (Math.random() < 0.3) {
            const dataOp = generateDataOperation(exec.agentName);
            setDataOps(prevOps => [dataOp, ...prevOps.slice(0, 99)]); // Keep last 100
          }
          
          // 2% chance of being stopped by monitoring (much less frequent)
          if (Math.random() < 0.02) {
            const alert = generateAlert(exec.agentName);
            setAlerts(prevAlerts => [alert, ...prevAlerts.slice(0, 14)]); // Keep last 15
            return { ...exec, status: 'stopped', duration: newDuration };
          }
          
          // Complete after 3-15 seconds
          if (newDuration > 3 + Math.random() * 12) {
            // Generate final data operations when completing
            const numOps = Math.floor(Math.random() * 2) + 1; // 1-2 final operations
            for (let i = 0; i < numOps; i++) {
              setTimeout(() => {
                const dataOp = generateDataOperation(exec.agentName);
                setDataOps(prev => [dataOp, ...prev.slice(0, 99)]); // Keep last 100
              }, i * 200);
            }
            
            return { ...exec, status: 'completed', duration: newDuration };
          }
          
          return { ...exec, duration: newDuration };
        }
        return exec;
      }));
    }, 2000); // Much slower updates (2 seconds instead of 300ms)

    return () => clearInterval(interval);
  }, []);

  const runningExecutions = executions.filter(e => e.status === 'running');
  const completedExecutions = executions.filter(e => e.status === 'completed');
  const stoppedExecutions = executions.filter(e => e.status === 'stopped');

  const recentDataOps = dataOps.slice(0, 10);
  const recentAlerts = alerts.slice(0, 5);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-h-screen bg-dark-900">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <ComputerDesktopIcon className="h-8 w-8 text-primary-600" />
              <h1 className="text-3xl font-bold text-gray-100">Agent Monitoring Dashboard</h1>
            </div>
            <p className="text-gray-300">
              Real-time monitoring of AI agent executions and system operations
            </p>
          </div>
          
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-300">Running</p>
              <p className="text-3xl font-bold text-green-600">{runningExecutions.length}</p>
            </div>
            <ArrowPathIcon className="h-8 w-8 text-green-600 animate-spin" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-300">Completed</p>
              <p className="text-3xl font-bold text-blue-600">{completedExecutions.length}</p>
            </div>
            <CheckCircleIcon className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-300">Stopped</p>
              <p className="text-3xl font-bold text-red-600">{stoppedExecutions.length}</p>
            </div>
            <XCircleIcon className="h-8 w-8 text-red-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-300">Data Ops</p>
              <p className="text-3xl font-bold text-purple-600">{dataOps.length}</p>
            </div>
            <CircleStackIcon className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Active Executions */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-100">Active Executions</h3>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-300">Live</span>
            </div>
          </div>
          
          <div 
            className="space-y-3 max-h-96 overflow-y-auto"
            onWheel={(e) => e.stopPropagation()}
          >
            {runningExecutions.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No active executions</p>
            ) : (
              runningExecutions.map((exec) => {
                const IconComponent = agentIcons[exec.agentName] || CpuChipIcon;
                return (
                  <div key={exec.id} className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                    <div className="flex items-center space-x-3">
                      <IconComponent className="h-5 w-5 text-green-600" />
                      <div>
                        <p className="font-medium text-gray-900">{exec.agentName}</p>
                        <p className="text-sm text-gray-700">{exec.operation}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center space-x-2">
                        <ArrowPathIcon className="h-4 w-4 text-green-600 animate-spin" />
                        <span className="text-sm font-medium text-green-600">{exec.duration.toFixed(1)}s</span>
                      </div>
                      <p className="text-xs text-gray-600">{exec.dataProcessed.toLocaleString()} records</p>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Recent Data Operations */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-100">Database Operations</h3>
            <CircleStackIcon className="h-5 w-5 text-gray-400" />
          </div>
          
          <div 
            className="space-y-2 max-h-96 overflow-y-auto"
            onWheel={(e) => e.stopPropagation()}
          >
            {recentDataOps.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No recent operations</p>
            ) : (
              recentDataOps.map((op) => (
                <div key={op.id} className="flex items-center justify-between p-2 hover:bg-dark-700 rounded">
                  <div className="flex items-center space-x-3">
                    <div className={`px-2 py-1 rounded text-xs font-medium ${
                      op.operation === 'INSERT' ? 'bg-green-100 text-green-800' :
                      op.operation === 'SELECT' ? 'bg-blue-100 text-blue-800' :
                      op.operation === 'UPDATE' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {op.operation}
                    </div>
                    <span className="text-sm font-medium">{op.table}</span>
                    <span className="text-xs text-gray-400">by {op.agent}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{op.recordsAffected.toLocaleString()}</p>
                    <p className="text-xs text-gray-400">
                      {op.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Monitoring Alerts and Recent Executions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
        {/* Monitoring Alerts */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-100">Monitoring Alerts</h3>
            <ShieldCheckIcon className="h-5 w-5 text-gray-400" />
          </div>
          
          <div 
            className="space-y-3 max-h-96 overflow-y-auto"
            onWheel={(e) => e.stopPropagation()}
          >
            {recentAlerts.length === 0 ? (
              <div className="text-center py-8">
                <CheckCircleIcon className="h-12 w-12 text-green-400 mx-auto mb-2" />
                <p className="text-green-600 font-medium">All systems operating normally</p>
              </div>
            ) : (
              recentAlerts.map((alert) => (
                <div 
                  key={alert.id} 
                  onClick={() => setSelectedAlert(alert)}
                  className={`p-3 rounded-lg border-l-4 cursor-pointer hover:shadow-md transition-shadow ${
                    alert.severity === 'high' ? 'bg-red-50 border-red-400 hover:bg-red-100' :
                    alert.severity === 'medium' ? 'bg-yellow-50 border-yellow-400 hover:bg-yellow-100' :
                    'bg-blue-50 border-blue-400 hover:bg-blue-100'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <ExclamationTriangleIcon className={`h-4 w-4 ${
                          alert.severity === 'high' ? 'text-red-600' :
                          alert.severity === 'medium' ? 'text-yellow-600' :
                          'text-blue-600'
                        }`} />
                        <span className="font-medium text-gray-900">{alert.agentName}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          alert.severity === 'high' ? 'bg-red-100 text-red-800' :
                          alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {alert.severity.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-800 mt-1">{alert.reason}</p>
                      <p className="text-xs text-gray-600 mt-1">Click for details</p>
                    </div>
                    <span className="text-xs text-gray-600">
                      {alert.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Execution History */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-100">Recent Executions</h3>
            <ClockIcon className="h-5 w-5 text-gray-400" />
          </div>
          
          <div 
            className="space-y-2 max-h-96 overflow-y-auto"
            onWheel={(e) => e.stopPropagation()}
          >
            {executions.slice(0, 10).map((exec) => {
              const IconComponent = agentIcons[exec.agentName] || CpuChipIcon;
              return (
                <div key={exec.id} className="flex items-center justify-between p-2 hover:bg-dark-700 rounded">
                  <div className="flex items-center space-x-3">
                    <IconComponent className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-400">{exec.agentName}</p>
                      <p className="text-xs text-gray-400">{exec.operation}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center space-x-2">
                      {exec.status === 'running' && (
                        <ArrowPathIcon className="h-3 w-3 text-green-600 animate-spin" />
                      )}
                      {exec.status === 'completed' && (
                        <CheckCircleIcon className="h-3 w-3 text-green-600" />
                      )}
                      {exec.status === 'stopped' && (
                        <XCircleIcon className="h-3 w-3 text-red-600" />
                      )}
                      <span className={`text-xs font-medium ${
                        exec.status === 'running' ? 'text-green-400' :
                        exec.status === 'completed' ? 'text-blue-400' :
                        'text-red-400'
                      }`}>
                        {exec.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400">{exec.duration.toFixed(1)}s</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 bg-black bg-opacity-75 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-dark-800">
            <div className="mt-3">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <ExclamationTriangleIcon className={`h-6 w-6 ${
                    selectedAlert.severity === 'high' ? 'text-red-600' :
                    selectedAlert.severity === 'medium' ? 'text-yellow-600' :
                    'text-blue-600'
                  }`} />
                  <div>
                    <h3 className="text-lg font-semibold text-gray-100">
                      {selectedAlert.reason}
                    </h3>
                    <p className="text-sm text-gray-400">
                      {selectedAlert.agentName} • {selectedAlert.timestamp.toLocaleString()}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="text-gray-400 hover:text-gray-300"
                >
                  <XCircleIcon className="h-6 w-6" />
                </button>
              </div>

              {/* Alert Details */}
              <div className="space-y-6">
                {/* Description */}
                <div>
                  <h4 className="text-sm font-medium text-gray-100 mb-2">Description</h4>
                  <p className="text-sm text-gray-300">{selectedAlert.details.description}</p>
                </div>

                {/* Metrics */}
                {(selectedAlert.details.confidenceScore || selectedAlert.details.accuracy || selectedAlert.details.dataQuality) && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-100 mb-3">Metrics</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {selectedAlert.details.confidenceScore && (
                        <div className="bg-dark-700 p-3 rounded-lg">
                          <p className="text-xs text-gray-400 mb-1">Confidence Score</p>
                          <p className={`text-lg font-semibold ${
                            selectedAlert.details.confidenceScore < 60 ? 'text-red-600' :
                            selectedAlert.details.confidenceScore < 80 ? 'text-yellow-600' :
                            'text-green-600'
                          }`}>
                            {selectedAlert.details.confidenceScore}%
                          </p>
                        </div>
                      )}
                      {selectedAlert.details.accuracy && (
                        <div className="bg-dark-700 p-3 rounded-lg">
                          <p className="text-xs text-gray-400 mb-1">Model Accuracy</p>
                          <p className={`text-lg font-semibold ${
                            selectedAlert.details.accuracy < 80 ? 'text-red-600' :
                            selectedAlert.details.accuracy < 90 ? 'text-yellow-600' :
                            'text-green-600'
                          }`}>
                            {selectedAlert.details.accuracy}%
                          </p>
                        </div>
                      )}
                      {selectedAlert.details.dataQuality && (
                        <div className="bg-dark-700 p-3 rounded-lg">
                          <p className="text-xs text-gray-400 mb-1">Data Quality</p>
                          <p className={`text-lg font-semibold ${
                            selectedAlert.details.dataQuality < 70 ? 'text-red-600' :
                            selectedAlert.details.dataQuality < 85 ? 'text-yellow-600' :
                            'text-green-600'
                          }`}>
                            {selectedAlert.details.dataQuality}%
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Affected Operations */}
                <div>
                  <h4 className="text-sm font-medium text-gray-100 mb-2">Affected Operations</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedAlert.details.affectedOperations.map((operation, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                      >
                        {operation}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Impact */}
                <div>
                  <h4 className="text-sm font-medium text-gray-100 mb-2">Business Impact</h4>
                  <p className="text-sm text-gray-300">{selectedAlert.details.impact}</p>
                </div>

                {/* Recommendation */}
                <div>
                  <h4 className="text-sm font-medium text-gray-100 mb-2">Recommended Action</h4>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-sm text-blue-800">{selectedAlert.details.recommendation}</p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex justify-end space-x-3 pt-4 border-t">
                  <button
                    onClick={() => setSelectedAlert(null)}
                    className="btn-outline"
                  >
                    Close
                  </button>
                  <button className="btn-primary">
                    Mark as Resolved
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminMonitoringDashboard;
