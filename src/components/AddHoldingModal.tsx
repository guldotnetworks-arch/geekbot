import { useState } from 'react';
import { CryptoPrice, Holding } from '../types';

interface AddHoldingModalProps {
  availableCoins: CryptoPrice[];
  onAdd: (holding: Omit<Holding, 'id'>) => void;
  onClose: () => void;
}

export default function AddHoldingModal({ availableCoins, onAdd, onClose }: AddHoldingModalProps) {
  const [selectedCoin, setSelectedCoin] = useState<CryptoPrice | null>(null);
  const [amount, setAmount] = useState('');
  const [buyPrice, setBuyPrice] = useState('');
  const [search, setSearch] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);

  const filtered = availableCoins.filter(
    c =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.symbol.toLowerCase().includes(search.toLowerCase()),
  );

  const selectCoin = (coin: CryptoPrice) => {
    setSelectedCoin(coin);
    setSearch(coin.name);
    setBuyPrice(coin.current_price.toString());
    setShowDropdown(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCoin || !amount || !buyPrice) return;
    onAdd({
      coinId: selectedCoin.id,
      symbol: selectedCoin.symbol,
      name: selectedCoin.name,
      amount: parseFloat(amount),
      buyPrice: parseFloat(buyPrice),
      image: selectedCoin.image,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-2xl w-full max-w-md border border-gray-700 shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Add Holding</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl leading-none">
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Coin search */}
          <div className="relative">
            <label className="block text-xs text-gray-400 mb-1.5">Select Coin</label>
            <input
              type="text"
              placeholder="Search Bitcoin, ETH…"
              value={search}
              onChange={e => {
                setSearch(e.target.value);
                setSelectedCoin(null);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            {showDropdown && filtered.length > 0 && (
              <ul className="absolute z-10 w-full mt-1 bg-gray-700 border border-gray-600 rounded-lg shadow-lg max-h-52 overflow-y-auto">
                {filtered.slice(0, 15).map(coin => (
                  <li
                    key={coin.id}
                    onClick={() => selectCoin(coin)}
                    className="flex items-center gap-2.5 px-3 py-2 hover:bg-gray-600 cursor-pointer"
                  >
                    <img src={coin.image} alt={coin.name} className="w-5 h-5 rounded-full" />
                    <span className="text-white text-sm">{coin.name}</span>
                    <span className="text-gray-400 text-xs ml-auto">
                      {coin.symbol.toUpperCase()}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Amount */}
          <div>
            <label className="block text-xs text-gray-400 mb-1.5">
              Amount{selectedCoin ? ` (${selectedCoin.symbol.toUpperCase()})` : ''}
            </label>
            <input
              type="number"
              placeholder="e.g. 0.5"
              value={amount}
              onChange={e => setAmount(e.target.value)}
              min="0"
              step="any"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Buy price */}
          <div>
            <label className="block text-xs text-gray-400 mb-1.5">Avg. Buy Price (USD)</label>
            <input
              type="number"
              placeholder="e.g. 42000"
              value={buyPrice}
              onChange={e => setBuyPrice(e.target.value)}
              min="0"
              step="any"
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
            {selectedCoin && (
              <p className="text-xs text-gray-500 mt-1">
                Current price: ${selectedCoin.current_price.toLocaleString()}
              </p>
            )}
          </div>

          {/* Preview */}
          {selectedCoin && amount && buyPrice && (
            <div className="bg-gray-700/50 rounded-lg p-3 text-sm">
              <p className="text-gray-300">
                Total invested:{' '}
                <span className="text-white font-medium">
                  ${(parseFloat(amount) * parseFloat(buyPrice)).toLocaleString()}
                </span>
              </p>
              <p className="text-gray-300">
                Current value:{' '}
                <span className="text-white font-medium">
                  ${(parseFloat(amount) * selectedCoin.current_price).toLocaleString()}
                </span>
              </p>
            </div>
          )}

          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2.5 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!selectedCoin || !amount || !buyPrice}
              className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:text-gray-400 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Add to Portfolio
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
