import { HoldingWithStats } from '../types';
import { formatCurrency, formatPercent, formatAmount } from '../utils/formatters';

interface PortfolioTableProps {
  holdings: HoldingWithStats[];
  onRemove: (id: string) => void;
  onAddClick: () => void;
}

function PnLBadge({ value, percent }: { value: number; percent: number }) {
  const positive = value >= 0;
  return (
    <div className={`text-right ${positive ? 'text-green-400' : 'text-red-400'}`}>
      <p className="font-medium">{formatCurrency(Math.abs(value))}</p>
      <p className="text-xs">{formatPercent(percent)}</p>
    </div>
  );
}

function Change24h({ value }: { value: number }) {
  const positive = value >= 0;
  return (
    <span
      className={`text-sm font-medium px-2 py-0.5 rounded-full ${
        positive ? 'bg-green-400/10 text-green-400' : 'bg-red-400/10 text-red-400'
      }`}
    >
      {formatPercent(value)}
    </span>
  );
}

export default function PortfolioTable({ holdings, onRemove, onAddClick }: PortfolioTableProps) {
  if (holdings.length === 0) {
    return (
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-12 text-center">
        <p className="text-4xl mb-3">📊</p>
        <p className="text-white font-medium mb-1">No holdings yet</p>
        <p className="text-gray-400 text-sm mb-4">Add your first crypto holding to get started.</p>
        <button
          onClick={onAddClick}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Add Holding
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
        <h2 className="text-white font-semibold">Holdings</h2>
        <button
          onClick={onAddClick}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <span className="text-base leading-none">+</span> Add
        </button>
      </div>

      {/* Desktop table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-xs text-gray-400 uppercase tracking-wide border-b border-gray-700">
              <th className="text-left px-6 py-3">Asset</th>
              <th className="text-right px-4 py-3">Holdings</th>
              <th className="text-right px-4 py-3">Avg Buy</th>
              <th className="text-right px-4 py-3">Current Price</th>
              <th className="text-right px-4 py-3">Value</th>
              <th className="text-right px-4 py-3">P&L</th>
              <th className="text-right px-4 py-3">24h</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {holdings.map(h => (
              <tr
                key={h.id}
                className="border-b border-gray-700/50 last:border-0 hover:bg-gray-700/20 transition-colors"
              >
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    {h.image ? (
                      <img src={h.image} alt={h.name} className="w-8 h-8 rounded-full" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-xs font-bold text-white">
                        {h.symbol.slice(0, 2).toUpperCase()}
                      </div>
                    )}
                    <div>
                      <p className="text-white font-medium">{h.name}</p>
                      <p className="text-gray-400 text-xs">{h.symbol.toUpperCase()}</p>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-4 text-right">
                  <p className="text-white">{formatAmount(h.amount)}</p>
                  <p className="text-gray-400 text-xs">{h.symbol.toUpperCase()}</p>
                </td>
                <td className="px-4 py-4 text-right text-gray-300">{formatCurrency(h.buyPrice)}</td>
                <td className="px-4 py-4 text-right text-white font-medium">
                  {formatCurrency(h.currentPrice)}
                </td>
                <td className="px-4 py-4 text-right text-white font-medium">
                  {formatCurrency(h.currentValue)}
                </td>
                <td className="px-4 py-4">
                  <PnLBadge value={h.pnl} percent={h.pnlPercent} />
                </td>
                <td className="px-4 py-4 text-right">
                  <Change24h value={h.change24h} />
                </td>
                <td className="px-4 py-4">
                  <button
                    onClick={() => onRemove(h.id)}
                    className="text-gray-500 hover:text-red-400 transition-colors text-lg leading-none"
                    title="Remove"
                  >
                    ×
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile cards */}
      <div className="md:hidden divide-y divide-gray-700">
        {holdings.map(h => (
          <div key={h.id} className="px-4 py-4 flex items-start justify-between gap-3">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              {h.image ? (
                <img src={h.image} alt={h.name} className="w-10 h-10 rounded-full flex-shrink-0" />
              ) : (
                <div className="w-10 h-10 rounded-full bg-gray-600 flex items-center justify-center text-sm font-bold text-white flex-shrink-0">
                  {h.symbol.slice(0, 2).toUpperCase()}
                </div>
              )}
              <div className="min-w-0">
                <p className="text-white font-medium truncate">{h.name}</p>
                <p className="text-gray-400 text-xs">
                  {formatAmount(h.amount)} {h.symbol.toUpperCase()}
                </p>
                <p className="text-gray-400 text-xs">@ {formatCurrency(h.currentPrice)}</p>
              </div>
            </div>
            <div className="text-right flex-shrink-0">
              <p className="text-white font-medium">{formatCurrency(h.currentValue)}</p>
              <p className={`text-sm font-medium ${h.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {formatPercent(h.pnlPercent)}
              </p>
              <button
                onClick={() => onRemove(h.id)}
                className="text-gray-500 hover:text-red-400 transition-colors text-sm mt-1"
              >
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
