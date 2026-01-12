
import React, { useState } from 'react';
import DriverView from './views/DriverView';
import AdminView from './views/AdminView';
import HomeView from './views/HomeView';

const App: React.FC = () => {
  const [view, setView] = useState<'home' | 'driver' | 'admin'>('home');

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 overflow-x-hidden">
      {view === 'home' && (
        <HomeView onSelectDriver={() => setView('driver')} onSelectAdmin={() => setView('admin')} />
      )}
      {view === 'driver' && (
        <DriverView onBack={() => setView('home')} />
      )}
      {view === 'admin' && (
        <AdminView onBack={() => setView('home')} />
      )}
    </div>
  );
};

export default App;
