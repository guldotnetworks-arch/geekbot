export interface CryptoPrice {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  price_change_percentage_24h: number;
  image: string;
  market_cap: number;
}

export interface Holding {
  id: string;
  coinId: string;
  symbol: string;
  name: string;
  amount: number;
  buyPrice: number;
  image?: string;
}

export interface HoldingWithStats extends Holding {
  currentPrice: number;
  currentValue: number;
  invested: number;
  pnl: number;
  pnlPercent: number;
  change24h: number;
}

export interface PortfolioSummary {
  totalValue: number;
  totalInvested: number;
  totalPnL: number;
  totalPnLPercent: number;
  change24h: number;
  bestPerformer: HoldingWithStats | null;
  worstPerformer: HoldingWithStats | null;
}
