/**
 * System Health Plugin for Hermes Desktop
 *
 * Adds a "System Health" pane showing live CPU/RAM/Disk usage,
 * wiki stats, Hermes token usage, models, skills, and gateway status.
 *
 * ═════════════════════════════════════════════════════════════════════════
 * J2B WSP — Web Solutions & Projects
 * https://j2b.live  |  hermes@j2b.live
 * "L'élégance n'est pas une option, c'est une signature."
 * ═════════════════════════════════════════════════════════════════════════
 *
 * License: MIT
 * Repository: https://github.com/jbtvstreaming-ai/Agent-Hermes
 *
 * Installation:
 *   mkdir -p ~/.hermes/desktop-plugins/system-health
 *   cp plugin.js ~/.hermes/desktop-plugins/system-health/
 *   Then ⌘K → "Reload desktop plugins"
 *
 * NOTE: This is a TEMPLATE — the __HEALTH_DATA__ block is populated at
 * runtime by collector.py. Do NOT commit an injected copy to the repo.
 */

// ═══════════════════════════════════════════════════════════════════════
//  DATA INJECTION POINT — populated by collector.py (do not edit)
// ═══════════════════════════════════════════════════════════════════════
// __INJECTED_DATA_START__
const __HEALTH_DATA__ = null;
// __INJECTED_DATA_END__
// ═══════════════════════════════════════════════════════════════════════

import { Badge, cn, Codicon, haptic, host, StatusDot, useValue } from '@hermes/plugin-sdk'
import { jsx, jsxs } from 'react/jsx-runtime'
import { useState, useEffect, useCallback } from 'react'

const ID = 'system-health'
const REFRESH_MS = 15_000

// ── Color helpers ─────────────────────────────────────────────────────
function colorFor(pct) {
  if (pct > 80) return 'var(--ui-error)'
  if (pct > 60) return 'var(--ui-warning)'
  return 'var(--ui-accent)'
}

// ── Gauge component ───────────────────────────────────────────────────
function Gauge({ label, value, sub }) {
  const pct = Math.min(Math.max(value ?? 0, 0), 100)
  const hue = colorFor(pct)
  return jsxs('div', {
    className: 'flex flex-col gap-0.5',
    children: [
      jsxs('div', {
        className: 'flex items-center justify-between text-xs',
        children: [
          jsx('span', { className: 'text-(--ui-text-secondary)', children: label }),
          jsxs('span', {
            className: 'font-semibold tabular-nums text-xs',
            style: { color: hue },
            children: [String(pct), '%']
          })
        ]
      }),
      jsx('div', {
        className: 'h-1.5 w-full overflow-hidden rounded-full bg-(--ui-stroke-secondary)',
        children: jsx('div', {
          className: 'h-full rounded-full transition-all duration-700 ease-out',
          style: { width: `${pct}%`, backgroundColor: hue }
        })
      }),
      sub ? jsx('span', {
        className: 'text-(--ui-text-quaternary) text-[0.65rem]',
        children: sub
      }) : null
    ]
  })
}

// ── Stat row ──────────────────────────────────────────────────────────
function Stat({ label, value, icon }) {
  return jsxs('div', {
    className: 'flex items-center justify-between py-0.5 text-xs',
    children: [
      jsxs('span', {
        className: 'flex items-center gap-1 text-(--ui-text-secondary)',
        children: [
          icon ? jsx(Codicon, { name: icon, className: 'text-(--ui-text-quaternary) text-[0.75rem]' }) : null,
          label
        ]
      }),
      jsx('span', { className: 'font-medium tabular-nums', children: value ?? '—' })
    ]
  })
}

// ── Section wrapper ───────────────────────────────────────────────────
function Section({ title, icon, children }) {
  return jsxs('div', {
    className: 'space-y-2',
    children: [
      jsxs('div', {
        className: 'flex items-center gap-1.5 border-b border-(--ui-stroke-secondary) pb-1 text-[0.65rem] font-semibold uppercase tracking-wider text-(--ui-text-tertiary)',
        children: [
          icon ? jsx(Codicon, { name: icon, className: 'text-(--ui-text-quaternary) text-[0.7rem]' }) : null,
          title
        ]
      }),
      children
    ]
  })
}

// ── Main pane ─────────────────────────────────────────────────────────
function HealthPane() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const gateway = useValue(host.state.gateway)

  const fetchData = useCallback(async () => {
    // Try 1: Use injected static data (fastest, no CSP)
    if (typeof __HEALTH_DATA__ !== 'undefined' && __HEALTH_DATA__?.system) {
      setData(__HEALTH_DATA__)
      setLoading(false)
      return
    }

    // Try 2: No fallback — injected data is the primary path.
    // Override this function in your local copy for alternative sources.
    setLoading(false)
  }, [])

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, REFRESH_MS)
    return () => clearInterval(interval)
  }, [fetchData])

  if (loading && !data) {
    return jsx('div', {
      className: 'flex h-full flex-col items-center justify-center gap-2 p-4 text-center',
      children: [
        jsx(Codicon, { name: 'dashboard', className: 'text-2xl text-(--ui-text-quaternary)' }),
        jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: 'Collecting data...' }),
        jsx('div', { className: 'text-[0.65rem] text-(--ui-text-quaternary)', children: 'Run collector.py to populate data' }),
      ]
    })
  }

  if (!data) {
    return jsxs('div', {
      className: 'flex h-full flex-col items-center justify-center gap-2 p-4 text-center',
      children: [
        jsx(Codicon, { name: 'warning', className: 'text-xl text-(--ui-warning)' }),
        jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: 'No data available' }),
        jsx('div', { className: 'text-[0.65rem] text-(--ui-text-quaternary)', children: 'Run: python collector/collector.py' }),
      ]
    })
  }

  const sys = data?.system
  const wiki = data?.wiki
  const ins = data?.hermes?.insights
  const skills = data?.hermes?.skills

  return jsxs('div', {
    className: 'flex h-full flex-col gap-4 overflow-auto p-3 text-xs',
    children: [
      jsx(Section, {
        title: 'System Resources',
        icon: 'vm',
        children: jsxs('div', {
          className: 'space-y-2.5 pt-0.5',
          children: [
            jsx(Gauge, { label: 'CPU', value: sys?.cpu }),
            jsx(Gauge, { label: 'RAM', value: sys?.ram?.percent, sub: sys?.ram ? `${sys.ram.used_gb} / ${sys.ram.total_gb} GB` : null }),
            jsx(Gauge, { label: 'Disk (C:)', value: sys?.disk?.percent, sub: sys?.disk ? `${sys.disk.used_gb} / ${sys.disk.total_gb} GB` : null }),
          ]
        }),
      }),
      jsx(Section, {
        title: 'Tokens (30 days)',
        icon: 'pulse',
        children: jsxs('div', {
          className: 'space-y-1 pt-0.5',
          children: [
            jsx(Stat, { label: 'Input', value: ins?.input_tokens ? `${(ins.input_tokens / 1000).toFixed(0)}K` : '—' }),
            jsx(Stat, { label: 'Output', value: ins?.output_tokens ? `${(ins.output_tokens / 1000).toFixed(0)}K` : '—' }),
            ins?.total_tokens ? jsx(Stat, { label: 'Total', value: ins.total_tokens >= 1_000_000 ? `${(ins.total_tokens / 1_000_000).toFixed(1)}M` : `${(ins.total_tokens / 1000).toFixed(0)}K` }) : null,
            jsx(Stat, { label: 'Sessions', value: ins?.sessions ?? '—' }),
            jsx(Stat, { label: 'Messages', value: ins?.messages ?? '—' }),
            jsx(Stat, { label: 'Tool calls', value: ins?.tool_calls ?? '—' }),
          ]
        }),
      }),
      ins?.models?.length ? jsx(Section, {
        title: 'Models Used',
        icon: 'robot',
        children: jsx('div', { className: 'space-y-1 pt-0.5', children: ins.models.map((m, i) => jsx(Stat, { label: m.name, value: `${m.sessions} session(s)` }, i)) })
      }) : null,
      skills ? jsx(Section, {
        title: 'Skills',
        icon: 'extensions',
        children: jsxs('div', { className: 'space-y-1 pt-0.5', children: [jsx(Stat, { label: 'Installed', value: skills.total ?? '—' }), jsx(Stat, { label: 'Enabled', value: skills.enabled ?? '—' })] })
      }) : null,
      ins?.tools?.length ? jsx(Section, {
        title: 'Top Tools',
        icon: 'tools',
        children: jsx('div', { className: 'space-y-1 pt-0.5', children: ins.tools.slice(0, 6).map((t, i) => jsx(Stat, { label: t.name, value: `${t.calls} calls` }, i)) })
      }) : null,
      jsx(Section, {
        title: 'LLM Wiki',
        icon: 'book',
        children: jsxs('div', { className: 'space-y-0.5 pt-0.5', children: [
          jsx(Stat, { label: 'Status', value: jsx(StatusDot, { status: wiki?.exists ? 'available' : 'unavailable', children: wiki?.exists ? 'Enabled' : 'Not found' }) }),
          jsx(Stat, { label: 'Wiki Pages', value: wiki?.total_wiki_pages ?? 0 }),
          jsx(Stat, { label: 'Entities', value: wiki?.entities ?? 0 }),
          jsx(Stat, { label: 'Concepts', value: wiki?.concepts ?? 0 }),
          jsx(Stat, { label: 'Files', value: wiki?.total_files ?? 0 }),
          wiki?.last_updated ? jsx(Stat, { label: 'Updated', value: wiki.last_updated }) : null,
        ]})
      }),
      jsx(Section, {
        title: 'Hermes',
        icon: 'dashboard',
        children: jsxs('div', { className: 'space-y-0.5 pt-0.5', children: [
          jsx(Stat, { label: 'Gateway', value: jsx(StatusDot, { status: 'available', children: 'Running' }) }),
          jsx(Stat, { label: 'Refresh', value: `${REFRESH_MS / 1000}s` }),
          data?._injected_at ? jsx(Stat, { label: 'Updated', value: data._injected_at }) : null,
        ]})
      }),
      jsx('div', { className: 'mt-auto text-center text-[0.6rem] text-(--ui-text-quaternary)', children: 'System Health v1.0 — J2B WSP' })
    ]
  })
}

// ── Plugin export ──────────────────────────────────────────────────────
export default {
  id: ID,
  name: 'System Health',
  defaultEnabled: true,
  register(ctx) {
    ctx.register({
      id: 'pane',
      area: 'panes',
      title: 'System Health',
      data: { placement: 'right', width: '260px', minWidth: '200px' },
      render: () => jsx(HealthPane, {}),
    })
    ctx.register({
      id: 'chip',
      area: 'statusBar.right',
      order: 120,
      render: () => {
        return jsx('button', {
          className: cn('inline-flex h-full items-center gap-1 px-1.5 text-[0.65rem] transition-colors', 'text-(--ui-text-tertiary) hover:bg-(--chrome-action-hover) hover:text-foreground'),
          type: 'button',
          onClick: () => { haptic('tap'); host.notify({ kind: 'info', message: 'System Health pane added (right side)' }) },
          children: jsxs('span', { className: 'flex items-center gap-1', children: [jsx(StatusDot, { status: 'available', className: 'text-[0.45rem]' }), 'Health'] })
        })
      }
    })
  }
}
