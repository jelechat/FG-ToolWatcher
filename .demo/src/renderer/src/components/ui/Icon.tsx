import type { JSX } from 'solid-js'

const ICONS = import.meta.glob('../../assets/icons/*.svg', {
  eager: true,
  query: '?url',
  import: 'default',
}) as Record<string, string>

export type IconName =
  | 'settings'
  | 'synchronize'
  | 'documentation'
  | 'english'
  | 'french'
  | 'netherlands'
  | 'FG'
  | 'ToolWatcher'
  | 'quickadd'
  | 'refresh'
  | 'save'
  | 'mail'
  | 'analyze'
  | 'filter'
  | 'table'
  | 'graph'
  | 'switch'
  | 'bug'
  | 'github'
  | 'general'
  | 'websites'
  | 'profile'
  | 'system'
  | 'ai'

export interface IconProps {
  name: IconName
  /** Color variant: `white` for dark backgrounds, `black` for light ones. */
  color?: 'white' | 'black'
  /** Size in pixels. */
  size?: number
  class?: string
  title?: string
  style?: JSX.CSSProperties
}

/** Resolves the SVG url for a given icon name / color variant. */
export function resolveIcon(name: string, color: 'white' | 'black' = 'white'): string | undefined {
  const suffix = color === 'white' ? 'White' : 'Black'
  // Icons use either an underscore (settings_White.svg) or a dash (FG-White.svg).
  const candidates = [
    `../../assets/icons/${name}_${suffix}.svg`,
    `../../assets/icons/${name}-${suffix}.svg`,
    `../../assets/icons/${name}.svg`,
  ]
  for (const candidate of candidates) {
    const found = ICONS[candidate]
    if (found) return found
  }
  return undefined
}

/** Renders one of the 46 bundled SVG icons. */
export function Icon(props: IconProps) {
  const source = () => resolveIcon(props.name, props.color ?? 'white')
  return (
    <img
      src={source()}
      alt={props.title ?? props.name}
      title={props.title}
      aria-hidden={props.title ? undefined : 'true'}
      width={props.size ?? 20}
      height={props.size ?? 20}
      class={props.class}
      style={props.style}
      draggable={false}
    />
  )
}
