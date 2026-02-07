import React from 'react';

const TradingMetrics = ({ stats }) => {
  const metrics = [
    {
      label: 'Win Rate',
      value: `${stats.win_rate}%`,
      icon: '🎯',
      color: stats.win_rate >= 50 ? 'text-green-400' : 'text-red-400',
      bgColor: stats.win_rate >= 50 ? 'bg-green-900/30' : 'bg-red-900/30'
    },
    {
      label: 'Max Win Streak',
      value: stats.max_win_streak || 0,
      icon: '🔥',
      color: 'text-orange-400',
      bgColor: 'bg-orange-900/30'
    },
    {
      label: 'Max Loss Streak',
      value: stats.max_loss_streak || 0,
      icon: '❄️',
      color: 'text-blue-400',
      bgColor: 'bg-blue-900/30'
    },
    {
      label: 'Profit Factor',
      value: stats.profit_factor || 'N/A',
      icon: '📊',
      color: typeof stats.profit_factor === 'number' && stats.profit_factor > 1 ? 'text-green-400' : 'text-gray-400',
      bgColor: typeof stats.profit_factor === 'number' && stats.profit_factor > 1 ? 'bg-green-900/30' : 'bg-gray-900/30',
      tooltip: 'Gross profit divided by gross loss'
    },
    {
      label: 'Expectancy',
      value: stats.expectancy || 0,
      icon: '💰',
      color: stats.expectancy > 0 ? 'text-green-400' : 'text-red-400',
      bgColor: stats.expectancy > 0 ? 'bg-green-900/30' : 'bg-red-900/30',
      tooltip: 'Average expected return per trade'
    },
    {
      label: 'Total Trades',
      value: stats.total_trades || 0,
      icon: '📝',
      color: 'text-purple-400',
      bgColor: 'bg-purple-900/30'
    },
    {
      label: 'Wins',
      value: stats.wins || 0,
      icon: '✅',
      color: 'text-green-400',
      bgColor: 'bg-green-900/30'
    },
    {
      label: 'Losses',
      value: stats.losses || 0,
      icon: '❌',
      color: 'text-red-400',
      bgColor: 'bg-red-900/30'
    },
    {
      label: 'Break Even',
      value: stats.break_even || 0,
      icon: '➖',
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-900/30'
    },
    {
      label: 'Open Trades',
      value: stats.open_trades || 0,
      icon: '🔄',
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-900/30'
    }
  ];

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
      <h3 className="text-white font-semibold text-lg mb-6">Trading Metrics</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {metrics.map((metric, index) => (
          <div
            key={index}
            className={`${metric.bgColor} p-4 rounded-lg border border-gray-700 hover:border-gray-600 transition-all`}
            title={metric.tooltip}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-2xl">{metric.icon}</span>
              <div className={`${metric.color} text-2xl font-bold`}>
                {metric.value}
              </div>
            </div>
            <div className="text-gray-400 text-sm font-medium">
              {metric.label}
            </div>
          </div>
        ))}
      </div>

      {/* Performance Indicators */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Win Rate Indicator */}
        <div className="bg-gray-700 p-4 rounded-lg">
          <div className="text-gray-400 text-sm mb-2">Win Rate Status</div>
          <div className="flex items-center">
            <div className="flex-1 bg-gray-600 rounded-full h-2 mr-3">
              <div
                className={`h-2 rounded-full ${
                  stats.win_rate >= 60 ? 'bg-green-500' :
                  stats.win_rate >= 50 ? 'bg-yellow-500' :
                  'bg-red-500'
                }`}
                style={{ width: `${Math.min(stats.win_rate, 100)}%` }}
              />
            </div>
            <div className="text-white font-semibold">{stats.win_rate}%</div>
          </div>
        </div>

        {/* Risk/Reward */}
        <div className="bg-gray-700 p-4 rounded-lg">
          <div className="text-gray-400 text-sm mb-2">Win/Loss Ratio</div>
          <div className="flex items-center justify-between">
            <div className="text-center">
              <div className="text-green-400 text-xl font-bold">{stats.wins || 0}</div>
              <div className="text-gray-500 text-xs">Wins</div>
            </div>
            <div className="text-gray-500 text-2xl">:</div>
            <div className="text-center">
              <div className="text-red-400 text-xl font-bold">{stats.losses || 0}</div>
              <div className="text-gray-500 text-xs">Losses</div>
            </div>
          </div>
        </div>

        {/* Trading Activity */}
        <div className="bg-gray-700 p-4 rounded-lg">
          <div className="text-gray-400 text-sm mb-2">Trading Activity</div>
          <div className="flex items-center justify-between">
            <div className="text-center">
              <div className="text-blue-400 text-xl font-bold">{stats.closed_trades || 0}</div>
              <div className="text-gray-500 text-xs">Closed</div>
            </div>
            <div className="text-gray-500 text-2xl">/</div>
            <div className="text-center">
              <div className="text-cyan-400 text-xl font-bold">{stats.open_trades || 0}</div>
              <div className="text-gray-500 text-xs">Open</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingMetrics;
