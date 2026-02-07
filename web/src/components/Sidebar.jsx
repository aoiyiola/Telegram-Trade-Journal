import React from 'react';

const Sidebar = ({ user, accounts, selectedAccount, onAccountSelect, isOpen, onClose }) => {
  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const initials = user.initials || getInitials(user.name || user.username);

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          w-64 bg-gray-800 border-r border-gray-700
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          flex flex-col
        `}
      >
        {/* User Profile Section */}
        <div className="p-6 border-b border-gray-700">
          {/* User Avatar with Initials */}
          <div className="flex items-center justify-center mb-4">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
              <span className="text-white text-2xl font-bold">{initials}</span>
            </div>
          </div>

          {/* Username */}
          <div className="text-center">
            <h3 className="text-white font-semibold text-lg truncate">
              {user.name || user.username || 'User'}
            </h3>
            {user.username && user.name && (
              <p className="text-gray-400 text-sm mt-1">@{user.username}</p>
            )}
          </div>
        </div>

        {/* Accounts Section */}
        <div className="flex-1 overflow-y-auto p-4">
          <h4 className="text-gray-400 text-xs uppercase font-semibold mb-3 px-2">
            Trading Accounts
          </h4>

          {/* All Accounts Option */}
          <button
            onClick={() => onAccountSelect('all')}
            className={`
              w-full text-left px-4 py-3 rounded-lg mb-2
              transition-all duration-200
              ${
                selectedAccount === 'all'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'text-gray-300 hover:bg-gray-700'
              }
            `}
          >
            <div className="flex items-center">
              <div className="mr-3">
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                  />
                </svg>
              </div>
              <div>
                <div className="font-medium">All Accounts</div>
                <div className="text-xs opacity-75">Combined view</div>
              </div>
            </div>
          </button>

          {/* Individual Accounts */}
          {accounts && accounts.length > 0 ? (
            accounts.map((account) => (
              <button
                key={account.account_id}
                onClick={() => onAccountSelect(account.account_id)}
                className={`
                  w-full text-left px-4 py-3 rounded-lg mb-2
                  transition-all duration-200
                  ${
                    selectedAccount === account.account_id
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'text-gray-300 hover:bg-gray-700'
                  }
                `}
              >
                <div className="flex items-center">
                  <div className="mr-3">
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"
                      />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium flex items-center">
                      {account.account_name || account.account_id}
                      {account.is_default && (
                        <span className="ml-2 text-xs bg-green-600 px-2 py-0.5 rounded">
                          Default
                        </span>
                      )}
                    </div>
                    <div className="text-xs opacity-75">{account.account_id}</div>
                  </div>
                </div>
              </button>
            ))
          ) : (
            <div className="text-gray-400 text-sm px-4 py-3">
              No accounts found
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-700">
          <div className="text-gray-400 text-xs text-center">
            Trade Journal Dashboard
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
