import React, { useState } from 'react';
import Login from './components/Login';
import ProfessionalDashboard from './components/ProfessionalDashboard';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState<{ user_id: string; email: string; name?: string } | null>(null);

  const handleLogin = (user: { user_id: string; email: string; name?: string }) => {
    setCurrentUser(user);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentUser(null);
  };

  return (
    <ErrorBoundary>
      <div className="h-screen w-screen overflow-hidden">
        {!isLoggedIn ? (
          <ErrorBoundary>
            <Login onLogin={handleLogin} />
          </ErrorBoundary>
        ) : (
          <ErrorBoundary>
            <ProfessionalDashboard
              currentUser={currentUser}
              onLogout={handleLogout}
            />
          </ErrorBoundary>
        )}
      </div>
    </ErrorBoundary>
  );
}

export default App;