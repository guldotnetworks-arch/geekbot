import { useState, useEffect, useRef } from 'react';
import { CryptoPrice } from '../types';

const POPULAR_COIN_IDS = [
  'bitcoin',
  'ethereum',
  'binancecoin',
  'solana',
  'cardano',
  'ripple',
  'dogecoin',
  'avalanche-2',
  'polkadot',
  'chainlink',
  'litecoin',
  'uniswap',
  'matic-network',
  'cosmos',
  'stellar',
  'shiba-inu',
  'tron',
  'near',
  'aptos',
  'arbitrum',
];

const BASE_URL = 'https://api.coingecko.com/api/v3';
const REFRESH_INTERVAL = 60_000;

export function useCryptoData(portfolioCoinIds: string[]) {
  const [prices, setPrices] = useState<Record<string, CryptoPrice>>({});
  const [availableCoins, setAvailableCoins] = useState<CryptoPrice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const allCoinIds = useRef<string[]>([]);

  useEffect(() => {
    const merged = Array.from(new Set([...POPULAR_COIN_IDS, ...portfolioCoinIds]));
    allCoinIds.current = merged;
  }, [portfolioCoinIds.join(',')]);

  const fetchPrices = async (coinIds: string[]) => {
    const ids = coinIds.join(',');
    const response = await fetch(
      `${BASE_URL}/coins/markets?vs_currency=usd&ids=${ids}&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=24h`,
    );
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return response.json() as Promise<CryptoPrice[]>;
  };

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const ids = Array.from(new Set([...POPULAR_COIN_IDS, ...portfolioCoinIds]));
        const data = await fetchPrices(ids);

        if (cancelled) return;

        const map: Record<string, CryptoPrice> = {};
        data.forEach(coin => {
          map[coin.id] = coin;
        });
        setPrices(map);
        setAvailableCoins(data);
        setLastUpdated(new Date());
      } catch (err) {
        if (!cancelled) {
          setError('Failed to fetch prices. Retrying in 60s.');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    const interval = setInterval(load, REFRESH_INTERVAL);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [portfolioCoinIds.join(',')]);

  return { prices, availableCoins, loading, error, lastUpdated };
}
