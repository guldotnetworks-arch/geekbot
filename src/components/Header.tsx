interface HeaderProps {
  lastUpdated: Date | null;
  loading: boolean;
  onRefresh: () => void;
}

export default function Header({ lastUpdated, loading }: HeaderProps) {
  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl">₿</span>
          <div>
            <h1 className="text-xl font-bold text-white">Crypto Portfolio Simulator</h1>
            <p className="text-xs text-gray-500">Track &amp; simulate your crypto investments</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {loading && (
            <span className="flex items-center gap-1.5 text-xs text-yellow-400">
              <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-pulse" />
              Fetching prices…
            </span>
          )}
          {!loading && lastUpdated && (
            <span className="text-xs text-gray-500">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>
    </header>
  );
}
