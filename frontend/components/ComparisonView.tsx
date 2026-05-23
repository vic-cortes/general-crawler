
import React, { useMemo } from 'react';
import { JobOffer, LanguageLevel } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface ComparisonViewProps {
  offers: JobOffer[];
  onBack: () => void;
}

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

const ComparisonView: React.FC<ComparisonViewProps> = ({ offers, onBack }) => {
  const chartData = useMemo(() => {
    return offers.map((o) => ({
      name: o.title.length > 15 ? o.title.substring(0, 15) + '...' : o.title,
      min: o.salaryMin,
      max: o.salaryMax,
      avg: (o.salaryMin + o.salaryMax) / 2
    }));
  }, [offers]);

  const allTech = useMemo(() => {
    const set = new Set<string>();
    offers.forEach(o => o.techStack.forEach(t => set.add(t)));
    return Array.from(set);
  }, [offers]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          Back to Dashboard
        </button>
        <div className="text-right">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white transition-colors">Comparative Analysis</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 transition-colors">{offers.length} offers selected</p>
        </div>
      </div>

      {/* Salary Comparison Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-200">
          <h2 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider mb-6">Salary Landscape</h2>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 10}} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#9ca3af', fontSize: 12}} tickFormatter={(value) => `$${value/1000}k`} />
                <Tooltip 
                  cursor={{fill: '#f9fafb'}}
                  contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', backgroundColor: '#1f2937', color: '#fff'}}
                  itemStyle={{ color: '#fff' }}
                  labelStyle={{ color: '#9ca3af' }}
                  formatter={(value) => [`$${(Number(value)).toLocaleString()}`, '']}
                />
                <Legend iconType="circle" />
                <Bar dataKey="min" name="Min Salary" fill="#93c5fd" radius={[4, 4, 0, 0]} />
                <Bar dataKey="max" name="Max Salary" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm transition-colors duration-200">
          <h2 className="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider mb-4">Tech Overlap</h2>
          <div className="space-y-4">
            {allTech.slice(0, 10).map(tech => {
              const count = offers.filter(o => o.techStack.includes(tech)).length;
              const percentage = (count / offers.length) * 100;
              return (
                <div key={tech} className="space-y-1.5">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-gray-700 dark:text-gray-300">{tech}</span>
                    <span className="text-gray-500 dark:text-gray-500">{count}/{offers.length}</span>
                  </div>
                  <div className="w-full bg-gray-100 dark:bg-gray-900 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-blue-500 dark:bg-blue-400 h-full rounded-full transition-all" style={{ width: `${percentage}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Side by Side Grid */}
      <div className="overflow-x-auto pb-6">
        <div className="inline-flex gap-6 min-w-full">
          {offers.map((offer, idx) => (
            <div key={offer.id} className="w-80 flex-shrink-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden shadow-sm flex flex-col transition-colors">
              <div className="p-5 bg-gray-50 dark:bg-gray-900/50 border-b border-gray-100 dark:border-gray-700 transition-colors">
                <div className="flex items-center justify-between mb-1">
                  <div className="text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest">Option {idx + 1}</div>
                  <Badge color="gray">{offer.sourceName}</Badge>
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-white line-clamp-1">{offer.title}</div>
                <div className="text-xl font-bold text-blue-600 dark:text-blue-400 mt-1">
                  ${offer.salaryMax.toLocaleString()} <span className="text-xs font-normal text-gray-500 dark:text-gray-400">/{offer.salaryCurrency}</span>
                </div>
              </div>
              
              <div className="p-5 space-y-6 flex-1">
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase">Information Source</label>
                  <a 
                    href={offer.sourceUrl} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="flex items-center justify-between p-2 rounded bg-gray-50 dark:bg-gray-900/50 border border-gray-100 dark:border-gray-700 group transition-all"
                  >
                    <span className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{offer.sourceName}</span>
                    <span className="text-xs text-blue-600 dark:text-blue-400 font-semibold group-hover:underline flex items-center gap-1">
                      Original
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>
                    </span>
                  </a>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase">Languages</label>
                  <div className="flex flex-col gap-2 mt-2">
                    {offer.languages?.map((lang, lidx) => (
                      <div key={lidx} className="flex items-center justify-between bg-gray-50 dark:bg-gray-900/50 p-2 rounded border border-gray-100 dark:border-gray-700">
                        <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{lang.name}</span>
                        <LanguageLevelBadge level={lang.level} />
                      </div>
                    )) || <span className="text-xs text-gray-400 italic">No specific language requirement</span>}
                  </div>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase">Tech Stack</label>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {offer.techStack.map(t => (
                      <span key={t} className="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-[11px] font-medium rounded border border-blue-100 dark:border-blue-800 transition-colors">{t}</span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase">Work Mode</label>
                    <p className="text-sm font-semibold mt-1 text-gray-900 dark:text-white transition-colors">{offer.workMode}</p>
                  </div>
                  <div>
                    <label className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase">Experience</label>
                    <p className="text-sm font-semibold mt-1 text-gray-900 dark:text-white transition-colors">{offer.experienceLevel}</p>
                  </div>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-gray-400 dark:text-gray-500 uppercase">Key Benefits</label>
                  <ul className="mt-2 space-y-2">
                    {offer.benefits.map((b, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400 transition-colors">
                        <span className="text-green-500 dark:text-green-400 mt-1 flex-shrink-0">
                          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                        </span>
                        {b}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ComparisonView;
