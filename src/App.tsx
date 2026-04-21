import { useState, useMemo } from 'react';
import { usePortfolio } from './hooks/usePortfolio';
import { useCryptoData } from './hooks/useCryptoData';
import { HoldingWithStats, PortfolioSummary } from './types';
import Header from './components/Header';
import SummaryCards from './components/SummaryCards';
import PortfolioTable from './components/PortfolioTable';
import AddHoldingModal from './components/AddHoldingModal';
import PortfolioCharts from './components/PortfolioCharts';
import Simulator from './components/Simulator';

type Tab = 'portfolio' | 'charts' | 'simulator';

export default function App() {
  const [tab, setTab] = useState<Tab>('portfolio');
  const [showAddModal, setShowAddModal] = useState(false);
  const { holdings, addHolding, removeHolding } = usePortfolio();

  const coinIds = holdings.map(h => h.coinId);
  const { prices, availableCoins, loading, error, lastUpdated } = useCryptoData(coinIds);

  const holdingsWithStats: HoldingWithStats[] = useMemo(() => {
    return holdings.map(h => {
      const price = prices[h.coinId];
      const currentPrice = price?.current_price ?? h.buyPrice;
      const currentValue = h.amount * currentPrice;
      const invested = h.amount * h.buyPrice;
      const pnl = currentValue - invested;
      const pnlPercent = invested > 0 ? (pnl / invested) * 100 : 0;
      const change24h = price?.price_change_percentage_24h ?? 0;
      return {
        ...h,
        image: price?.image ?? h.image,
        currentPrice,
        currentValue,
        invested,
        pnl,
        pnlPercent,
        change24h,
      };
    });
  }, [holdings, prices]);

  const summary: PortfolioSummary = useMemo(() => {
    const totalValue = holdingsWithStats.reduce((s, h) => s + h.currentValue, 0);
    const totalInvested = holdingsWithStats.reduce((s, h) => s + h.invested, 0);
    const totalPnL = totalValue - totalInvested;
    const totalPnLPercent = totalInvested > 0 ? (totalPnL / totalInvested) * 100 : 0;
    const change24h = holdingsWithStats.reduce(
      (s, h) => s + h.currentValue * (h.change24h / 100),
      0,
    );

    const sorted = [...holdingsWithStats].sort((a, b) => b.pnlPercent - a.pnlPercent);
    return {
      totalValue,
      totalInvested,
      totalPnL,
      totalPnLPercent,
      change24h,
      bestPerformer: sorted[0] ?? null,
      worstPerformer: sorted[sorted.length - 1] ?? null,
    };
  }, [holdingsWithStats]);

  const tabs: { id: Tab; label: string }[] = [
    { id: 'portfolio', label: 'Portfolio' },
    { id: 'charts', label: 'Charts' },
    { id: 'simulator', label: 'Simulator' },
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <Header lastUpdated={lastUpdated} loading={loading} onRefresh={() => {}} />

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Error banner */}
        {error && (
          <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg px-4 py-3 text-yellow-300 text-sm">
            {error}
          </div>
        )}

        {/* Summary cards */}
        <SummaryCards summary={summary} />

        {/* Tab bar */}
        <div className="flex gap-1 bg-gray-800 rounded-xl p-1 w-fit border border-gray-700">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors ${
                tab === t.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        {tab === 'portfolio' && (
          <PortfolioTable
            holdings={holdingsWithStats}
            onRemove={removeHolding}
            onAddClick={() => setShowAddModal(true)}
          />
        )}
        {tab === 'charts' && <PortfolioCharts holdings={holdingsWithStats} />}
        {tab === 'simulator' && <Simulator holdings={holdingsWithStats} />}
      </main>

      {showAddModal && (
        <AddHoldingModal
          availableCoins={availableCoins}
          onAdd={addHolding}
          onClose={() => setShowAddModal(false)}
        />
      )}
    </div>
  );
}
