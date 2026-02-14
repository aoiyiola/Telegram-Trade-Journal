import { BarChart3, Target, CheckCircle2, XCircle, Scale, TrendingUp } from 'lucide-react';

export default function StatsOverview({ stats }) {
  const statCards = [
    {
      label: 'Total Trades',
      value: stats.total_trades,
      Icon: BarChart3,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30'
    },
    {
      label: 'Win Rate',
      value: `${stats.win_rate}%`,
      Icon: Target,
      color: stats.win_rate >= 50 ? 'text-green-400' : 'text-red-400',
      bgColor: stats.win_rate >= 50 ? 'bg-green-500/10' : 'bg-red-500/10',
      borderColor: stats.win_rate >= 50 ? 'border-green-500/30' : 'border-red-500/30'
    },
    {
      label: 'Wins',
      value: stats.wins,
      Icon: CheckCircle2,
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30'
    },
    {
      label: 'Losses',
      value: stats.losses,
      Icon: XCircle,
      color: 'text-red-400',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/30'
    },
    {
      label: 'Break Even',
      value: stats.break_even,
      Icon: Scale,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/30'
    },
    {
      label: 'Open Trades',
      value: stats.open_trades,
      Icon: TrendingUp,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30'
    }
  ]

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <BarChart3 className="w-7 h-7 text-blue-400" />
        <span>Performance Overview</span>
      </h2>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {statCards.map((stat, index) => {
          const IconComponent = stat.Icon;
          return (
            <div
              key={index}
              className={`stat-card border ${stat.borderColor} ${stat.bgColor}`}
            >
              <div className="flex items-start justify-between mb-3">
                <IconComponent className={`w-8 h-8 ${stat.color}`} />
                <div className={`text-xs px-2 py-1 rounded ${stat.bgColor} ${stat.borderColor} border`}>
                  Live
                </div>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                <p className={`text-3xl font-bold ${stat.color}`}>
                  {stat.value}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  )
}
