export default function Header({ user }) {
  return (
    <header className="bg-dark-800 border-b border-dark-700 shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center text-2xl font-bold">
              {user.name ? user.name[0].toUpperCase() : '👤'}
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-400 to-primary-600 bg-clip-text text-transparent">
                Trading Journal
              </h1>
              <p className="text-gray-400 text-sm">
                {user.name && `${user.name} • `}@{user.username || 'Trader'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="px-4 py-2 bg-dark-700 rounded-lg">
              <span className="text-xs text-gray-400">Status</span>
              <div className="flex items-center gap-2 mt-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-400">Live</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
