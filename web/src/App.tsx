import React, { useState } from 'react';
import { Layout, Database, Ghost, Map, Activity, Shield } from 'lucide-react';

const App = () => {
    const [activeTab, setActiveTab] = useState('adrs');

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-cyan-500/30">
            {/* Sidebar */}
            <aside className="fixed left-0 top-0 h-full w-64 bg-slate-900 border-r border-slate-800 p-6 flex flex-col gap-8">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
                        <Shield size={24} className="text-white" />
                    </div>
                    <span className="text-xl font-bold tracking-tight">TraceContext</span>
                </div>

                <nav className="flex flex-col gap-2">
                    <NavItem
                        icon={<Layout size={20} />}
                        label="ADR Registry"
                        active={activeTab === 'adrs'}
                        onClick={() => setActiveTab('adrs')}
                    />
                    <NavItem
                        icon={<Ghost size={20} />}
                        label="Dead-End Tracker"
                        active={activeTab === 'deadends'}
                        onClick={() => setActiveTab('deadends')}
                    />
                    <NavItem
                        icon={<Map size={20} />}
                        label="Intent Graph"
                        active={activeTab === 'graph'}
                        onClick={() => setActiveTab('graph')}
                    />
                    <NavItem
                        icon={<Database size={20} />}
                        label="Intent Vectors"
                        active={activeTab === 'vectors'}
                        onClick={() => setActiveTab('vectors')}
                    />
                </nav>

                <div className="mt-auto pt-6 border-t border-slate-800">
                    <div className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
                        <Activity className="text-green-400" size={16} />
                        <span className="text-sm font-medium">Orchestrator: Online</span>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="pl-64 p-8">
                <header className="mb-12">
                    <h1 className="text-4xl font-extrabold tracking-tight mb-2">
                        {activeTab === 'adrs' && "Architecture Decision Records"}
                        {activeTab === 'deadends' && "Dead-End Approaches"}
                        {activeTab === 'graph' && "Semantic Codebase Map"}
                        {activeTab === 'vectors' && "Intent Vector Store"}
                    </h1>
                    <p className="text-slate-400 text-lg">
                        Trace. Your decisions, permanent. Your context, shared.
                    </p>
                </header>

                <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Sample Card (Placeholder for dynamic content) */}
                    <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl hover:border-cyan-500/50 transition-all group">
                        <div className="flex justify-between items-start mb-4">
                            <span className="px-3 py-1 bg-cyan-500/10 text-cyan-400 text-xs font-bold rounded-full border border-cyan-500/20">
                                ADR-042
                            </span>
                            <span className="text-slate-500 text-sm">2h ago</span>
                        </div>
                        <h3 className="text-xl font-bold mb-3 group-hover:text-cyan-400 transition-colors">Use Dinero.js for monetary values</h3>
                        <p className="text-slate-400 text-sm leading-relaxed mb-4">
                            Decided to move away from plain floats to prevent precision errors in payment processing.
                        </p>
                        <div className="flex gap-2">
                            <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300">#payments</span>
                            <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300">#architecture</span>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
};

const NavItem = ({ icon, label, active, onClick }) => (
    <button
        onClick={onClick}
        className={`flex items-center gap-3 w-full p-3 rounded-xl transition-all ${active
                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
            }`}
    >
        {icon}
        <span className="font-medium">{label}</span>
    </button>
);

export default App;
