import { useState, useMemo } from 'react'
import {
  niches, countries, calcEarnings,
  sliderToViews, viewsToSlider, formatViews, formatMoney,
} from '../data/rpmData'

function EarningsBar({ label, value, max, color }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-slate-400">{label}</span>
        <span className="font-semibold text-white">{formatMoney(value)}</span>
      </div>
      <div className="h-2 w-full rounded-full bg-slate-700">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function StatCard({ label, value, sub }) {
  return (
    <div className="rounded-2xl bg-slate-800/60 border border-slate-700/50 p-5 text-center">
      <p className="text-xs font-medium uppercase tracking-widest text-slate-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
      {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
    </div>
  )
}

export default function RPMCalculator() {
  const [nicheId, setNicheId]       = useState('technology')
  const [countryCode, setCountry]   = useState('US')
  const [sliderPos, setSliderPos]   = useState(40)
  const [rawInput, setRawInput]     = useState('')
  const [inputFocused, setInputFocused] = useState(false)

  const views = sliderToViews(sliderPos)

  const niche   = useMemo(() => niches.find(n => n.id === nicheId),          [nicheId])
  const country = useMemo(() => countries.find(c => c.code === countryCode), [countryCode])

  const monthly = useMemo(
    () => calcEarnings(views, niche.rpm, country.multiplier),
    [views, niche, country],
  )

  const annual = useMemo(() => ({
    low:  +(monthly.low  * 12).toFixed(2),
    mid:  +(monthly.mid  * 12).toFixed(2),
    high: +(monthly.high * 12).toFixed(2),
  }), [monthly])

  const effectiveRPM = useMemo(() => ({
    low:  +(niche.rpm.low  * country.multiplier).toFixed(2),
    mid:  +(niche.rpm.mid  * country.multiplier).toFixed(2),
    high: +(niche.rpm.high * country.multiplier).toFixed(2),
  }), [niche, country])

  function handleSlider(e) {
    setSliderPos(Number(e.target.value))
  }

  function handleViewInput(e) {
    const raw = e.target.value.replace(/[^0-9]/g, '')
    setRawInput(raw)
    const num = Number(raw)
    if (num >= 1_000) {
      setSliderPos(viewsToSlider(num))
    }
  }

  function handleInputBlur() {
    setInputFocused(false)
    setRawInput('')
  }

  const displayViews = inputFocused ? rawInput : views.toLocaleString()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white font-sans px-4 py-12">
      {/* Header */}
      <div className="max-w-2xl mx-auto text-center mb-10">
        <div className="inline-flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-full px-4 py-1.5 mb-4">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs font-semibold uppercase tracking-widest text-red-400">YouTube RPM Calculator</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent mb-3">
          Estimate Your Earnings
        </h1>
        <p className="text-slate-400 text-base max-w-md mx-auto">
          Select your content niche, primary audience country, and monthly views to see realistic RPM-based revenue estimates.
        </p>
      </div>

      <div className="max-w-2xl mx-auto space-y-6">
        {/* Niche */}
        <div className="rounded-2xl bg-slate-800/40 border border-slate-700/50 p-6">
          <label className="block text-xs font-semibold uppercase tracking-widest text-slate-500 mb-4">
            Content Niche
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {niches.map(n => (
              <button
                key={n.id}
                onClick={() => setNicheId(n.id)}
                className={`flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150 ${
                  nicheId === n.id
                    ? 'bg-red-500 text-white shadow-lg shadow-red-500/25'
                    : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700 hover:text-white'
                }`}
              >
                <span className="text-base leading-none">{n.icon}</span>
                <span className="truncate">{n.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Country */}
        <div className="rounded-2xl bg-slate-800/40 border border-slate-700/50 p-6">
          <label className="block text-xs font-semibold uppercase tracking-widest text-slate-500 mb-4">
            Primary Audience Country
          </label>
          <div className="relative">
            <select
              value={countryCode}
              onChange={e => setCountry(e.target.value)}
              className="w-full appearance-none rounded-xl bg-slate-700/60 border border-slate-600/50 text-white px-4 py-3 pr-10 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-red-500/50 cursor-pointer"
            >
              {countries.map(c => (
                <option key={c.code} value={c.code}>
                  {c.flag}  {c.label}  —  {(c.multiplier * 100).toFixed(0)}% of US RPM
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          {/* Country RPM indicator */}
          <div className="mt-3 flex items-center gap-3">
            <div className="flex-1 h-1.5 rounded-full bg-slate-700">
              <div
                className="h-1.5 rounded-full bg-gradient-to-r from-red-500 to-orange-400 transition-all duration-500"
                style={{ width: `${country.multiplier * 100}%` }}
              />
            </div>
            <span className="text-xs text-slate-400 w-24 text-right">
              {country.flag} {(country.multiplier * 100).toFixed(0)}% of US RPM
            </span>
          </div>
        </div>

        {/* View Count */}
        <div className="rounded-2xl bg-slate-800/40 border border-slate-700/50 p-6">
          <label className="block text-xs font-semibold uppercase tracking-widest text-slate-500 mb-4">
            Monthly Views
          </label>
          <div className="flex items-center gap-4 mb-5">
            <input
              type="text"
              inputMode="numeric"
              value={displayViews}
              onFocus={() => { setInputFocused(true); setRawInput(String(views)) }}
              onChange={handleViewInput}
              onBlur={handleInputBlur}
              className="w-40 rounded-xl bg-slate-700/60 border border-slate-600/50 text-white px-4 py-2.5 text-lg font-bold text-center focus:outline-none focus:ring-2 focus:ring-red-500/50"
            />
            <span className="text-slate-400 text-sm">views / month</span>
          </div>

          <input
            type="range"
            min={0}
            max={100}
            value={sliderPos}
            onChange={handleSlider}
            className="w-full accent-red-500 cursor-pointer"
          />

          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>1K</span>
            <span>10K</span>
            <span>100K</span>
            <span>1M</span>
            <span>10M</span>
            <span>50M</span>
          </div>
        </div>

        {/* Results */}
        <div className="rounded-2xl bg-gradient-to-br from-slate-800/60 to-slate-900/60 border border-slate-700/50 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-white">Estimated Earnings</h2>
            <div className="text-xs text-slate-500 text-right">
              <div>{niche.icon} {niche.label}</div>
              <div>{country.flag} {country.label} · {formatViews(views)} views/mo</div>
            </div>
          </div>

          {/* Stat cards */}
          <div className="grid grid-cols-3 gap-3">
            <StatCard
              label="Low"
              value={formatMoney(monthly.low)}
              sub="/ month"
            />
            <StatCard
              label="Typical"
              value={formatMoney(monthly.mid)}
              sub="/ month"
            />
            <StatCard
              label="High"
              value={formatMoney(monthly.high)}
              sub="/ month"
            />
          </div>

          {/* Bars */}
          <div className="space-y-3">
            <EarningsBar label="Low estimate"     value={monthly.low}  max={monthly.high} color="bg-slate-500" />
            <EarningsBar label="Typical estimate" value={monthly.mid}  max={monthly.high} color="bg-orange-400" />
            <EarningsBar label="High estimate"    value={monthly.high} max={monthly.high} color="bg-red-500" />
          </div>

          {/* Annual & RPM breakdown */}
          <div className="border-t border-slate-700/50 pt-4 grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-slate-500 text-xs uppercase tracking-widest mb-2">Annual Projection</p>
              <p className="text-white font-semibold">{formatMoney(annual.low)} – {formatMoney(annual.high)}</p>
              <p className="text-slate-500 text-xs mt-0.5">Typical: {formatMoney(annual.mid)}</p>
            </div>
            <div>
              <p className="text-slate-500 text-xs uppercase tracking-widest mb-2">Effective RPM</p>
              <p className="text-white font-semibold">${effectiveRPM.low} – ${effectiveRPM.high}</p>
              <p className="text-slate-500 text-xs mt-0.5">per 1,000 views</p>
            </div>
          </div>

          <p className="text-xs text-slate-600 text-center leading-relaxed">
            Estimates are based on publicly reported RPM ranges and vary with seasonality, ad-block rates, audience engagement, and YouTube's 45% revenue share. Results are for informational purposes only.
          </p>
        </div>
      </div>
    </div>
  )
}
