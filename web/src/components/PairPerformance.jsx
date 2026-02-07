import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'

export default function PairPerformance({ data }) {
  // Transform data for chart
  const chartData = Object.entries(data)
    .map(([pair, stats]) => ({
      pair,
      winRate: parseFloat(stats.win_rate.toFixed(2)),
      wins: stats.wins,
      losses: stats.losses,
      total: stats.total
    }))
    .sort((a, b) => b.winRate - a.winRate)

  const getBarColor = (winRate) => {
    if (winRate >= 60) return '#10b981' // green
    if (winRate >= 50) return '#3b82f6' // blue
    if (winRate >= 40) return '#f59e0b' // yellow
    return '#ef4444' // red
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-dark-800 border border-dark-600 rounded-lg p-3 shadow-xl">
          <p className="font-bold text-white mb-2">{data.pair}</p>
          <p className="text-sm text-gray-300">
            Win Rate: <span className="font-semibold text-primary-400">{data.winRate}%</span>
          </p>
          <p className="text-sm text-green-400">Wins: {data.wins}</p>
          <p className="text-sm text-red-400">Losses: {data.losses}</p>
          <p className="text-sm text-gray-400">Total: {data.total}</p>
        </div>
      )
    }
    return null
  }

  if (chartData.length === 0) {
    return (
      <div className="card">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <span>💱</span>
          <span>Pair Performance</span>
        </h3>
        <div className="text-center py-12 text-gray-400">
          <p>No trading data available yet</p>
          <p className="text-sm mt-2">Start logging trades to see pair performance</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
        <span>💱</span>
        <span>Pair Performance</span>
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis 
            dataKey="pair" 
            stroke="#94a3b8" 
            tick={{ fill: '#94a3b8' }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            stroke="#94a3b8"
            tick={{ fill: '#94a3b8' }}
            label={{ value: 'Win Rate (%)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="winRate" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.winRate)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      
      <div className="mt-4 flex items-center justify-center gap-4 text-xs text-gray-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded"></div>
          <span>≥60%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-blue-500 rounded"></div>
          <span>50-60%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-500 rounded"></div>
          <span>40-50%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded"></div>
          <span>&lt;40%</span>
        </div>
      </div>
    </div>
  )
}
