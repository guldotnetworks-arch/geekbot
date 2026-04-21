import { PortfolioSummary } from '../types';
import { formatCurrency, formatPercent } from '../utils/formatters';

interface SummaryCardsProps {
  summary: PortfolioSummary;
}

function Card({
  label,
  value,
  sub,
  subPositive,
}: {
  label: string;
  value: string;
  sub?: string;
  subPositive?: boolean;
}) {
  return (
    <div className="bg-gray-800 rounded-xl p-5 border border-gray-700">
      <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      {sub && (
        <p
          className={`text-sm mt-1 font-medium ${
            subPositive === undefined
              ? 'text-gray-400'
              : subPositive
              ? 'text-green-400'
              : 'text-red-400'
          }`}
        >
          {sub}
        </p>
      )}
    </div>
  );
}

export default function SummaryCards({ summary }: SummaryCardsProps) {
  const { totalValue, totalInvested, totalPnL, totalPnLPercent, change24h, bestPerformer } =
    summary;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <Card label="Portfolio Value" value={formatCurrency(totalValue)} />
      <Card
        label="Total P&L"
        value={formatCurrency(totalPnL)}
        sub={`${formatPercent(totalPnLPercent)} vs invested`}
        subPositive={totalPnL >= 0}
      />
      <Card
        label="Total Invested"
        value={formatCurrency(totalInvested)}
        sub="Cost basis"
      />
      <Card
        label="24h Change"
        value={formatCurrency(change24h)}
        sub={
          bestPerformer
            ? `Best: ${bestPerformer.symbol.toUpperCase()} ${formatPercent(bestPerformer.pnlPercent)}`
            : undefined
        }
        subPositive={bestPerformer ? bestPerformer.pnlPercent >= 0 : undefined}
      />
    </div>
  );
}
