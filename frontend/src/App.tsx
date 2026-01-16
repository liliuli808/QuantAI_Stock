import { useState } from 'react';
import { en } from './locales/en';
import { zh } from './locales/zh';
import AnalysisResult from './components/AnalysisResult';
import { LineChart, Briefcase, Search, Activity, Globe } from 'lucide-react';

function App() {
  const [lang, setLang] = useState<'en' | 'zh'>('en');
  const t = lang === 'en' ? en : zh;

  const [mode, setMode] = useState<'entry' | 'holding'>('entry');
  const [ticker, setTicker] = useState('');
  const [cost, setCost] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!ticker) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const payload: any = { stock_code: ticker };
      if (mode === 'holding' && cost) {
        payload.holding_cost = parseFloat(cost);
      }

      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(t.error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-gray-100 flex flex-col items-center p-8 font-sans selection:bg-indigo-500 selection:text-white">
      {/* Header */}
      <header className="w-full max-w-5xl flex justify-between items-center mb-12">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 p-2 rounded-lg shadow-lg shadow-indigo-500/20">
            <Activity size={28} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{t.title}</h1>
            <p className="text-xs text-gray-400 uppercase tracking-widest">{t.subtitle}</p>
          </div>
        </div>

        <button
          onClick={() => setLang(lang === 'en' ? 'zh' : 'en')}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-full border border-gray-700 transition"
        >
          <Globe size={16} />
          <span className="text-sm font-medium">{lang === 'en' ? '中文' : 'English'}</span>
        </button>
      </header>

      {/* Main Input Card */}
      <div className="w-full max-w-lg bg-gray-800 rounded-2xl shadow-xl overflow-hidden border border-gray-700">
        {/* Mode Switcher */}
        <div className="flex border-b border-gray-700">
          <button
            className={`flex-1 py-4 text-sm font-medium transition flex items-center justify-center gap-2 ${mode === 'entry' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
            onClick={() => setMode('entry')}
          >
            <Search size={18} />
            {t.modes.entry}
          </button>
          <button
            className={`flex-1 py-4 text-sm font-medium transition flex items-center justify-center gap-2 ${mode === 'holding' ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:bg-gray-700'}`}
            onClick={() => setMode('holding')}
          >
            <Briefcase size={18} />
            {t.modes.holding}
          </button>
        </div>

        {/* Form Inputs */}
        <div className="p-8 space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400 block">{t.inputs.ticker}</label>
            <div className="relative">
              <input
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                type="text"
                placeholder="e.g. AAPL"
                className="w-full bg-gray-900 border border-gray-600 rounded-lg py-3 px-4 pl-10 text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
              />
              <LineChart className="absolute left-3 top-3.5 text-gray-500" size={18} />
            </div>
          </div>

          {mode === 'holding' && (
            <div className="space-y-2 animate-fade-in">
              <label className="text-sm font-medium text-gray-400 block">{t.inputs.cost}</label>
              <div className="relative">
                <input
                  value={cost}
                  onChange={(e) => setCost(e.target.value)}
                  type="number"
                  placeholder="0.00"
                  className="w-full bg-gray-900 border border-gray-600 rounded-lg py-3 px-4 text-white placeholder-gray-600 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
                />
              </div>
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-bold py-3 rounded-lg shadow-lg shadow-indigo-500/30 transform transition active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {t.loading}
              </span>
            ) : t.inputs.analyze}
          </button>

          {error && <p className="text-red-400 text-center text-sm mt-2">{error}</p>}
        </div>
      </div>

      {/* Results Section */}
      {result && <AnalysisResult data={result} lang={lang} />}

    </div>
  );
}

export default App;
