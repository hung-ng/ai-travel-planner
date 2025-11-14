'use client';

interface BudgetItem {
  category: 'accommodation' | 'food' | 'activities' | 'transport' | 'other';
  amount: number;
}

interface BudgetBreakdownProps {
  totalBudget: number;
  spent?: BudgetItem[];
  currency?: string;
}

export default function BudgetBreakdown({ 
  totalBudget, 
  spent = [],
  currency = 'USD' 
}: BudgetBreakdownProps) {
  
  // calc totals by category
  const categoryTotals = spent.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + item.amount;
    return acc;
  }, {} as Record<string, number>);

  const totalSpent = spent.reduce((sum, item) => sum + item.amount, 0);
  const remaining = totalBudget - totalSpent;
  const percentageUsed = totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0;

  // Category
  const categories = [
    { 
      key: 'accommodation', 
      label: 'Accommodation', 
      icon: '🏨', 
      color: 'bg-purple-500',
      lightColor: 'bg-purple-100',
      textColor: 'text-purple-700'
    },
    { 
      key: 'food', 
      label: 'Food & Dining', 
      icon: '🍽️', 
      color: 'bg-orange-500',
      lightColor: 'bg-orange-100',
      textColor: 'text-orange-700'
    },
    { 
      key: 'activities', 
      label: 'Activities', 
      icon: '🎯', 
      color: 'bg-blue-500',
      lightColor: 'bg-blue-100',
      textColor: 'text-blue-700'
    },
    { 
      key: 'transport', 
      label: 'Transportation', 
      icon: '🚗', 
      color: 'bg-green-500',
      lightColor: 'bg-green-100',
      textColor: 'text-green-700'
    },
    { 
      key: 'other', 
      label: 'Other', 
      icon: '📦', 
      color: 'bg-gray-500',
      lightColor: 'bg-gray-100',
      textColor: 'text-gray-700'
    },
  ];

  return (
    <div className="space-y-6">
      {/* budget overview */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Total Budget</span>
            <span className="text-2xl">💰</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            ${totalBudget.toLocaleString()}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Spent So Far</span>
            <span className="text-2xl">💳</span>
          </div>
          <p className="text-3xl font-bold text-blue-600">
            ${totalSpent.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {percentageUsed.toFixed(0)}% of budget
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">Remaining</span>
            <span className="text-2xl">{remaining >= 0 ? '✅' : '⚠️'}</span>
          </div>
          <p className={`text-3xl font-bold ${remaining >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${Math.abs(remaining).toLocaleString()}
          </p>
          {remaining < 0 && (
            <p className="text-xs text-red-500 mt-1">Over budget!</p>
          )}
        </div>
      </div>

      {/* progress */}
      <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900">Budget Usage</h3>
          <span className="text-sm text-gray-600">{percentageUsed.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div 
            className={`h-4 rounded-full transition-all duration-500 ${
              percentageUsed > 100 ? 'bg-red-500' : 
              percentageUsed > 80 ? 'bg-yellow-500' : 
              'bg-green-500'
            }`}
            style={{ width: `${Math.min(percentageUsed, 100)}%` }}
          />
        </div>
        {percentageUsed > 80 && percentageUsed <= 100 && (
          <p className="text-xs text-yellow-600 mt-2">⚠️ Approaching budget limit</p>
        )}
        {percentageUsed > 100 && (
          <p className="text-xs text-red-600 mt-2">🚨 Over budget by ${(totalSpent - totalBudget).toLocaleString()}</p>
        )}
      </div>

      {/* Breakdown */}
      <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Spending by Category</h3>
        
        <div className="space-y-4">
          {categories.map(category => {
            const amount = categoryTotals[category.key] || 0;
            const percentage = totalBudget > 0 ? (amount / totalBudget) * 100 : 0;
            
            return (
              <div key={category.key}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{category.icon}</span>
                    <span className="text-sm font-medium text-gray-700">{category.label}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-gray-900">
                      ${amount.toLocaleString()}
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      {percentage.toFixed(0)}%
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`${category.color} h-2 rounded-full transition-all duration-500`}
                    style={{ width: `${Math.min(percentage, 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/*  pie dhart */}
      <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Budget Distribution</h3>
        
        <div className="flex flex-wrap gap-6 justify-center">
          {/* simple viz*/}
          <div className="grid grid-cols-2 gap-4 w-full">
            {categories.map(category => {
              const amount = categoryTotals[category.key] || 0;
              const percentage = totalSpent > 0 ? (amount / totalSpent) * 100 : 0;
              
              if (amount === 0) return null;
              
              return (
                <div key={category.key} className={`${category.lightColor} rounded-lg p-4 border-2 border-gray-200`}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{category.icon}</span>
                    <span className={`text-sm font-semibold ${category.textColor}`}>
                      {category.label}
                    </span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">
                    ${amount.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    {percentage.toFixed(1)}% of spending
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* tip */}
      {totalSpent === 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">💡</span>
            <div>
              <h4 className="font-semibold text-blue-900 mb-1">Budget Tracking Tips</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• As you add activities, costs will be tracked automatically</li>
                <li>• The AI will try to keep you within your budget</li>
                <li>• You can adjust your budget anytime</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}