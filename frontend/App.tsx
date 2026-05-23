
import React, { useState, useEffect } from 'react';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import ComparisonView from './components/ComparisonView';
import { AppRoute, JobOffer } from './types';
import { REAL_OFFERS } from './services/realData';

const App: React.FC = () => {
  const [activeRoute, setActiveRoute] = useState<AppRoute>(AppRoute.DASHBOARD);
  const [selectedForCompare, setSelectedForCompare] = useState<JobOffer[]>([]);
  const [allOffers] = useState<JobOffer[]>(REAL_OFFERS);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme');
      if (saved) return saved === 'dark';
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  useEffect(() => {
    const root = window.document.documentElement;
    if (isDarkMode) {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDarkMode]);

  const handleCompare = (offers: JobOffer[]) => {
    setSelectedForCompare(offers);
    setActiveRoute(AppRoute.COMPARISON);
  };

  const renderContent = () => {
    switch (activeRoute) {
      case AppRoute.COMPARISON:
        return (
          <ComparisonView 
            offers={selectedForCompare} 
            onBack={() => setActiveRoute(AppRoute.DASHBOARD)} 
          />
        );
      case AppRoute.ANALYTICS:
        return (
          <div className="p-8 flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400">
            <h2 className="text-xl font-bold mb-2">Market Analytics</h2>
            <p>Coming soon: Predictive salary trends and demand heatmaps based on real-time data scraping.</p>
          </div>
        );
      case AppRoute.DASHBOARD:
      default:
        return (
          <Dashboard 
            offers={allOffers}
            onCompare={handleCompare} 
          />
        );
    }
  };

  return (
    <Layout 
      activeRoute={activeRoute} 
      setRoute={setActiveRoute}
      isDarkMode={isDarkMode}
      toggleDarkMode={() => setIsDarkMode(!isDarkMode)}
    >
      <div className="min-h-screen transition-colors duration-200">
        {renderContent()}
      </div>
    </Layout>
  );
};

export default App;
