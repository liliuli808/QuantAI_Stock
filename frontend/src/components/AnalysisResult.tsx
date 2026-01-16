import React from 'react';
import { en } from '../locales/en';
import { zh } from '../locales/zh';

// Define types locally or import (simpler locally for now)
interface AnalysisData {
    ticker: string;
    current_price: number;
    tech_score: number;
    tech_signal: string;
    sentiment_score: number;
    sentiment_summary: string;
    advice_action: string;
    advice_rationale: string;
    entry_point?: number;
    exit_point?: number;
    indicators: any;
    news_headlines: string[];
}

interface Props {
    data: AnalysisData;
    lang: 'en' | 'zh';
}

const AnalysisResult: React.FC<Props> = ({ data, lang }) => {
    const t = lang === 'en' ? en : zh;

    const getScoreColor = (score: number) => {
        if (score >= 70) return 'text-green-500';
        if (score >= 40) return 'text-yellow-500';
        return 'text-red-500';
    };

    const downloadReport = async (type: 'pdf' | 'html') => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/report/${type}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ analysis_data: data, language: lang })
            });

            if (type === 'html') {
                const text = await response.text();
                const newWindow = window.open();
                newWindow?.document.write(text);
            } else {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `report_${data.ticker}.pdf`;
                a.click();
            }
        } catch (e) {
            console.error("Download failed", e);
        }
    };

    return (
        <div className="w-full max-w-4xl bg-gray-800 rounded-xl p-6 shadow-2xl mt-8 animate-fade-in">
            <div className="flex justify-between items-center border-b border-gray-700 pb-4 mb-4">
                <div>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                        {data.ticker}
                    </h2>
                    <p className="text-gray-400 text-sm">Price: ${data.current_price.toFixed(2)}</p>
                </div>
                <div className="flex gap-2">
                    <button onClick={() => downloadReport('pdf')} className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm transition font-medium">
                        {t.results.download_pdf}
                    </button>
                    <button onClick={() => downloadReport('html')} className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition font-medium">
                        {t.results.download_html}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Technical Score */}
                <div className="bg-gray-700/50 p-4 rounded-lg text-center backdrop-blur-sm">
                    <h3 className="text-gray-400 text-sm uppercase tracking-wider mb-2">{t.results.score}</h3>
                    <div className={`text-4xl font-bold ${getScoreColor(data.tech_score)}`}>
                        {data.tech_score.toFixed(1)}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{data.tech_signal}</p>
                </div>

                {/* Sentiment Score */}
                <div className="bg-gray-700/50 p-4 rounded-lg text-center backdrop-blur-sm">
                    <h3 className="text-gray-400 text-sm uppercase tracking-wider mb-2">{t.results.sentiment}</h3>
                    <div className={`text-4xl font-bold ${getScoreColor(data.sentiment_score)}`}>
                        {data.sentiment_score.toFixed(1)}
                    </div>
                    <p className="text-xs text-gray-500 mt-1 line-clamp-1">{data.sentiment_summary}</p>
                </div>

                {/* Advice Action */}
                <div className="bg-gradient-to-br from-indigo-900 to-gray-800 p-4 rounded-lg text-center border border-indigo-500/30">
                    <h3 className="text-indigo-400 text-sm uppercase tracking-wider mb-2">{t.results.advice}</h3>
                    <div className="text-3xl font-extrabold text-white">
                        {data.advice_action}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <h3 className="text-xl font-semibold mb-3 border-l-4 border-blue-500 pl-3">{t.results.advice}</h3>
                    <div className="bg-gray-700 p-4 rounded-lg">
                        <p className="text-gray-300 mb-2">{data.advice_rationale}</p>
                        {data.entry_point && (
                            <div className="flex justify-between mt-3 text-sm">
                                <span className="text-gray-400">Entry Target:</span>
                                <span className="text-green-400 font-mono">${data.entry_point.toFixed(2)}</span>
                            </div>
                        )}
                        {data.exit_point && (
                            <div className="flex justify-between mt-1 text-sm">
                                <span className="text-gray-400">Exit Target:</span>
                                <span className="text-red-400 font-mono">${data.exit_point.toFixed(2)}</span>
                            </div>
                        )}
                    </div>
                </div>

                <div>
                    <h3 className="text-xl font-semibold mb-3 border-l-4 border-purple-500 pl-3">{t.results.indicators}</h3>
                    <div className="bg-gray-700 p-4 rounded-lg text-sm space-y-2">
                        <div className="flex justify-between">
                            <span>RSI (14)</span>
                            <span className="font-mono text-gray-300">{data.indicators.RSI.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>MACD</span>
                            <span className="font-mono text-gray-300">{data.indicators.MACD.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Bollinger Upper</span>
                            <span className="font-mono text-gray-300">{data.indicators.BB_High.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>MA20</span>
                            <span className="font-mono text-gray-300">{data.indicators.MA20.toFixed(2)}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnalysisResult;
