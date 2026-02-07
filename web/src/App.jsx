import { useState, useEffect } from 'react'
import axios from 'axios'
import Header from './components/Header'
import StatsOverview from './components/StatsOverview'
import TradeHistory from './components/TradeHistory'
import PairPerformance from './components/PairPerformance'
import SessionPerformance from './components/SessionPerformance'
import LoadingSpinner from './components/LoadingSpinner'
import ErrorMessage from './components/ErrorMessage'

function App() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

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

  if (loading) {
    return <LoadingSpinner />
  }

  if (error) {
    return <ErrorMessage message={error} />
  }

  if (!dashboardData) {
    return <ErrorMessage message="No data available" />
  }

  return (
    <div className="min-h-screen pb-10">
      <Header user={dashboardData.user} />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 space-y-8">
        {/* Stats Overview */}
        <StatsOverview stats={dashboardData.stats} />
        
        {/* Performance Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <PairPerformance data={dashboardData.pair_stats} />
          <SessionPerformance data={dashboardData.session_stats} />
        </div>
        
        {/* Complete Trade History */}
        <TradeHistory trades={dashboardData.recent_trades} />
      </div>
    </div>
  )
}

export default App
