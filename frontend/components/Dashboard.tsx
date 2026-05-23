
import React, { useState, useMemo, useEffect } from 'react';
import { JobOffer, ExperienceLevel, LanguageLevel } from '../types';
import { ICONS } from '../constants';

const KPICard: React.FC<{ title: string; value: string; trend?: string; trendUp?: boolean }> = ({ title, value, trend, trendUp }) => (
  <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-200">
    <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{title}</div>
    <div className="text-2xl font-bold text-gray-900 dark:text-white">{value}</div>
    {trend && (
      <div className={`text-xs mt-2 flex items-center gap-1 ${trendUp ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
        {trendUp ? '↑' : '↓'} {trend} vs last month
      </div>
    )}
  </div>
);

const Badge: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color = 'blue' }) => {
  const colors: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-700 border-blue-100 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800',
    green: 'bg-green-50 text-green-700 border-green-100 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
    purple: 'bg-purple-50 text-purple-700 border-purple-100 dark:bg-purple-900/30 dark:text-purple-400 dark:border-purple-800',
    gray: 'bg-gray-50 text-gray-700 border-gray-100 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700',
    orange: 'bg-orange-50 text-orange-700 border-orange-100 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800',
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${colors[color] || colors.blue}`}>
      {children}
    </span>
  );
};

const LanguageLevelBadge: React.FC<{ level: LanguageLevel }> = ({ level }) => {
  const colorMap: Record<LanguageLevel, string> = {
    'A1': 'gray',
    'A2': 'gray',
    'B1': 'orange',
    'B2': 'orange',
    'C1': 'blue',
    'C2': 'purple',
    'Native': 'green'
  };
  return <Badge color={colorMap[level]}>{level}</Badge>;
};

interface DashboardProps {
  offers: JobOffer[];
  onCompare: (offers: JobOffer[]) => void;
}

const PAGE_SIZE = 5;

const Dashboard: React.FC<DashboardProps> = ({ offers, onCompare }) => {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [filterExp, setFilterExp] = useState<ExperienceLevel | 'All'>('All');
  const [currentPage, setCurrentPage] = useState(1);

  const filteredOffers = useMemo(() => {
    return offers.filter(offer => {
      const matchesTitle = offer.title.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesTech = offer.techStack.some(t => t.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesExp = filterExp === 'All' || offer.experienceLevel === filterExp;
      return (matchesTitle || matchesTech) && matchesExp;
    });
  }, [offers, searchTerm, filterExp]);

  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, filterExp]);

  const totalPages = Math.ceil(filteredOffers.length / PAGE_SIZE);
  
  const paginatedOffers = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredOffers.slice(start, start + PAGE_SIZE);
  }, [filteredOffers, currentPage]);

  const stats = useMemo(() => {
    if (offers.length === 0) return { avgSalary: 0, remoteCount: 0 };
    const avgSalary = Math.round(offers.reduce((acc, curr) => acc + (curr.salaryMin + curr.salaryMax) / 2, 0) / offers.length);
    const remoteCount = offers.filter(o => o.workMode === 'Remote').length;
    return { avgSalary, remoteCount };
  }, [offers]);

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) newSelected.delete(id);
    else newSelected.add(id);
    setSelectedIds(newSelected);
  };

  const handleCompareClick = () => {
    const selectedOffers = offers.filter(o => selectedIds.has(o.id));
    onCompare(selectedOffers);
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white transition-colors">Job Market Overview</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1 transition-colors">Aggregated data from multiple sources. Focus on the metrics that matter.</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <KPICard title="Average Annual Salary" value={`$${stats.avgSalary.toLocaleString()}`} trend="4.2%" trendUp={true} />
        <KPICard title="Remote Availability" value={`${offers.length > 0 ? Math.round((stats.remoteCount / offers.length) * 100) : 0}%`} trend="12%" trendUp={true} />
        <KPICard title="Total Analyzed Offers" value={offers.length.toString()} />
      </div>

      {/* Main Grid / Table */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm transition-colors flex flex-col">
        {/* Table Toolbar */}
        <div className="p-4 border-b border-gray-100 dark:border-gray-700 flex flex-wrap gap-4 items-center justify-between bg-gray-50/50 dark:bg-gray-800/50">
          <div className="flex gap-4 flex-1 max-w-md">
            <div className="relative flex-1">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              </span>
              <input 
                type="text" 
                placeholder="Search position or tech..." 
                className="w-full pl-9 pr-4 py-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-colors"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <select 
              className="px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-sm bg-white dark:bg-gray-900 text-gray-900 dark:text-white transition-colors"
              value={filterExp}
              onChange={(e) => setFilterExp(e.target.value as any)}
            >
              <option value="All">All Levels</option>
              <option value="Junior">Junior</option>
              <option value="Mid">Mid-level</option>
              <option value="Senior">Senior</option>
              <option value="Lead">Lead</option>
              <option value="Staff">Staff</option>
            </select>
          </div>

          <div className="flex items-center gap-3">
            {selectedIds.size > 0 && (
              <div className="flex items-center gap-3 animate-in fade-in slide-in-from-right-2">
                <span className="text-sm font-medium text-blue-600 dark:text-blue-400">{selectedIds.size} selected</span>
                <button 
                  onClick={handleCompareClick}
                  disabled={selectedIds.size < 2}
                  className="px-4 py-2 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/50 rounded-lg text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed border border-blue-200 dark:border-blue-800 transition-all"
                >
                  Compare Now
                </button>
              </div>
            )}
            <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <ICONS.Filter />
            </button>
          </div>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700 transition-colors">
              <tr>
                <th className="px-6 py-4 w-12">
                  <input 
                    type="checkbox" 
                    className="rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-blue-600 focus:ring-blue-500" 
                    onChange={(e) => {
                      const allPageIds = paginatedOffers.map(o => o.id);
                      const newSelected = new Set(selectedIds);
                      if (e.target.checked) allPageIds.forEach(id => newSelected.add(id));
                      else allPageIds.forEach(id => newSelected.delete(id));
                      setSelectedIds(newSelected);
                    }}
                    checked={paginatedOffers.length > 0 && paginatedOffers.every(o => selectedIds.has(o.id))}
                  />
                </th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Position</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Salary Range</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Mode</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Languages</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase text-right">Added</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {paginatedOffers.map(offer => (
                <tr 
                  key={offer.id} 
                  className={`hover:bg-blue-50/30 dark:hover:bg-blue-900/10 transition-colors cursor-pointer ${selectedIds.has(offer.id) ? 'bg-blue-50/50 dark:bg-blue-900/20' : ''}`}
                  onClick={() => toggleSelect(offer.id)}
                >
                  <td className="px-6 py-4" onClick={(e) => e.stopPropagation()}>
                    <input 
                      type="checkbox" 
                      className="rounded border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-blue-600 focus:ring-blue-500" 
                      checked={selectedIds.has(offer.id)}
                      onChange={() => toggleSelect(offer.id)}
                    />
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-semibold text-gray-900 dark:text-white text-sm">{offer.title}</div>
                    <div className="text-[11px] text-gray-400 dark:text-gray-500 font-mono tracking-tighter line-clamp-1">{offer.techStack.join(', ')}</div>
                  </td>
                  <td className="px-6 py-4 font-semibold text-gray-900 dark:text-gray-100">
                    ${offer.salaryMin.toLocaleString()} - ${offer.salaryMax.toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    <Badge color={offer.workMode === 'Remote' ? 'green' : 'gray'}>
                      {offer.workMode}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-2">
                      {offer.languages?.map((lang, idx) => (
                        <div key={idx} className="flex items-center gap-1">
                          <span className="text-[10px] font-medium text-gray-500 dark:text-gray-400">{lang.name}</span>
                          <LanguageLevelBadge level={lang.level} />
                        </div>
                      )) || <span className="text-xs text-gray-400">-</span>}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right text-xs text-gray-400 dark:text-gray-500">
                    {new Date(offer.createdAt).toLocaleDateString()}
                  </td>
                </tr>
              ))}
              {paginatedOffers.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="flex flex-col items-center gap-2 text-gray-400 dark:text-gray-600">
                      <ICONS.Analytics />
                      <p className="text-sm">No offers match your search criteria.</p>
                      <button onClick={() => {setSearchTerm(''); setFilterExp('All');}} className="text-blue-600 dark:text-blue-400 font-medium text-sm mt-2">Clear Filters</button>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="p-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50/30 dark:bg-gray-900/30 flex items-center justify-between">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Showing <span className="font-medium text-gray-900 dark:text-white">{(currentPage - 1) * PAGE_SIZE + 1}</span> to <span className="font-medium text-gray-900 dark:text-white">{Math.min(currentPage * PAGE_SIZE, filteredOffers.length)}</span> of <span className="font-medium text-gray-900 dark:text-white">{filteredOffers.length}</span> results
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-white dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <div className="flex items-center gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                    currentPage === page 
                      ? 'bg-blue-600 text-white' 
                      : 'text-gray-600 dark:text-gray-400 hover:bg-white dark:hover:bg-gray-800'
                  }`}
                >
                  {page}
                </button>
              ))}
            </div>
            <button 
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages || totalPages === 0}
              className="px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-white dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
