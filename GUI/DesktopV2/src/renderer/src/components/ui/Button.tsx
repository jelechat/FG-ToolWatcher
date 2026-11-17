import { splitProps, type JSX, type ParentProps } from 'solid-js'

export type ButtonVariant = 'secondary' | 'primary' | 'danger' | 'info' | 'ghost' | 'warning'
export type ButtonSize = 'sm' | 'md' | 'lg'

export interface ButtonProps extends ParentProps {
  variant?: ButtonVariant
  size?: ButtonSize
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
  title?: string
  class?: string
  style?: JSX.CSSProperties
  onClick?: JSX.EventHandlerUnion<HTMLButtonElement, MouseEvent>
}

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  secondary:
    'bg-button-secondary-bg border border-border-light hover:bg-button-secondary-hover hover:border-accent text-text',
  primary: 'bg-accent hover:bg-accent-hover text-black',
  danger: 'bg-button-danger-bg hover:bg-error-dark text-text',
  info: 'bg-button-info-bg hover:bg-[#005a9e] text-text',
  ghost: 'bg-button-save-blue hover:bg-button-save-blue-hover text-text',
  warning: 'bg-button-warning-bg hover:bg-[#444444] text-text',
}

const SIZE_CLASS: Record<ButtonSize, string> = {
  sm: 'h-8 px-3 text-[13px]',
  md: 'h-10 px-4 text-[14px]',
  lg: 'h-[50px] px-6 text-[15px]',
}

/** Generic button matching the PySide6 `CustomPushButton` presets. */
export function Button(props: ButtonProps) {
  const [local] = splitProps(props, [
    'variant',
    'size',
    'disabled',
    'type',
    'title',
    'class',
    'style',
    'onClick',
    'children',
  ])

  return (
    <button
      type={local.type ?? 'button'}
      disabled={local.disabled}
      title={local.title}
      onClick={local.onClick}
      style={local.style}
      class={[
        'inline-flex items-center justify-center gap-2 rounded-[6px] font-semibold transition-colors',
        'disabled:bg-disabled-bg disabled:text-disabled-text disabled:border-none disabled:cursor-not-allowed',
        VARIANT_CLASS[local.variant ?? 'secondary'],
        SIZE_CLASS[local.size ?? 'md'],
        local.class,
      ].join(' ')}
    >
      {local.children}
    </button>
  )
}
