import { useState } from 'react'

export default function TradesTable({ trades }) {
  const [filter, setFilter] = useState('all') // all, open, closed

  const filteredTrades = trades.filter(trade => {
    if (filter === 'all') return true
    if (filter === 'open') return trade.status === 'OPEN'
    if (filter === 'closed') return trade.status === 'CLOSED'
    return true
  })

  const getResultBadge = (result) => {
    if (!result) return <span className="badge-info">Pending</span>
    if (result === 'W') return <span className="badge-success">Win</span>
    if (result === 'L') return <span className="badge-danger">Loss</span>
    if (result === 'BE') return <span className="badge-warning">Break Even</span>
    return <span className="badge">{result}</span>
  }

  const getDirectionBadge = (direction) => {
    if (direction === 'BUY') {
      return <span className="badge-success">🔼 BUY</span>
    }
    return <span className="badge-danger">🔽 SELL</span>
  }

  const getStatusBadge = (status) => {
    if (status === 'OPEN') {
      return <span className="badge-info">🟢 OPEN</span>
    }
    return <span className="badge">⚫ CLOSED</span>
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (trades.length === 0) {
    return (
      <div className="card">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
          <span>📜</span>
          <span>Recent Trades</span>
        </h3>
        <div className="text-center py-12 text-gray-400">
          <p>No trades logged yet</p>
          <p className="text-sm mt-2">Use /newtrade in Telegram to log your first trade</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <span>📜</span>
          <span>Recent Trades</span>
        </h3>
        
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
            }`}
          >
            All ({trades.length})
          </button>
          <button
            onClick={() => setFilter('open')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filter === 'open'
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
            }`}
          >
            Open ({trades.filter(t => t.status === 'OPEN').length})
          </button>
          <button
            onClick={() => setFilter('closed')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filter === 'closed'
                ? 'bg-primary-600 text-white'
                : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
            }`}
          >
            Closed ({trades.filter(t => t.status === 'CLOSED').length})
          </button>
        </div>
      </div>

      {/* Mobile View */}
      <div className="block lg:hidden space-y-4">
        {filteredTrades.map((trade, index) => (
          <div key={index} className="bg-dark-700 rounded-lg p-4 border border-dark-600">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg font-bold text-white">{trade.pair}</span>
                  {getDirectionBadge(trade.direction)}
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(trade.status)}
                  {getResultBadge(trade.result)}
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-400">Entry:</span>
                <span className="ml-2 text-white font-medium">{trade.entry_price}</span>
              </div>
              <div>
                <span className="text-gray-400">SL:</span>
                <span className="ml-2 text-white font-medium">{trade.stop_loss || 'N/A'}</span>
              </div>
              <div>
                <span className="text-gray-400">TP:</span>
                <span className="ml-2 text-white font-medium">{trade.take_profit || 'N/A'}</span>
              </div>
              <div>
                <span className="text-gray-400">Session:</span>
                <span className="ml-2 text-white font-medium">{trade.session || 'N/A'}</span>
              </div>
            </div>
            
            <div className="mt-3 pt-3 border-t border-dark-600 text-xs text-gray-400">
              {formatDate(trade.entry_datetime)}
            </div>
          </div>
        ))}
      </div>

      {/* Desktop View */}
      <div className="hidden lg:block overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left border-b border-dark-700">
              <th className="pb-3 text-sm font-medium text-gray-400">Pair</th>
              <th className="pb-3 text-sm font-medium text-gray-400">Direction</th>
              <th className="pb-3 text-sm font-medium text-gray-400">Entry</th>
              <th className="pb-3 text-sm font-medium text-gray-400">SL</th>
              <th className="pb-3 text-sm font-medium text-gray-400">TP</th>
              <th className="pb-3 text-sm font-medium text-gray-400">Status</th>
              <th className="pb-3 text-sm font-medium text-gray-400">Result</th>
              <th className="pb-3 text-sm font-medium text-gray-400">Session</th>
              <th className="pb-3 text-sm font-medium text-gray-400">Entry Time</th>
            </tr>
          </thead>
          <tbody>
            {filteredTrades.map((trade, index) => (
              <tr key={index} className="border-b border-dark-700 hover:bg-dark-700/50 transition-colors">
                <td className="py-3 font-bold text-white">{trade.pair}</td>
                <td className="py-3">{getDirectionBadge(trade.direction)}</td>
                <td className="py-3 text-gray-300">{trade.entry_price}</td>
                <td className="py-3 text-gray-300">{trade.stop_loss || 'N/A'}</td>
                <td className="py-3 text-gray-300">{trade.take_profit || 'N/A'}</td>
                <td className="py-3">{getStatusBadge(trade.status)}</td>
                <td className="py-3">{getResultBadge(trade.result)}</td>
                <td className="py-3 text-gray-300">{trade.session || 'N/A'}</td>
                <td className="py-3 text-gray-400 text-sm">{formatDate(trade.entry_datetime)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
