import { useState, useMemo } from 'react';
import { HoldingWithStats } from '../types';
import { formatCurrency, formatPercent } from '../utils/formatters';

interface SimulatorProps {
  holdings: HoldingWithStats[];
}

type Scenario = 'custom' | 'bull' | 'bear' | 'moon' | 'crash';

const PRESETS: Record<Exclude<Scenario, 'custom'>, { label: string; emoji: string; pct: number }> =
  {
    bull: { label: 'Bull Run', emoji: '🐂', pct: 50 },
    bear: { label: 'Bear Market', emoji: '🐻', pct: -40 },
    moon: { label: 'To the Moon', emoji: '🚀', pct: 200 },
    crash: { label: 'Crypto Winter', emoji: '❄️', pct: -75 },
  };

export default function Simulator({ holdings }: SimulatorProps) {
  const [scenario, setScenario] = useState<Scenario>('custom');
  const [customChanges, setCustomChanges] = useState<Record<string, number>>({});

  const getPriceChange = (coinId: string): number => {
    if (scenario === 'custom') return customChanges[coinId] ?? 0;
    return PRESETS[scenario].pct;
  };

  const projected = useMemo(() => {
    return holdings.map(h => {
      const pct = getPriceChange(h.coinId);
      const projectedPrice = h.currentPrice * (1 + pct / 100);
      const projectedValue = h.amount * projectedPrice;
      return { ...h, projectedPrice, projectedValue, pct };
    });
  }, [holdings, scenario, customChanges]);

  const currentTotal = holdings.reduce((s, h) => s + h.currentValue, 0);
  const projectedTotal = projected.reduce((s, h) => s + h.projectedValue, 0);
  const projectedPnL = projectedTotal - currentTotal;
  const projectedPnLPct = currentTotal > 0 ? (projectedPnL / currentTotal) * 100 : 0;
  const totalInvested = holdings.reduce((s, h) => s + h.invested, 0);
  const projectedVsInvested = projectedTotal - totalInvested;
  const projectedVsInvestedPct =
    totalInvested > 0 ? (projectedVsInvested / totalInvested) * 100 : 0;

  const setCustomChange = (coinId: string, value: number) => {
    setCustomChanges(prev => ({ ...prev, [coinId]: value }));
  };

  return (
    <div className="space-y-6">
      {/* Scenario selector */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <h3 className="text-white font-semibold mb-4">Price Scenario</h3>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          <button
            onClick={() => setScenario('custom')}
            className={`px-3 py-2.5 rounded-lg text-sm font-medium transition-colors border ${
              scenario === 'custom'
                ? 'bg-blue-600 border-blue-500 text-white'
                : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
            }`}
          >
            🎛 Custom
          </button>
          {(Object.entries(PRESETS) as [Exclude<Scenario, 'custom'>, (typeof PRESETS)[Exclude<Scenario, 'custom'>]][]).map(
            ([key, preset]) => (
              <button
                key={key}
                onClick={() => setScenario(key)}
                className={`px-3 py-2.5 rounded-lg text-sm font-medium transition-colors border ${
                  scenario === key
                    ? 'bg-blue-600 border-blue-500 text-white'
                    : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {preset.emoji} {preset.label}
                <span
                  className={`ml-1 text-xs ${preset.pct >= 0 ? 'text-green-400' : 'text-red-400'}`}
                >
                  {formatPercent(preset.pct)}
                </span>
              </button>
            ),
          )}
        </div>
      </div>

      {/* Custom sliders */}
      {scenario === 'custom' && holdings.length > 0 && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <h3 className="text-white font-semibold mb-4">Adjust Price Changes</h3>
          <div className="space-y-5">
            {holdings.map(h => {
              const pct = customChanges[h.coinId] ?? 0;
              return (
                <div key={h.coinId}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {h.image && (
                        <img src={h.image} alt={h.name} className="w-5 h-5 rounded-full" />
                      )}
                      <span className="text-white text-sm font-medium">
                        {h.symbol.toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-sm font-medium ${pct >= 0 ? 'text-green-400' : 'text-red-400'}`}
                      >
                        {pct >= 0 ? '+' : ''}
                        {pct}%
                      </span>
                      <input
                        type="number"
                        value={pct}
                        onChange={e => setCustomChange(h.coinId, parseFloat(e.target.value) || 0)}
                        className="w-20 bg-gray-700 border border-gray-600 rounded px-2 py-1 text-white text-xs text-right focus:outline-none focus:border-blue-500"
                      />
                    </div>
                  </div>
                  <input
                    type="range"
                    min="-90"
                    max="500"
                    value={pct}
                    onChange={e => setCustomChange(h.coinId, parseInt(e.target.value))}
                    className="w-full h-1.5 bg-gray-600 rounded-full appearance-none cursor-pointer accent-blue-500"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>-90%</span>
                    <span>0%</span>
                    <span>+500%</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Results */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <h3 className="text-white font-semibold mb-4">Projected Outcome</h3>

        {holdings.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Add holdings to run simulations.</p>
        ) : (
          <>
            {/* Summary numbers */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">Current Value</p>
                <p className="text-white font-bold text-lg">{formatCurrency(currentTotal)}</p>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">Projected Value</p>
                <p className="text-white font-bold text-lg">{formatCurrency(projectedTotal)}</p>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">Gain vs Now</p>
                <p
                  className={`font-bold text-lg ${projectedPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}
                >
                  {formatCurrency(projectedPnL)}
                </p>
                <p
                  className={`text-xs ${projectedPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}
                >
                  {formatPercent(projectedPnLPct)}
                </p>
              </div>
              <div className="bg-gray-700/50 rounded-lg p-4">
                <p className="text-xs text-gray-400 mb-1">Total P&L vs Invested</p>
                <p
                  className={`font-bold text-lg ${projectedVsInvested >= 0 ? 'text-green-400' : 'text-red-400'}`}
                >
                  {formatCurrency(projectedVsInvested)}
                </p>
                <p
                  className={`text-xs ${projectedVsInvested >= 0 ? 'text-green-400' : 'text-red-400'}`}
                >
                  {formatPercent(projectedVsInvestedPct)}
                </p>
              </div>
            </div>

            {/* Per-asset table */}
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-xs text-gray-400 uppercase border-b border-gray-700">
                    <th className="text-left pb-2">Asset</th>
                    <th className="text-right pb-2">Change</th>
                    <th className="text-right pb-2">Proj. Price</th>
                    <th className="text-right pb-2">Proj. Value</th>
                    <th className="text-right pb-2">Gain vs Now</th>
                  </tr>
                </thead>
                <tbody>
                  {projected.map(h => {
                    const gainVsNow = h.projectedValue - h.currentValue;
                    return (
                      <tr key={h.id} className="border-b border-gray-700/30 last:border-0">
                        <td className="py-3">
                          <div className="flex items-center gap-2">
                            {h.image && (
                              <img
                                src={h.image}
                                alt={h.name}
                                className="w-5 h-5 rounded-full"
                              />
                            )}
                            <span className="text-white">{h.symbol.toUpperCase()}</span>
                          </div>
                        </td>
                        <td className="py-3 text-right">
                          <span
                            className={`font-medium ${h.pct >= 0 ? 'text-green-400' : 'text-red-400'}`}
                          >
                            {formatPercent(h.pct)}
                          </span>
                        </td>
                        <td className="py-3 text-right text-gray-300">
                          {formatCurrency(h.projectedPrice)}
                        </td>
                        <td className="py-3 text-right text-white font-medium">
                          {formatCurrency(h.projectedValue)}
                        </td>
                        <td className="py-3 text-right">
                          <span
                            className={`font-medium ${gainVsNow >= 0 ? 'text-green-400' : 'text-red-400'}`}
                          >
                            {gainVsNow >= 0 ? '+' : ''}
                            {formatCurrency(gainVsNow)}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
