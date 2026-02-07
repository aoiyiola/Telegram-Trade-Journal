import { useState, useEffect } from 'react'
import axios from 'axios'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import StatsOverview from './components/StatsOverview'
import TradeHistory from './components/TradeHistory'
import PairPerformance from './components/PairPerformance'
import SessionPerformance from './components/SessionPerformance'
import EquityCurve from './components/EquityCurve'
import TradingMetrics from './components/TradingMetrics'
import LoadingSpinner from './components/LoadingSpinner'
import ErrorMessage from './components/ErrorMessage'

function App() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [selectedAccount, setSelectedAccount] = useState('all')

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        // Get token from URL
        const urlParams = new URLSearchParams(window.location.search)
        const token = urlParams.get('token') || window.location.pathname.split('/').pop()
        
        if (!token || token === 'dashboard') {
          setError('Invalid dashboard link. Please generate a new link from Telegram.')
          setLoading(false)
          return
        }

        const response = await axios.get(`/api/dashboard/${token}`)
        setDashboardData(response.data)
        setLoading(false)
      } catch (err) {
        console.error('Dashboard fetch error:', err)
        if (err.response?.status === 401) {
          setError('Dashboard link expired or invalid. Please generate a new link from Telegram using /dashboard command.')
        } else {
          setError('Failed to load dashboard data. Please try again.')
        }
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  // Filter data based on selected account
  const getFilteredData = () => {
    if (!dashboardData) return null;
    
    if (selectedAccount === 'all') {
      return {
        stats: dashboardData.stats,
        trades: dashboardData.recent_trades,
        equityCurve: dashboardData.equity_curve,
        pairStats: dashboardData.pair_stats,
        sessionStats: dashboardData.session_stats
      };
    }
    
    // Filter for specific account
    const accountTrades = dashboardData.recent_trades.filter(
      trade => trade.account === selectedAccount
    );
    
    // Get account-specific stats
    const accountStats = dashboardData.account_stats?.[selectedAccount] || {
      total_trades: 0,
      wins: 0,
      losses: 0,
      break_even: 0,
      win_rate: 0,
      open_trades: 0,
      closed_trades: 0
    };
    
    // Calculate account-specific equity curve
    const closedAccountTrades = accountTrades
      .filter(t => t.status === 'CLOSED' && t.exit_datetime)
      .sort((a, b) => new Date(a.exit_datetime) - new Date(b.exit_datetime));
    
    let cumulative = 0;
    const accountEquityCurve = closedAccountTrades.map(trade => {
      let pnl = 0;
      if (trade.result === 'W') pnl = 1;
      else if (trade.result === 'L') pnl = -1;
      cumulative += pnl;
      
      return {
        date: new Date(trade.exit_datetime).toISOString().split('T')[0],
        timestamp: trade.exit_datetime,
        pnl: pnl,
        cumulative: cumulative,
        trade_id: trade.id
      };
    });
    
    // Calculate pair stats for this account
    const accountPairStats = {};
    accountTrades.forEach(trade => {
      if (!accountPairStats[trade.pair]) {
        accountPairStats[trade.pair] = { total: 0, wins: 0, losses: 0, win_rate: 0 };
      }
      accountPairStats[trade.pair].total += 1;
      if (trade.result === 'W') accountPairStats[trade.pair].wins += 1;
      if (trade.result === 'L') accountPairStats[trade.pair].losses += 1;
    });
    
    Object.keys(accountPairStats).forEach(pair => {
      const closed = accountPairStats[pair].wins + accountPairStats[pair].losses;
      if (closed > 0) {
        accountPairStats[pair].win_rate = (accountPairStats[pair].wins / closed * 100);
      }
    });
    
    // Calculate session stats for this account
    const accountSessionStats = {};
    accountTrades.forEach(trade => {
      const session = trade.session || 'Unknown';
      if (!accountSessionStats[session]) {
        accountSessionStats[session] = { total: 0, wins: 0, losses: 0, win_rate: 0 };
      }
      accountSessionStats[session].total += 1;
      if (trade.result === 'W') accountSessionStats[session].wins += 1;
      if (trade.result === 'L') accountSessionStats[session].losses += 1;
    });
    
    Object.keys(accountSessionStats).forEach(session => {
      const closed = accountSessionStats[session].wins + accountSessionStats[session].losses;
      if (closed > 0) {
        accountSessionStats[session].win_rate = (accountSessionStats[session].wins / closed * 100);
      }
    });
    
    return {
      stats: accountStats,
      trades: accountTrades,
      equityCurve: accountEquityCurve,
      pairStats: accountPairStats,
      sessionStats: accountSessionStats
    };
  };

  const handleAccountSelect = (accountId) => {
    setSelectedAccount(accountId);
    setSidebarOpen(false); // Close sidebar on mobile after selection
  };

  if (loading) {
    return <LoadingSpinner />
  }

  if (error) {
    return <ErrorMessage message={error} />
  }

  if (!dashboardData) {
    return <ErrorMessage message="No data available" />
  }

  const filteredData = getFilteredData();

  return (
    <div className="min-h-screen flex bg-gray-900">
      {/* Sidebar */}
      <Sidebar
        user={dashboardData.user}
        accounts={dashboardData.accounts}
        selectedAccount={selectedAccount}
        onAccountSelect={handleAccountSelect}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        <Header 
          user={dashboardData.user} 
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
        />
        
        <div className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6 overflow-auto">
          {/* Account Title */}
          {selectedAccount !== 'all' && (
            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
              <h2 className="text-xl font-bold text-white">
                {dashboardData.accounts.find(a => a.account_id === selectedAccount)?.account_name || selectedAccount}
              </h2>
              <p className="text-gray-400 text-sm">Individual account performance</p>
            </div>
          )}

          {/* Stats Overview */}
          <StatsOverview stats={filteredData.stats} />
          
          {/* Equity Curve */}
          <EquityCurve 
            data={filteredData.equityCurve} 
            title={selectedAccount === 'all' ? "Overall Equity Curve" : "Account Equity Curve"}
          />
          
          {/* Trading Metrics */}
          <TradingMetrics stats={filteredData.stats} />
          
          {/* Performance Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PairPerformance data={filteredData.pairStats} />
            <SessionPerformance data={filteredData.sessionStats} />
          </div>
          
          {/* Complete Trade History */}
          <TradeHistory trades={filteredData.trades} />
        </div>
      </div>
    </div>
  )
}

export default App
