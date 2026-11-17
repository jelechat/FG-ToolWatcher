import Drawer from '@corvu/drawer'
import { Show, type ParentProps } from 'solid-js'

export interface DialogProps extends ParentProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title?: string
  description?: string
  /** Drawer side (the Quick Add dialog is centered, the filter drawer slides in). */
  side?: 'top' | 'bottom' | 'left' | 'right'
  /** When true the drawer is centered instead of sliding from a side. */
  centered?: boolean
  /** Called when the user clicks on the overlay (outside of the content). */
  onOverlayClick?: () => void
  class?: string
}

/**
 * Modal wrapper based on @corvu/drawer.
 *
 * Z-index layers: overlay 70, content 80. Kobalte poppers (select listboxes)
 * live in a portal attached to <body> with a z-index of 120 so that they are
 * painted above the modal and remain clickable.
 *
 * The corvu drawer dismisses itself on any pointer event happening outside of
 * its content element. A Kobalte listbox is rendered outside of that subtree,
 * so selecting an option would close the dialog before the value is applied:
 * the outside-pointer/outside-focus dismissal is therefore disabled and the
 * overlay handles the "click outside to close" behaviour instead.
 *
 * `Esc` still closes the dialog (handled by corvu).
 */
export function Dialog(props: DialogProps) {
  return (
    <Drawer
      open={props.open}
      onOpenChange={props.onOpenChange}
      side={props.side ?? 'bottom'}
      snapPoints={[0, 1]}
      defaultSnapPoint={1}
      closeOnOutsidePointer={false}
      closeOnOutsideFocus={false}
    >
      <Drawer.Portal>
        <Drawer.Overlay
          class="fixed inset-0 z-[70] bg-black/60"
          onClick={() => props.onOverlayClick?.()}
        />
        <Drawer.Content
          class={[
            'z-[80] rounded-[10px] border border-border bg-surface p-5 shadow-md',
            props.centered
              ? 'fixed left-1/2 top-1/2 w-[420px] max-w-[92vw] -translate-x-1/2 -translate-y-1/2'
              : 'fixed right-0 top-0 h-full w-[360px] max-w-[90vw] rounded-l-[10px] rounded-r-none pb-[70px]',
            props.class,
          ].join(' ')}
        >
          <Show when={props.title}>
            <Drawer.Label class="mb-1 font-montserrat-black text-[20px] text-text">
              {props.title}
            </Drawer.Label>
          </Show>
          <Show when={props.description}>
            <Drawer.Description class="mb-3 text-[13px] text-text-dim">
              {props.description}
            </Drawer.Description>
          </Show>
          {props.children}
        </Drawer.Content>
      </Drawer.Portal>
    </Drawer>
  )
}
