import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

const SESSION_COLORS = {
  'Asia': '#3b82f6',
  'London': '#10b981',
  'New York': '#8b5cf6',
  'Unknown': '#6b7280'
}

export default function SessionPerformance({ data }) {
  // Transform data for pie chart
  const chartData = Object.entries(data)
    .map(([session, stats]) => ({
      name: session,
      value: stats.total,
      winRate: parseFloat(stats.win_rate.toFixed(2)),
      wins: stats.wins,
      losses: stats.losses
    }))
    .sort((a, b) => b.value - a.value)

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-dark-800 border border-dark-600 rounded-lg p-3 shadow-xl">
          <p className="font-bold text-white mb-2">{data.name}</p>
          <p className="text-sm text-gray-300">
            Win Rate: <span className="font-semibold text-primary-400">{data.winRate}%</span>
          </p>
          <p className="text-sm text-green-400">Wins: {data.wins}</p>
          <p className="text-sm text-red-400">Losses: {data.losses}</p>
          <p className="text-sm text-gray-400">Total Trades: {data.value}</p>
        </div>
      )
    }
    return null
  }

  const CustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-sm font-bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    )
  }

  if (chartData.length === 0) {
    return (
      <div className="card">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <span>🌍</span>
          <span>Session Performance</span>
        </h3>
        <div className="text-center py-12 text-gray-400">
          <p>No session data available yet</p>
          <p className="text-sm mt-2">Trades will be auto-tagged with trading sessions</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
        <span>🌍</span>
        <span>Session Performance</span>
      </h3>
      
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={CustomLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={SESSION_COLORS[entry.name] || SESSION_COLORS.Unknown} 
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
      
      <div className="mt-6 space-y-2">
        {chartData.map((session, index) => (
          <div key={index} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: SESSION_COLORS[session.name] || SESSION_COLORS.Unknown }}
              ></div>
              <span className="text-gray-300">{session.name}</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-gray-400">{session.value} trades</span>
              <span className={`font-semibold ${session.winRate >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                {session.winRate}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
