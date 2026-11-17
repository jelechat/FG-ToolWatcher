import { For } from 'solid-js'
import { ScrollArea } from '../ui/ScrollArea'

export interface BrandQuickAccessProps {
  brands: string[]
  onSelect: (brand: string) => void
  label: string
}

/** Right rail listing the brands (scrollable). */
export function BrandQuickAccess(props: BrandQuickAccessProps) {
  return (
    <aside class="flex w-[180px] shrink-0 flex-col gap-2">
      <span class="font-montserrat-semibold text-label text-text-dim">{props.label}</span>
      <ScrollArea class="max-h-[520px] rounded-[10px] border border-border bg-surface p-2">
        <ul class="flex flex-col gap-1">
          <For each={props.brands}>
            {(brand) => (
              <li>
                <button
                  type="button"
                  onClick={() => props.onSelect(brand)}
                  class="w-full rounded-[6px] px-2 py-1 text-left text-[13px] text-text transition-colors hover:bg-white/10"
                >
                  {brand}
                </button>
              </li>
            )}
          </For>
        </ul>
      </ScrollArea>
    </aside>
  )
}
