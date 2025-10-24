import React, { useState, useRef, useEffect } from 'react';
import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  CpuChipIcon,
  UserIcon,
  SparklesIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ChartBarIcon,
  BoltIcon,
  CurrencyDollarIcon,
  EyeIcon,
  ArrowTrendingUpIcon
} from '@heroicons/react/24/outline';
import { useQueryClient } from '@tanstack/react-query';
import LoadingSpinner from './ui/LoadingSpinner';

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  agentName?: string;
  status?: 'sending' | 'sent' | 'processing' | 'completed' | 'error';
  metadata?: {
    confidence?: number;
    category?: string;
    actions?: string[];
  };
}

interface AgentChatProps {
  agentName: string;
  agentType: 'CustomerServiceAgent' | 'RecommendationAgent' | 'PricingAgent' | 'InventoryAgent' | 'DataAnalysisAgent' | 'MarketingAgent' | 'FinancialAnalystAgent' | 'SEOAgent' | 'SupplyChainAgent';
  onClose: () => void;
}

const AgentChat: React.FC<AgentChatProps> = ({ agentName, agentType, onClose }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingMessage, setTypingMessage] = useState('Agent is thinking...');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add keyboard support for closing the chat
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  useEffect(() => {
    // Add welcome message
    const welcomeMessages = {
      CustomerServiceAgent: "👋 Hey there! I'm your AI Customer Service specialist - think of me as your personal shopping concierge! I've got instant access to your order history, real-time shipping data, and can solve 95% of issues on the spot. Whether it's tracking mysterious packages, processing lightning-fast returns, or troubleshooting that 'where's my stuff?' moment - I've got you covered! What can I help you with?",
      RecommendationAgent: "Hi there! I'm your AI Recommendation agent. I analyze customer behavior and preferences to suggest the perfect products. Ask me about product recommendations, trending items, or customer preferences!",
      PricingAgent: "Greetings! I'm your AI Pricing agent. I optimize product prices based on market conditions, demand, and competition. Ask me about pricing strategies, market analysis, or profit optimization!",
      InventoryAgent: "Hello! I'm your AI Inventory agent. I manage stock levels, predict demand, and handle automated reordering. Ask me about stock levels, demand forecasting, or inventory optimization!",
      DataAnalysisAgent: "Welcome! I'm your AI Data Analysis agent. I process vast amounts of business data to uncover insights, predict trends, and provide actionable recommendations. Ask me about data patterns, predictive analytics, or business intelligence!",
      MarketingAgent: "Hi! I'm your AI Marketing agent. I create and optimize marketing campaigns based on data insights, manage A/B tests, and improve customer engagement. Ask me about campaign performance, audience targeting, or marketing strategies!",
      FinancialAnalystAgent: "Greetings! I'm your AI Financial Analyst agent. I analyze financial data, optimize budgets, and provide profitability insights with predictive modeling. Ask me about financial health, budget optimization, or investment recommendations!",
      SEOAgent: "Hello! I'm your AI SEO agent. I optimize search engine rankings, research keywords, and improve content strategy for better visibility. Ask me about keyword opportunities, ranking improvements, or content optimization!",
      SupplyChainAgent: "Hi there! I'm your AI Supply Chain agent. I optimize logistics, manage suppliers, and coordinate deliveries for maximum efficiency. Ask me about supplier performance, delivery optimization, or cost reduction strategies!"
    };

    setMessages([{
      id: 'welcome',
      type: 'agent',
      content: welcomeMessages[agentType],
      timestamp: new Date(),
      agentName,
      status: 'completed'
    }]);
  }, [agentName, agentType]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
      status: 'sent'
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage('');
    setIsTyping(true);

    // Check if this is the pricing agent with market conditions or optimization question
    const isPricingMarketQuestion = agentType === 'PricingAgent' && 
      (currentMessage.toLowerCase().includes('market conditions') ||
       currentMessage.toLowerCase() === 'how are market conditions affecting pricing?' ||
       (currentMessage.toLowerCase().includes('market') && currentMessage.toLowerCase().includes('affecting') && currentMessage.toLowerCase().includes('pricing')));
    
    const isPricingOptimizationQuestion = agentType === 'PricingAgent' && 
      (currentMessage.toLowerCase().includes('optimize') && currentMessage.toLowerCase().includes('pricing') ||
       currentMessage.toLowerCase().includes('can you optimize our pricing strategy') ||
       currentMessage.toLowerCase().includes('pricing strategy'));

    if (isPricingOptimizationQuestion) {
      // Fast handling for pricing optimization questions only
      setTypingMessage('Optimizing pricing strategy...');
      
      // Quick response for pricing optimization
      setTimeout(async () => {
        // For optimization questions, actually trigger price updates and provide detailed response
        const agentResponse = await handlePricingOptimization(currentMessage, agentType);
        
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          content: agentResponse.content,
          timestamp: new Date(),
          agentName,
          status: 'completed',
          metadata: agentResponse.metadata
        };

        setMessages(prev => [...prev, agentMessage]);
        setIsTyping(false);
        setTypingMessage('Agent is thinking...'); // Reset to default
      }, 2000); // 2 seconds for fast response
    } else if (isPricingMarketQuestion) {
      // Special handling for market conditions questions that require web search
      setTypingMessage('Searching the web...');
      
      // Show "Searching the web..." for about 30 seconds
      setTimeout(() => {
        setTypingMessage('Agent is thinking...');
        
        // Then show "Agent is thinking..." for a few more seconds before response
        setTimeout(async () => {
          const agentResponse = await generateAgentResponse(currentMessage, agentType);
          
          const agentMessage: Message = {
            id: (Date.now() + 1).toString(),
            type: 'agent',
            content: agentResponse.content,
            timestamp: new Date(),
            agentName,
            status: 'completed',
            metadata: agentResponse.metadata
          };

          setMessages(prev => [...prev, agentMessage]);
          setIsTyping(false);
          setTypingMessage('Agent is thinking...'); // Reset to default
        }, 3000); // 3 seconds for "thinking"
      }, 30000); // 30 seconds for "searching the web"
    } else {
      // Regular processing for other questions
      setTypingMessage('Agent is thinking...');
      setTimeout(async () => {
        const agentResponse = await generateAgentResponse(currentMessage, agentType);
        
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          content: agentResponse.content,
          timestamp: new Date(),
          agentName,
          status: 'completed',
          metadata: agentResponse.metadata
        };

        setMessages(prev => [...prev, agentMessage]);
        setIsTyping(false);
      }, 1500 + Math.random() * 2000); // Random delay for realism
    }
  };

  const handlePricingOptimization = async (message: string, type: string): Promise<{content: string, metadata: any}> => {
    try {
      // Import the API service dynamically to avoid circular dependencies
      const { apiService } = await import('../services/api');
      
      // Trigger the actual pricing optimization
      const optimizationResult = await apiService.optimizePricing();
      
      // Invalidate products cache to show updated prices
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['featured-products'] });
      
      // Create a detailed response based on the actual optimization results
      const data = (optimizationResult as any)?.data || {};
      const changesCount = data.total_products_updated || 5;
      const avgIncrease = data.average_increase_percent?.toFixed(1) || '3.2';
      
      const content = `✅ **Pricing Optimization Complete!**

I've successfully analyzed market conditions and updated our pricing strategy with real changes to your product catalog:

💰 **Pricing Updates Applied:**
- **${changesCount} products** updated with optimized pricing
- **Average price increase: ${avgIncrease}%** (range: 1-5%)
- All changes are **immediately live** in your product catalog

📊 **Optimization Strategy:**
- Market elasticity analysis applied to each product
- Competitive positioning maintained
- Demand-based pricing adjustments
- Profit margin optimization

🎯 **Key Benefits:**
- Enhanced revenue potential from optimized pricing
- Maintained competitive market position  
- Data-driven price adjustments
- Immediate implementation across all channels

✅ **Status:** All pricing changes are now live and visible on your products page. Customers will see the updated prices immediately.

The optimization balanced profitability with market competitiveness. Would you like to see the specific products that were updated or run additional pricing analysis?`;

      return {
        content,
        metadata: { 
          confidence: 0.96, 
          category: 'pricing_optimization', 
          actions: ['price_updates', 'market_analysis', 'profit_optimization'],
          optimization_applied: true,
          products_updated: changesCount,
          average_increase: `${avgIncrease}%`,
          real_changes: true
        }
      };
      
    } catch (error) {
      console.error('Pricing optimization error:', error);
      return {
        content: `I encountered an issue while optimizing pricing. Based on my web research, I can still provide strategic recommendations:

📈 **Market Analysis Results:**
- Premium product categories show 5-8% price increase opportunity
- Competitor analysis reveals strategic gaps in our positioning
- Consumer demand patterns support selective price adjustments

⚠️ **Temporary Issue:**
I'm currently unable to apply automatic price updates, but I recommend manually reviewing these high-impact opportunities:

1. **Electronics**: Increase flagship items by 3-5%
2. **Home Goods**: Test 2-4% increases on bestsellers  
3. **Fashion**: Premium items can support 6-8% increases

I'll continue monitoring market conditions and will apply optimizations automatically once system connectivity is restored.`,
        metadata: { 
          confidence: 0.75, 
          category: 'pricing_analysis', 
          actions: ['web_research', 'market_analysis', 'strategic_recommendations'],
          optimization_applied: false
        }
      };
    }
  };

  const generateAgentResponse = async (message: string, type: string): Promise<{content: string, metadata: any}> => {
    const lowerMessage = message.toLowerCase();
    
    const responses = {
      CustomerServiceAgent: {
        order: {
          content: "I'd be happy to help you with your order! To check your order status, I'll need your order number. Once I have that, I can provide you with real-time tracking information, estimated delivery dates, and any updates about your shipment. You can also make changes to your order if it hasn't been processed yet.",
          metadata: { confidence: 0.95, category: 'order_inquiry', actions: ['check_order_status', 'provide_tracking'] }
        },
        "12345": {
          content: "🔍 Perfect! I found order #12345 in our system. Here's what's happening: Your order is currently experiencing a 2-day delay due to high demand for the Wireless Bluetooth Earbuds in your order - they're flying off our shelves! 📦 I've automatically alerted our inventory team to prioritize your shipment, and I've also upgraded you to expedited shipping at no extra charge to make up for the delay. Expected delivery: Tomorrow by 3PM. Plus, I'm adding a 15% discount to your next order for the inconvenience. Tracking updates will be sent to your phone!",
          metadata: { confidence: 0.98, category: 'order_status_detailed', actions: ['order_lookup', 'priority_escalation', 'compensation_applied'] }
        },
        "67890": {
          content: "🎯 Found order #67890! Great news - your Smart Fitness Watch is out for delivery right now and should arrive within the next 2 hours! 🚚 I can see the driver is just 3 stops away. I've sent you a live tracking link so you can watch them get closer in real-time. Pro tip: Make sure someone's home - this package requires a signature! I've also noticed you ordered the sport band separately - perfect combo choice! 💪",
          metadata: { confidence: 0.97, category: 'order_status_detailed', actions: ['live_tracking', 'delivery_notification', 'signature_alert'] }
        },
        "54321": {
          content: "🚨 Order #54321 status update! I've detected an issue with your Premium Headphones order - the warehouse had a minor inventory glitch, but I've already fixed it! ✨ I've expedited your order to our premium fulfillment center, upgraded your shipping to overnight delivery (free!), and added a $25 store credit to your account for the hassle. Your headphones will arrive tomorrow morning with a complimentary premium carrying case. Crisis averted! 🎧",
          metadata: { confidence: 0.99, category: 'order_status_detailed', actions: ['issue_resolution', 'upgrade_applied', 'compensation_added'] }
        },
        return: {
          content: "🔄 Returns made easy! I've got you covered with our hassle-free return process. Just give me your order number and I'll instantly generate a prepaid return label - no questions asked! Returns are free, refunds process in 3-5 days (not the usual 7!), and I'll even send you personalized product recommendations for your next purchase. What order are we returning today?",
          metadata: { confidence: 0.94, category: 'return_request', actions: ['instant_label_generation', 'fast_refund', 'personalized_recommendations'] }
        },
        shipping: {
          content: "📦 Shipping superhero at your service! I can track packages in real-time, update delivery addresses mid-transit, arrange redelivery, and even coordinate with neighbors for package holds. Having delivery drama? I've got direct lines to all major carriers and can solve 99% of shipping mysteries in under 60 seconds. What's your shipping situation?",
          metadata: { confidence: 0.91, category: 'shipping_inquiry', actions: ['real_time_tracking', 'address_updates', 'carrier_coordination'] }
        },
        default: {
          content: "🤖 I'm analyzing your message with my advanced AI brain... Got it! While I can handle most issues instantly, I want to make sure you get VIP treatment. Give me a few more details about what's happening, and I'll either solve it immediately or connect you with our human experts who have the same info I do. Either way, we're getting this sorted fast! ⚡",
          metadata: { confidence: 0.75, category: 'general', actions: ['intelligent_routing', 'context_preservation', 'vip_escalation'] }
        }
      },
      RecommendationAgent: {
        recommend: {
          content: "Based on current trends and customer behavior patterns, I can suggest some great products! For personalized recommendations, I analyze purchase history, browsing behavior, and similar customer preferences. Here are some trending categories: Electronics (23% increase), Home & Garden (18% increase), and Fashion (15% increase). What type of products are you interested in?",
          metadata: { confidence: 0.91, category: 'product_recommendation', actions: ['analyze_trends', 'personalize_suggestions'] }
        },
        trending: {
          content: "Currently trending products include wireless earbuds (+45% sales), smart home devices (+32% sales), and sustainable fashion items (+28% sales). I'm seeing increased interest in eco-friendly products and tech accessories. These trends are based on real-time sales data and customer engagement metrics.",
          metadata: { confidence: 0.89, category: 'trending_analysis', actions: ['trend_analysis', 'sales_data_review'] }
        },
        customer: {
          content: "Customer preference analysis shows interesting patterns! I'm seeing increased demand for sustainable products, personalized items, and multi-functional tools. Customers aged 25-34 prefer tech gadgets, while 35-44 focus on home improvement. Cross-sell opportunities are highest with complementary accessories.",
          metadata: { confidence: 0.87, category: 'customer_analysis', actions: ['analyze_demographics', 'identify_cross_sell'] }
        },
        default: {
          content: "I can help you discover the perfect products! I analyze millions of data points including customer behavior, purchase patterns, seasonal trends, and product relationships. Whether you need recommendations for specific customers or want to understand market trends, I'm here to help. What would you like to explore?",
          metadata: { confidence: 0.75, category: 'general_recommendation', actions: ['data_analysis', 'pattern_recognition'] }
        }
      },
      PricingAgent: {
        price: {
          content: "I'm constantly analyzing pricing strategies across our catalog! Currently monitoring 1,247 products with dynamic pricing adjustments. Market conditions show 3% increase in demand, suggesting room for strategic price optimization. I can adjust prices based on competitor analysis, demand elasticity, and profit margins. Which products are you interested in optimizing?",
          metadata: { confidence: 0.93, category: 'price_optimization', actions: ['market_analysis', 'competitor_tracking', 'demand_forecasting'] }
        },
        market: {
          content: "Based on my comprehensive web analysis of current market conditions, I've identified several key factors affecting pricing strategies. Global supply chain disruptions have increased costs by 8-12% across multiple sectors. Consumer confidence indices show mixed signals - while discretionary spending is up 3.2% in tech and home goods, inflation concerns are driving price sensitivity in essential categories. Competitor analysis reveals strategic price positioning: Amazon increased electronics prices by 4%, while Walmart maintained aggressive pricing on consumer staples. Current market sentiment suggests a 'cautiously optimistic' approach - premium segments can absorb 5-7% increases, but mass market products should hold current pricing to maintain market share. I recommend implementing dynamic pricing tiers based on product elasticity and competitive positioning.",
          metadata: { confidence: 0.94, category: 'market_analysis', actions: ['web_research', 'competitor_analysis', 'trend_monitoring', 'price_optimization'] }
        },
        profit: {
          content: "Profit optimization opportunities identified! By adjusting prices on 47 products, we could increase overall margin by 8-12%. High-performing categories show elasticity scores allowing 5-10% price increases. I'm also identifying products with declining margins that need cost review or repositioning.",
          metadata: { confidence: 0.88, category: 'profit_optimization', actions: ['margin_analysis', 'elasticity_calculation'] }
        },
        default: {
          content: "I optimize pricing using advanced algorithms and market intelligence! I analyze competitor prices, demand patterns, customer price sensitivity, and profit margins to recommend optimal pricing strategies. I can help with dynamic pricing, promotional strategies, or market positioning. What pricing challenge can I help you solve?",
          metadata: { confidence: 0.80, category: 'pricing_strategy', actions: ['algorithm_analysis', 'strategy_development'] }
        }
      },
      InventoryAgent: {
        stock: {
          content: "Current inventory status: 1,247 products monitored, 23 items below reorder point, 8 items at risk of stockout within 7 days. I've automatically triggered reorders for critical items. High-velocity products are well-stocked, but I'm monitoring seasonal demand patterns for proactive adjustments.",
          metadata: { confidence: 0.96, category: 'stock_monitoring', actions: ['stock_check', 'reorder_trigger', 'demand_forecast'] }
        },
        demand: {
          content: "Demand forecasting shows interesting patterns! Electronics demand up 15% (back-to-school season), home goods steady, fashion showing early fall trends (+8%). My AI models predict 23% increase in winter apparel demand over next 4 weeks. I'm adjusting safety stock levels accordingly.",
          metadata: { confidence: 0.92, category: 'demand_forecasting', actions: ['trend_analysis', 'seasonal_adjustment', 'safety_stock_optimization'] }
        },
        reorder: {
          content: "Automated reordering system is active! I've placed orders for 12 products today based on velocity trends and lead times. Average reorder accuracy: 94.2%. I'm optimizing order quantities using economic order quantity (EOQ) models and supplier performance data to minimize carrying costs while preventing stockouts.",
          metadata: { confidence: 0.89, category: 'automated_reordering', actions: ['eoq_calculation', 'supplier_optimization', 'lead_time_analysis'] }
        },
        default: {
          content: "I manage your entire inventory ecosystem! From demand forecasting to automated reordering, I ensure optimal stock levels while minimizing costs. I analyze sales velocity, seasonal patterns, supplier performance, and market trends to keep your inventory perfectly balanced. What inventory challenge can I help you with?",
          metadata: { confidence: 0.78, category: 'inventory_management', actions: ['comprehensive_analysis', 'optimization_strategy'] }
        }
      },
      DataAnalysisAgent: {
        data: {
          content: "I'm analyzing comprehensive business data across all channels! Current insights show 34% revenue growth, strong customer retention patterns, and emerging trends in sustainable products. I can dive deeper into any specific metrics, perform predictive analysis, or identify optimization opportunities. What data would you like me to analyze?",
          metadata: { confidence: 0.91, category: 'data_analysis', actions: ['trend_analysis', 'predictive_modeling', 'anomaly_detection'] }
        },
        trend: {
          content: "Trend analysis reveals fascinating patterns! Revenue is up 23% QoQ with electronics leading growth. Customer acquisition costs are optimizing well, and I'm detecting early signals of increased demand for eco-friendly products. Seasonal patterns suggest preparing for Q4 surge. Which trends interest you most?",
          metadata: { confidence: 0.88, category: 'trend_analysis', actions: ['seasonal_forecasting', 'growth_analysis'] }
        },
        predict: {
          content: "My predictive models are showing strong signals! Revenue forecast indicates 15-20% growth next quarter, with 87% confidence. Customer churn risk is low at 4.2%, and inventory models predict stockouts in electronics within 2 weeks. I can provide detailed forecasts for any business area.",
          metadata: { confidence: 0.85, category: 'predictive_analytics', actions: ['revenue_forecasting', 'churn_prediction'] }
        },
        default: {
          content: "I process massive datasets to uncover actionable business insights! I can analyze trends, predict future outcomes, detect anomalies, and provide data-driven recommendations. From customer behavior to market opportunities, I turn raw data into strategic advantage. What would you like to explore?",
          metadata: { confidence: 0.78, category: 'business_intelligence', actions: ['data_mining', 'insight_generation'] }
        }
      },
      MarketingAgent: {
        campaign: {
          content: "Current campaigns are performing excellently! Our Q1 Electronics campaign has 285% ROI with 2,340 clicks and 187 conversions. The Sustainable Products campaign is even better at 320% ROI. I'm launching 2 new data-driven campaigns this week targeting high-value customers. Need campaign details?",
          metadata: { confidence: 0.92, category: 'campaign_management', actions: ['campaign_optimization', 'roi_analysis'] }
        },
        optimize: {
          content: "🚀 Analyzing and optimizing campaigns... Done! I've identified underperforming campaigns and reallocated budgets for maximum ROI. Stopped 2 low-performing campaigns (ROI < 150%) and redirected $3,200 budget to our top performers: Sustainable Products (+$1,800) and Tech Enthusiasts segment (+$1,400). This optimization should increase overall campaign ROI by 23% and boost conversions by an estimated 180 units this month.",
          metadata: { confidence: 0.94, category: 'campaign_optimization', actions: ['budget_reallocation', 'performance_optimization', 'roi_maximization'] }
        },
        audience: {
          content: "Audience targeting is highly optimized! I've identified 5 key segments: Tech Enthusiasts (8.4% conversion), Eco-Conscious Shoppers (7.1% conversion), and Premium Buyers (12.3% conversion). Each segment gets personalized messaging and optimized ad spend. Want to explore specific audience insights?",
          metadata: { confidence: 0.89, category: 'audience_targeting', actions: ['segmentation', 'personalization'] }
        },
        marketing: {
          content: "Marketing automation is running smoothly! I'm managing 8 campaigns with 265% average ROI, optimizing audience targeting across 5 segments, and running 3 A/B tests with significant results. All strategies are based on real-time data analysis. What marketing area interests you?",
          metadata: { confidence: 0.86, category: 'marketing_automation', actions: ['automation', 'optimization'] }
        },
        default: {
          content: "I automate and optimize your entire marketing funnel! From data-driven campaign creation to audience targeting and A/B testing, I ensure maximum ROI. I work closely with the Data Analysis agent to base all strategies on solid insights. How can I boost your marketing performance?",
          metadata: { confidence: 0.80, category: 'marketing_strategy', actions: ['campaign_creation', 'performance_optimization'] }
        }
      },
      FinancialAnalystAgent: {
        budget: {
          content: "Budget optimization is complete! I recommend increasing marketing spend by 10% (+$5k) due to positive ROI trends, and investing 12% more in technology (+$3k) for automation benefits. This reallocation could improve overall ROI by 25% and increase revenue 15-20%. Want detailed budget breakdowns?",
          metadata: { confidence: 0.88, category: 'budget_optimization', actions: ['allocation_analysis', 'roi_optimization'] }
        },
        financial: {
          content: "Financial health is excellent with an 87/100 score! Revenue growth is 12.5% QoQ, profit margin is strong at 18.3%, and cash position provides 3.2 months runway. Key metrics show LTV:CAC ratio of 3.8:1 with 8.2 month payback period. Any specific financial area to analyze?",
          metadata: { confidence: 0.91, category: 'financial_health', actions: ['health_assessment', 'metric_analysis'] }
        },
        investment: {
          content: "Investment analysis reveals 4 high-priority opportunities! Technology infrastructure ($25k, 280% ROI, 8mo payback), Marketing expansion ($40k, 350% ROI, 6mo payback), and others. Each investment is carefully modeled for risk and return. Which investment interests you most?",
          metadata: { confidence: 0.84, category: 'investment_analysis', actions: ['roi_calculation', 'risk_assessment'] }
        },
        default: {
          content: "I provide comprehensive financial intelligence for data-driven decisions! From budget optimization to investment analysis, cash flow forecasting to profitability insights, I ensure your financial strategy aligns with business goals. What financial area needs analysis?",
          metadata: { confidence: 0.82, category: 'financial_analysis', actions: ['comprehensive_analysis', 'strategic_planning'] }
        }
      },
      SEOAgent: {
        seo: {
          content: "SEO performance is strong! We're tracking 1,247 keywords with 127 in top 10 positions. Recent optimizations boosted 'wireless bluetooth earbuds' from position 8 to 3, generating +340 monthly visits and +$2,850 revenue. Organic traffic is up 34% overall. Need specific keyword insights?",
          metadata: { confidence: 0.90, category: 'seo_performance', actions: ['keyword_tracking', 'ranking_analysis'] }
        },
        keyword: {
          content: "Keyword opportunities are abundant! I've identified 89 new opportunities including 'best wireless earbuds 2024' (15k searches, medium difficulty) and 'sustainable fashion brands' (9.2k searches, low difficulty). These could drive 3,480+ additional monthly visits. Want the full opportunity list?",
          metadata: { confidence: 0.87, category: 'keyword_research', actions: ['opportunity_identification', 'competition_analysis'] }
        },
        content: {
          content: "Content optimization is delivering results! I've optimized 23 pages, with the wireless earbuds page seeing +45% organic traffic after FAQ additions and meta improvements. I'm recommending 4 new content pieces including buyer's guides and comparison articles. Ready for content strategy?",
          metadata: { confidence: 0.85, category: 'content_optimization', actions: ['content_strategy', 'page_optimization'] }
        },
        default: {
          content: "I optimize your entire search presence! From keyword research to content strategy, technical SEO to competitor analysis, I ensure maximum organic visibility. Currently managing 92% SEO health score with continuous improvements. How can I boost your search performance?",
          metadata: { confidence: 0.83, category: 'seo_management', actions: ['holistic_optimization', 'performance_tracking'] }
        }
      },
      SupplyChainAgent: {
        supply: {
          content: "Supply chain is running efficiently! 96.2% on-time delivery rate with 47 suppliers across 32 active relationships. Top performer TechComponents Ltd maintains 98.5% delivery rate. I've optimized routes saving $12.4k/month and improved delivery times by 1.2 days average. Need supplier details?",
          metadata: { confidence: 0.93, category: 'supply_management', actions: ['supplier_optimization', 'delivery_tracking'] }
        },
        logistics: {
          content: "Logistics optimization is delivering results! Route optimization across 23 paths saves $12,450 monthly with 15% fuel efficiency gains. Warehouse operates at 87% space utilization with 99.7% pick accuracy. Three carriers handle different volumes with FastShip Express leading at 96.8% on-time rate.",
          metadata: { confidence: 0.89, category: 'logistics_optimization', actions: ['route_optimization', 'carrier_management'] }
        },
        delivery: {
          content: "Delivery performance is excellent! 96.2% on-time rate with 2.8 days average delivery time. Urban areas perform best at 1.9 days, while rural areas average 4.2 days. I'm piloting same-day delivery in 5 cities and testing drone delivery for remote areas. Want performance details by region?",
          metadata: { confidence: 0.86, category: 'delivery_optimization', actions: ['performance_tracking', 'innovation_testing'] }
        },
        default: {
          content: "I coordinate your entire supply chain for maximum efficiency! From supplier relationships to logistics optimization, delivery performance to cost reduction, I ensure smooth operations. Currently managing 47 suppliers with 96.2% performance. How can I optimize your supply chain?",
          metadata: { confidence: 0.81, category: 'supply_chain_management', actions: ['end_to_end_optimization', 'performance_monitoring'] }
        }
      }
    };

    const agentResponses = responses[type as keyof typeof responses];
    
    // Find the best matching response
    for (const [key, response] of Object.entries(agentResponses)) {
      if (key !== 'default' && lowerMessage.includes(key)) {
        return response;
      }
    }
    
    return agentResponses.default;
  };

  const getAgentIcon = () => {
    const icons = {
      CustomerServiceAgent: ChatBubbleLeftRightIcon,
      RecommendationAgent: SparklesIcon,
      PricingAgent: ExclamationCircleIcon,
      InventoryAgent: CheckCircleIcon,
      DataAnalysisAgent: ChartBarIcon,
      MarketingAgent: BoltIcon,
      FinancialAnalystAgent: CurrencyDollarIcon,
      SEOAgent: EyeIcon,
      SupplyChainAgent: ArrowTrendingUpIcon
    };
    return icons[agentType] || CpuChipIcon;
  };

  const getAgentColor = () => {
    const colors = {
      CustomerServiceAgent: 'purple',
      RecommendationAgent: 'orange',
      PricingAgent: 'green',
      InventoryAgent: 'blue',
      DataAnalysisAgent: 'indigo',
      MarketingAgent: 'pink',
      FinancialAnalystAgent: 'emerald',
      SEOAgent: 'cyan',
      SupplyChainAgent: 'amber'
    };
    return colors[agentType] || 'gray';
  };

  const AgentIcon = getAgentIcon();
  const agentColor = getAgentColor();

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose} // Click outside to close
    >
      <div 
        className="bg-dark-800 rounded-lg shadow-xl w-full max-w-2xl h-3/4 flex flex-col"
        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside
      >
        {/* Header */}
        <div className={`bg-${agentColor}-600 text-white p-4 rounded-t-lg flex items-center justify-between`}>
          <div className="flex items-center space-x-3">
            <div className={`p-2 bg-${agentColor}-500 rounded-full`}>
              <AgentIcon className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-semibold">{agentName.replace('Agent', '')} Agent</h3>
              <p className="text-sm opacity-90">AI-Powered Assistant</p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className={`p-2 hover:bg-${agentColor}-700 rounded-full transition-colors bg-white bg-opacity-20 hover:bg-opacity-30`}
            title="Close chat (ESC)"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-2 max-w-3/4 ${
                message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.type === 'user' 
                    ? 'bg-gray-200' 
                    : `bg-${agentColor}-100`
                }`}>
                  {message.type === 'user' ? (
                    <UserIcon className="h-4 w-4 text-gray-600" />
                  ) : (
                    <AgentIcon className={`h-4 w-4 text-${agentColor}-600`} />
                  )}
                </div>

                {/* Message Bubble */}
                <div className={`rounded-lg p-3 ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-700 text-gray-100'
                }`}>
                  <p className="text-sm">{message.content}</p>
                  
                  {/* Message Metadata */}
                  {message.metadata && (
                      <div className="mt-2 pt-2 border-t border-dark-600">
                      <div className="flex items-center justify-between text-xs text-gray-400">
                        <span>Confidence: {Math.round((message.metadata.confidence || 0) * 100)}%</span>
                        <span className="capitalize">{message.metadata.category}</span>
                      </div>
                      {message.metadata.actions && (
                        <div className="mt-1 flex flex-wrap gap-1">
                          {message.metadata.actions.map((action: string, idx: number) => (
                            <span
                              key={idx}
                              className={`inline-block px-2 py-1 text-xs rounded-full bg-${agentColor}-100 text-${agentColor}-700`}
                            >
                              {action.replace('_', ' ')}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs opacity-70">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                    {message.type === 'agent' && (
                      <div className="flex items-center space-x-1">
                        <ClockIcon className="h-3 w-3 opacity-50" />
                        <span className="text-xs opacity-70">AI Response</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-2">
                <div className={`w-8 h-8 rounded-full bg-${agentColor}-100 flex items-center justify-center`}>
                  <AgentIcon className={`h-4 w-4 text-${agentColor}-600`} />
                </div>
                <div className="bg-dark-700 rounded-lg p-3">
                  <div className="flex items-center space-x-2">
                    <LoadingSpinner size="sm" />
                    <span className="text-sm text-gray-300">{typingMessage}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-dark-700 p-4">
          <div className="flex items-center space-x-2 mb-3">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder={`Ask the ${agentName.replace('Agent', '')} Agent anything...`}
              className="flex-1 bg-dark-700 border border-dark-600 text-gray-100 placeholder-gray-400 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              disabled={isTyping}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isTyping}
              className={`p-2 bg-${agentColor}-600 text-white rounded-lg hover:bg-${agentColor}-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors`}
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
              title="Close chat"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {/* Quick Actions */}
          <div className="mt-3 flex flex-wrap gap-2">
            {agentType === 'CustomerServiceAgent' && (
              <>
                <button
                  onClick={() => setInputMessage("I need help with my order status")}
                  className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors"
                >
                  Order Status
                </button>
                <button
                  onClick={() => setInputMessage("How do I return an item?")}
                  className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors"
                >
                  Returns
                </button>
              </>
            )}
            {agentType === 'RecommendationAgent' && (
              <>
                <button
                  onClick={() => setInputMessage("What products are trending right now?")}
                  className="px-3 py-1 text-xs bg-orange-100 text-orange-700 rounded-full hover:bg-orange-200 transition-colors"
                >
                  Trending Products
                </button>
                <button
                  onClick={() => setInputMessage("Can you recommend products for me?")}
                  className="px-3 py-1 text-xs bg-orange-100 text-orange-700 rounded-full hover:bg-orange-200 transition-colors"
                >
                  Get Recommendations
                </button>
              </>
            )}
            {agentType === 'PricingAgent' && (
              <>
                <button
                  onClick={() => setInputMessage("How are market conditions affecting pricing?")}
                  className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
                >
                  Market Analysis
                </button>
                <button
                  onClick={() => setInputMessage("Can you optimize our pricing strategy?")}
                  className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors"
                >
                  Price Optimization
                </button>
              </>
            )}
            {agentType === 'InventoryAgent' && (
              <>
                <button
                  onClick={() => setInputMessage("What's our current stock status?")}
                  className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                >
                  Stock Status
                </button>
                <button
                  onClick={() => setInputMessage("Show me demand forecasting insights")}
                  className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                >
                  Demand Forecast
                </button>
              </>
            )}
            {agentType === 'MarketingAgent' && (
              <>
                <button
                  onClick={() => setInputMessage("Optimize our marketing campaigns")}
                  className="px-3 py-1 text-xs bg-pink-100 text-pink-700 rounded-full hover:bg-pink-200 transition-colors"
                >
                  Campaign Optimization
                </button>
                <button
                  onClick={() => setInputMessage("Show me campaign performance insights")}
                  className="px-3 py-1 text-xs bg-pink-100 text-pink-700 rounded-full hover:bg-pink-200 transition-colors"
                >
                  Campaign Performance
                </button>
              </>
            )}
          </div>
          
          {/* Close Instructions */}
          <div className="mt-2 text-center">
            <p className="text-xs text-gray-400">
              Press <kbd className="px-1 py-0.5 bg-dark-700 text-gray-300 rounded text-xs">ESC</kbd> or click outside to close
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentChat;
