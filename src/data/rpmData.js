// RPM (Revenue Per Mille) estimates in USD — US audience baseline
// Ranges represent typical low / mid / high for the niche
export const niches = [
  { id: 'finance',       label: 'Finance & Investing',          icon: '💰', rpm: { low: 8,   mid: 12,  high: 18  } },
  { id: 'business',      label: 'Business & Entrepreneurship',  icon: '📈', rpm: { low: 6,   mid: 9,   high: 14  } },
  { id: 'technology',    label: 'Technology',                   icon: '💻', rpm: { low: 4,   mid: 6,   high: 10  } },
  { id: 'health',        label: 'Health & Fitness',             icon: '🏋️', rpm: { low: 3,   mid: 5,   high: 8   } },
  { id: 'education',     label: 'Education',                    icon: '📚', rpm: { low: 3,   mid: 5,   high: 8   } },
  { id: 'gaming',        label: 'Gaming',                       icon: '🎮', rpm: { low: 1.5, mid: 2.5, high: 4.5 } },
  { id: 'lifestyle',     label: 'Lifestyle & Vlogging',         icon: '✨', rpm: { low: 2,   mid: 3.5, high: 6   } },
  { id: 'food',          label: 'Food & Cooking',               icon: '🍳', rpm: { low: 2,   mid: 3.5, high: 5.5 } },
  { id: 'travel',        label: 'Travel',                       icon: '✈️', rpm: { low: 2,   mid: 3.5, high: 6   } },
  { id: 'beauty',        label: 'Beauty & Fashion',             icon: '💄', rpm: { low: 2,   mid: 3.5, high: 5.5 } },
  { id: 'sports',        label: 'Sports',                       icon: '⚽', rpm: { low: 1.5, mid: 2.5, high: 4   } },
  { id: 'entertainment', label: 'Entertainment',                icon: '🎬', rpm: { low: 1,   mid: 2,   high: 3.5 } },
]

// Multiplier relative to a US-based audience
export const countries = [
  { code: 'US', label: 'United States',   flag: '🇺🇸', multiplier: 1.00 },
  { code: 'UK', label: 'United Kingdom',  flag: '🇬🇧', multiplier: 0.72 },
  { code: 'CA', label: 'Canada',          flag: '🇨🇦', multiplier: 0.65 },
  { code: 'AU', label: 'Australia',       flag: '🇦🇺', multiplier: 0.65 },
  { code: 'DE', label: 'Germany',         flag: '🇩🇪', multiplier: 0.58 },
  { code: 'CH', label: 'Switzerland',     flag: '🇨🇭', multiplier: 0.62 },
  { code: 'NO', label: 'Norway',          flag: '🇳🇴', multiplier: 0.58 },
  { code: 'NL', label: 'Netherlands',     flag: '🇳🇱', multiplier: 0.52 },
  { code: 'SE', label: 'Sweden',          flag: '🇸🇪', multiplier: 0.52 },
  { code: 'FR', label: 'France',          flag: '🇫🇷', multiplier: 0.48 },
  { code: 'ES', label: 'Spain',           flag: '🇪🇸', multiplier: 0.38 },
  { code: 'IT', label: 'Italy',           flag: '🇮🇹', multiplier: 0.38 },
  { code: 'JP', label: 'Japan',           flag: '🇯🇵', multiplier: 0.42 },
  { code: 'KR', label: 'South Korea',     flag: '🇰🇷', multiplier: 0.38 },
  { code: 'BR', label: 'Brazil',          flag: '🇧🇷', multiplier: 0.15 },
  { code: 'MX', label: 'Mexico',          flag: '🇲🇽', multiplier: 0.15 },
  { code: 'IN', label: 'India',           flag: '🇮🇳', multiplier: 0.12 },
  { code: 'ID', label: 'Indonesia',       flag: '🇮🇩', multiplier: 0.10 },
  { code: 'PH', label: 'Philippines',     flag: '🇵🇭', multiplier: 0.10 },
  { code: 'VN', label: 'Vietnam',         flag: '🇻🇳', multiplier: 0.08 },
  { code: 'PK', label: 'Pakistan',        flag: '🇵🇰', multiplier: 0.07 },
  { code: 'BD', label: 'Bangladesh',      flag: '🇧🇩', multiplier: 0.07 },
]

export function calcEarnings(views, rpm, multiplier) {
  const thousands = views / 1000
  return {
    low:  +(thousands * rpm.low  * multiplier).toFixed(2),
    mid:  +(thousands * rpm.mid  * multiplier).toFixed(2),
    high: +(thousands * rpm.high * multiplier).toFixed(2),
  }
}

// Logarithmic slider helpers — slider 0‥100 → 1 000 ‥ 50 000 000 views
const LOG_MIN = Math.log10(1_000)
const LOG_MAX = Math.log10(50_000_000)

export function sliderToViews(pos) {
  return Math.round(10 ** (LOG_MIN + (pos / 100) * (LOG_MAX - LOG_MIN)))
}

export function viewsToSlider(views) {
  const clamped = Math.max(1_000, Math.min(50_000_000, views))
  return Math.round(((Math.log10(clamped) - LOG_MIN) / (LOG_MAX - LOG_MIN)) * 100)
}

export function formatViews(n) {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M'
  if (n >= 1_000)     return (n / 1_000).toFixed(0) + 'K'
  return String(n)
}

export function formatMoney(n) {
  if (n >= 1_000_000) return '$' + (n / 1_000_000).toFixed(2) + 'M'
  if (n >= 1_000)     return '$' + (n / 1_000).toFixed(1) + 'K'
  return '$' + n.toFixed(2)
}
