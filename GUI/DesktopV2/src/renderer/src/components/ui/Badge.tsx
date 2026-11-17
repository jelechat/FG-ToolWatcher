import type { ParentProps } from 'solid-js'

export type BadgeTone = 'neutral' | 'success' | 'warning' | 'danger' | 'soon'

export interface BadgeProps extends ParentProps {
  tone?: BadgeTone
  class?: string
}

const TONE_CLASS: Record<BadgeTone, string> = {
  neutral: 'bg-white/10 text-text-dim border-white/20',
  success: 'bg-[rgba(0,126,45,0.85)] text-text border-accent',
  warning: 'bg-[rgba(255,170,0,0.2)] text-[#ffaa00] border-[#ffaa00]/40',
  danger: 'bg-[rgba(204,0,0,0.25)] text-error border-error/40',
  soon: 'bg-white/10 text-text-dim border-white/20',
}

/** Small status badge (disabled website, "soon" features, ...). */
export function Badge(props: BadgeProps) {
  return (
    <span
      class={[
        'inline-flex items-center rounded-[10px] border px-2 py-[2px] text-[11px] font-semibold uppercase',
        TONE_CLASS[props.tone ?? 'neutral'],
        props.class,
      ].join(' ')}
    >
      {props.children}
    </span>
  )
}
