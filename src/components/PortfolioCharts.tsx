import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { HoldingWithStats } from '../types';
import { formatCurrency, formatCompactCurrency } from '../utils/formatters';

const COLORS = [
  '#3b82f6',
  '#8b5cf6',
  '#06b6d4',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#ec4899',
  '#14b8a6',
  '#f97316',
  '#6366f1',
];

interface PortfolioChartsProps {
  holdings: HoldingWithStats[];
}

interface PieEntry {
  name: string;
  value: number;
  symbol: string;
}

const CustomTooltip = ({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: PieEntry }>;
}) => {
  if (active && payload && payload.length) {
    const d = payload[0];
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 shadow-lg">
        <p className="text-white text-sm font-medium">{d.payload?.symbol ?? d.name}</p>
        <p className="text-gray-300 text-sm">{formatCurrency(d.value)}</p>
      </div>
    );
  }
  return null;
};

const PnLTooltip = ({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}) => {
  if (active && payload && payload.length) {
    const val = payload[0].value;
    return (
      <div className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 shadow-lg">
        <p className="text-white text-sm font-medium">{label}</p>
        <p className={`text-sm ${val >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {val >= 0 ? '+' : ''}
          {formatCurrency(val)}
        </p>
      </div>
    );
  }
  return null;
};

export default function PortfolioCharts({ holdings }: PortfolioChartsProps) {
  const pieData: PieEntry[] = holdings.map(h => ({
    name: h.name,
    symbol: h.symbol.toUpperCase(),
    value: h.currentValue,
  }));

  const pnlData = [...holdings]
    .sort((a, b) => b.pnl - a.pnl)
    .map(h => ({
      name: h.symbol.toUpperCase(),
      pnl: parseFloat(h.pnl.toFixed(2)),
    }));

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Allocation pie */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <h3 className="text-white font-semibold mb-4">Portfolio Allocation</h3>
        {holdings.length === 0 ? (
          <p className="text-gray-500 text-center py-12">No holdings to display</p>
        ) : (
          <>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {pieData.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  formatter={(value) => (
                    <span className="text-gray-300 text-xs">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-2 space-y-1.5">
              {pieData.map((d, i) => {
                const total = pieData.reduce((s, x) => s + x.value, 0);
                const pct = total > 0 ? ((d.value / total) * 100).toFixed(1) : '0';
                return (
                  <div key={d.symbol} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-2.5 h-2.5 rounded-full"
                        style={{ background: COLORS[i % COLORS.length] }}
                      />
                      <span className="text-gray-300">{d.symbol}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-gray-400">{pct}%</span>
                      <span className="text-white">{formatCurrency(d.value)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      {/* P&L bar chart */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <h3 className="text-white font-semibold mb-4">Profit / Loss by Asset</h3>
        {holdings.length === 0 ? (
          <p className="text-gray-500 text-center py-12">No holdings to display</p>
        ) : (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={pnlData} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <YAxis
                tickFormatter={formatCompactCurrency}
                tick={{ fill: '#9ca3af', fontSize: 11 }}
                width={70}
              />
              <Tooltip content={<PnLTooltip />} />
              <Bar
                dataKey="pnl"
                radius={[4, 4, 0, 0]}
                label={false}
              >
                {pnlData.map((d, i) => (
                  <Cell key={i} fill={d.pnl >= 0 ? '#10b981' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
