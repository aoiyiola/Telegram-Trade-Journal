import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

const EquityCurve = ({ data, title = "Equity Curve" }) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
        <h3 className="text-white font-semibold mb-4">{title}</h3>
        <div className="text-gray-400 text-center py-8">
          No closed trades yet. Start trading to see your equity curve!
        </div>
      </div>
    );
  }

  // Calculate statistics
  const finalEquity = data[data.length - 1]?.cumulative || 0;
  const maxEquity = Math.max(...data.map(d => d.cumulative));
  const minEquity = Math.min(...data.map(d => d.cumulative));
  const drawdown = maxEquity - finalEquity;

  // Color based on performance
  const lineColor = finalEquity >= 0 ? '#10b981' : '#ef4444';
  const isPositive = finalEquity >= 0;

  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-white font-semibold text-lg">{title}</h3>
        <div className="text-right">
          <div className={`text-2xl font-bold ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
            {finalEquity > 0 ? '+' : ''}{finalEquity}
          </div>
          <div className="text-gray-400 text-sm">Cumulative W/L</div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-700 p-3 rounded">
          <div className="text-gray-400 text-xs mb-1">Peak</div>
          <div className="text-green-400 font-semibold text-lg">{maxEquity}</div>
        </div>
        <div className="bg-gray-700 p-3 rounded">
          <div className="text-gray-400 text-xs mb-1">Lowest</div>
          <div className="text-red-400 font-semibold text-lg">{minEquity}</div>
        </div>
        <div className="bg-gray-700 p-3 rounded">
          <div className="text-gray-400 text-xs mb-1">Drawdown</div>
          <div className="text-yellow-400 font-semibold text-lg">{drawdown}</div>
        </div>
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => {
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
          />
          <YAxis
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#fff'
            }}
            labelFormatter={(value) => {
              const date = new Date(value);
              return date.toLocaleDateString();
            }}
            formatter={(value, name) => {
              if (name === 'cumulative') return [value, 'Cumulative'];
              if (name === 'pnl') {
                return [value > 0 ? `+${value}` : value, 'Trade Result'];
              }
              return [value, name];
            }}
          />
          <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="3 3" />
          <Line
            type="monotone"
            dataKey="cumulative"
            stroke={lineColor}
            strokeWidth={3}
            dot={{ fill: lineColor, r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-4 text-gray-400 text-xs text-center">
        Showing cumulative wins and losses over time. Each point represents a closed trade.
      </div>
    </div>
  );
};

export default EquityCurve;
