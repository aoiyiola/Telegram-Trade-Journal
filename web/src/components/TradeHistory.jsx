import { useState, useMemo } from 'react'

export default function TradeHistory({ trades }) {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterResult, setFilterResult] = useState('all')
  const [sortField, setSortField] = useState('entry_datetime')
  const [sortDirection, setSortDirection] = useState('desc')
  const [expandedTrade, setExpandedTrade] = useState(null)

  // Filter and sort trades
  const filteredTrades = useMemo(() => {
    let filtered = trades.filter(trade => {
      // Search filter
      const searchLower = searchTerm.toLowerCase()
      const matchesSearch = !searchTerm || 
        trade.pair.toLowerCase().includes(searchLower) ||
        trade.account.toLowerCase().includes(searchLower) ||
        (trade.notes && trade.notes.toLowerCase().includes(searchLower))

      // Status filter
      const matchesStatus = filterStatus === 'all' || trade.status === filterStatus

      // Result filter
      const matchesResult = filterResult === 'all' || trade.result === filterResult

      return matchesSearch && matchesStatus && matchesResult
    })

    // Sort
    filtered.sort((a, b) => {
      let aVal = a[sortField]
      let bVal = b[sortField]

      if (sortField === 'entry_datetime' || sortField === 'exit_datetime') {
        aVal = new Date(aVal || 0)
        bVal = new Date(bVal || 0)
      }

      if (sortDirection === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })

    return filtered
  }, [trades, searchTerm, filterStatus, filterResult, sortField, sortDirection])

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const getResultBadge = (result) => {
    if (!result) return <span className="badge-info">Pending</span>
    if (result === 'W') return <span className="badge-success">✓ Win</span>
    if (result === 'L') return <span className="badge-danger">✗ Loss</span>
    if (result === 'BE') return <span className="badge-warning">= BE</span>
    return <span className="badge">{result}</span>
  }

  const getDirectionBadge = (direction) => {
    if (direction === 'BUY') {
      return <span className="badge-success">▲ BUY</span>
    }
    return <span className="badge-danger">▼ SELL</span>
  }

  const getStatusBadge = (status) => {
    if (status === 'OPEN') {
      return <span className="badge-info flex items-center gap-1">
        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
        OPEN
      </span>
    }
    return <span className="badge-warning">CLOSED</span>
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const calculatePips = (entry, exit, direction) => {
    if (!entry || !exit) return null
    const diff = direction === 'BUY' ? exit - entry : entry - exit
    return (diff * 10000).toFixed(1)
  }

  if (trades.length === 0) {
    return (
      <div className="card">
        <h3 className="text-2xl font-bold mb-4">📚 Trade History</h3>
        <div className="text-center py-16 text-gray-400">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-lg">No trades logged yet</p>
          <p className="text-sm mt-2">Your trading journey starts with /newtrade</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-6">
        <h3 className="text-2xl font-bold flex items-center gap-2">
          <span>📚</span>
          <span>Trade History</span>
          <span className="text-sm font-normal text-gray-400">({filteredTrades.length} trades)</span>
        </h3>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {/* Search */}
        <div className="md:col-span-2">
          <input
            type="text"
            placeholder="🔍 Search pairs, accounts, notes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
          />
        </div>

        {/* Status Filter */}
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
        >
          <option value="all">All Status</option>
          <option value="OPEN">Open</option>
          <option value="CLOSED">Closed</option>
        </select>

        {/* Result Filter */}
        <select
          value={filterResult}
          onChange={(e) => setFilterResult(e.target.value)}
          className="px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-primary-500"
        >
          <option value="all">All Results</option>
          <option value="W">Wins</option>
          <option value="L">Losses</option>
          <option value="BE">Break Even</option>
        </select>
      </div>

      {/* Mobile View */}
      <div className="block lg:hidden space-y-3">
        {filteredTrades.map((trade, index) => (
          <div key={index} className="bg-dark-700 rounded-lg border border-dark-600 overflow-hidden">
            <div 
              className="p-4 cursor-pointer hover:bg-dark-600/50 transition-colors"
              onClick={() => setExpandedTrade(expandedTrade === trade.id ? null : trade.id)}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg font-bold text-white">{trade.pair}</span>
                    {getDirectionBadge(trade.direction)}
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    {getStatusBadge(trade.status)}
                    {getResultBadge(trade.result)}
                    {trade.session && (
                      <span className="badge bg-purple-500/20 text-purple-400 border border-purple-500/30">
                        🌍 {trade.session}
                      </span>
                    )}
                  </div>
                </div>
                <button className="text-gray-400 hover:text-white">
                  {expandedTrade === trade.id ? '▲' : '▼'}
                </button>
              </div>

              {expandedTrade === trade.id && (
                <div className="mt-4 pt-4 border-t border-dark-600 space-y-3">
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-gray-400 block text-xs mb-1">Entry Price</span>
                      <span className="text-white font-medium">{trade.entry_price}</span>
                    </div>
                    <div>
                      <span className="text-gray-400 block text-xs mb-1">Stop Loss</span>
                      <span className="text-white font-medium">{trade.stop_loss || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-400 block text-xs mb-1">Take Profit</span>
                      <span className="text-white font-medium">{trade.take_profit || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-400 block text-xs mb-1">Account</span>
                      <span className="text-white font-medium">{trade.account}</span>
                    </div>
                  </div>

                  {trade.news_risk && (
                    <div className={`px-3 py-2 rounded-lg ${
                      trade.news_risk === 'HIGH' 
                        ? 'bg-red-500/10 border border-red-500/30' 
                        : 'bg-green-500/10 border border-green-500/30'
                    }`}>
                      <span className="text-xs text-gray-400 block mb-1">News Risk</span>
                      <span className={`text-sm font-medium ${
                        trade.news_risk === 'HIGH' ? 'text-red-400' : 'text-green-400'
                      }`}>
                        {trade.news_risk === 'HIGH' ? '⚠️ HIGH' : '✓ LOW'}
                      </span>
                    </div>
                  )}

                  {trade.notes && (
                    <div className="bg-dark-800 rounded px-3 py-2">
                      <span className="text-xs text-gray-400 block mb-1">Notes</span>
                      <p className="text-sm text-gray-300">{trade.notes}</p>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs pt-2 border-t border-dark-600">
                    <div>
                      <span className="text-gray-400">Entry: </span>
                      <span className="text-gray-300">{formatDate(trade.entry_datetime)}</span>
                    </div>
                    {trade.exit_datetime && (
                      <div>
                        <span className="text-gray-400">Exit: </span>
                        <span className="text-gray-300">{formatDate(trade.exit_datetime)}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Desktop View */}
      <div className="hidden lg:block overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left border-b border-dark-700">
              <th 
                className="pb-3 px-2 text-sm font-medium text-gray-400 cursor-pointer hover:text-primary-400"
                onClick={() => handleSort('pair')}
              >
                Pair {sortField === 'pair' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th className="pb-3 px-2 text-sm font-medium text-gray-400">Direction</th>
              <th className="pb-3 px-2 text-sm font-medium text-gray-400">Entry</th>
              <th className="pb-3 px-2 text-sm font-medium text-gray-400">SL/TP</th>
              <th className="pb-3 px-2 text-sm font-medium text-gray-400">Status</th>
              <th className="pb-3 px-2 text-sm font-medium text-gray-400">Result</th>
              <th className="pb-3 px-2 text-sm font-medium text-gray-400">Session</th>
              <th className="pb-3 px-2 text-sm font-medium text-gray-400">Risk</th>
              <th 
                className="pb-3 px-2 text-sm font-medium text-gray-400 cursor-pointer hover:text-primary-400"
                onClick={() => handleSort('entry_datetime')}
              >
                Entry Time {sortField === 'entry_datetime' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th className="pb-3 px-2 text-sm font-medium text-gray-400"></th>
            </tr>
          </thead>
          <tbody>
            {filteredTrades.map((trade, index) => (
              <tr 
                key={index} 
                className="border-b border-dark-700 hover:bg-dark-700/50 transition-colors cursor-pointer"
                onClick={() => setExpandedTrade(expandedTrade === trade.id ? null : trade.id)}
              >
                <td className="py-3 px-2 font-bold text-white">{trade.pair}</td>
                <td className="py-3 px-2">{getDirectionBadge(trade.direction)}</td>
                <td className="py-3 px-2 text-gray-300">{trade.entry_price}</td>
                <td className="py-3 px-2 text-gray-300 text-sm">
                  <div>{trade.stop_loss || 'N/A'}</div>
                  <div className="text-xs text-gray-500">{trade.take_profit || 'N/A'}</div>
                </td>
                <td className="py-3 px-2">{getStatusBadge(trade.status)}</td>
                <td className="py-3 px-2">{getResultBadge(trade.result)}</td>
                <td className="py-3 px-2 text-gray-300 text-sm">{trade.session || 'N/A'}</td>
                <td className="py-3 px-2">
                  {trade.news_risk && (
                    <span className={`text-xs px-2 py-1 rounded ${
                      trade.news_risk === 'HIGH' 
                        ? 'bg-red-500/20 text-red-400' 
                        : 'bg-green-500/20 text-green-400'
                    }`}>
                      {trade.news_risk}
                    </span>
                  )}
                </td>
                <td className="py-3 px-2 text-gray-400 text-xs">{formatDate(trade.entry_datetime)}</td>
                <td className="py-3 px-2 text-gray-400">
                  {expandedTrade === trade.id ? '▲' : '▼'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Expanded Details */}
        {expandedTrade && filteredTrades.find(t => t.id === expandedTrade) && (
          <div className="mt-4 p-4 bg-dark-700 rounded-lg border border-dark-600">
            {(() => {
              const trade = filteredTrades.find(t => t.id === expandedTrade)
              return (
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-semibold text-gray-400 mb-3">Trade Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Account:</span>
                        <span className="text-white font-medium">{trade.account}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Entry:</span>
                        <span className="text-white">{formatDate(trade.entry_datetime)}</span>
                      </div>
                      {trade.exit_datetime && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Exit:</span>
                          <span className="text-white">{formatDate(trade.exit_datetime)}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-semibold text-gray-400 mb-3">Notes</h4>
                    <p className="text-sm text-gray-300">
                      {trade.notes || <span className="text-gray-500 italic">No notes added</span>}
                    </p>
                  </div>
                </div>
              )
            })()}
          </div>
        )}
      </div>

      {filteredTrades.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p>No trades match your filters</p>
          <button
            onClick={() => {
              setSearchTerm('')
              setFilterStatus('all')
              setFilterResult('all')
            }}
            className="mt-3 text-primary-400 hover:text-primary-300 text-sm"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  )
}
