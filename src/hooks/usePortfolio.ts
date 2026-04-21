import { useState, useEffect, useCallback } from 'react';
import { Holding } from '../types';

const STORAGE_KEY = 'crypto-portfolio-v1';

const DEFAULT_HOLDINGS: Holding[] = [
  {
    id: '1',
    coinId: 'bitcoin',
    symbol: 'BTC',
    name: 'Bitcoin',
    amount: 0.5,
    buyPrice: 42000,
    image: 'https://assets.coingecko.com/coins/images/1/thumb/bitcoin.png',
  },
  {
    id: '2',
    coinId: 'ethereum',
    symbol: 'ETH',
    name: 'Ethereum',
    amount: 5,
    buyPrice: 2200,
    image: 'https://assets.coingecko.com/coins/images/279/thumb/ethereum.png',
  },
  {
    id: '3',
    coinId: 'solana',
    symbol: 'SOL',
    name: 'Solana',
    amount: 50,
    buyPrice: 95,
    image: 'https://assets.coingecko.com/coins/images/4128/thumb/solana.png',
  },
];

export function usePortfolio() {
  const [holdings, setHoldings] = useState<Holding[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : DEFAULT_HOLDINGS;
    } catch {
      return DEFAULT_HOLDINGS;
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(holdings));
  }, [holdings]);

  const addHolding = useCallback((holding: Omit<Holding, 'id'>) => {
    setHoldings(prev => {
      const existingIdx = prev.findIndex(h => h.coinId === holding.coinId);
      if (existingIdx >= 0) {
        const updated = [...prev];
        const old = updated[existingIdx];
        const totalAmount = old.amount + holding.amount;
        const avgBuyPrice =
          (old.amount * old.buyPrice + holding.amount * holding.buyPrice) / totalAmount;
        updated[existingIdx] = { ...old, amount: totalAmount, buyPrice: avgBuyPrice };
        return updated;
      }
      return [...prev, { ...holding, id: crypto.randomUUID() }];
    });
  }, []);

  const removeHolding = useCallback((id: string) => {
    setHoldings(prev => prev.filter(h => h.id !== id));
  }, []);

  const updateHolding = useCallback((id: string, updates: Partial<Omit<Holding, 'id'>>) => {
    setHoldings(prev => prev.map(h => (h.id === id ? { ...h, ...updates } : h)));
  }, []);

  const clearPortfolio = useCallback(() => setHoldings([]), []);

  return { holdings, addHolding, removeHolding, updateHolding, clearPortfolio };
}
