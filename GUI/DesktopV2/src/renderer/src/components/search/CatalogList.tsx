import { For, Show } from 'solid-js'
import type { Product } from '@shared/domain'

export interface CatalogListProps {
  items: Product[]
  selected: string | null
  onSelect: (name: string) => void
  emptyMessage: string
}

/** List of the catalog items (bordered, selected item highlighted). */
export function CatalogList(props: CatalogListProps) {
  return (
    <div class="flex min-h-[220px] flex-1 flex-col overflow-hidden rounded-[10px] border-2 border-[#666666] bg-surface">
      <Show
        when={props.items.length > 0}
        fallback={<p class="p-6 text-center text-text-dim">{props.emptyMessage}</p>}
      >
        <ul class="flex-1 overflow-y-auto">
          <For each={props.items}>
            {(item) => (
              <li>
                <button
                  type="button"
                  onClick={() => props.onSelect(item.name)}
                  aria-selected={props.selected === item.name}
                  class={[
                    'flex w-full items-center justify-between gap-3 border-b border-border px-4 py-2 text-left text-[13px] transition-colors',
                    props.selected === item.name
                      ? 'bg-[#0078d7] font-semibold text-text'
                      : 'text-text hover:bg-white/5',
                  ].join(' ')}
                >
                  <span class="truncate">{item.name}</span>
                  <span class="shrink-0 text-text-dim">{item.brand}</span>
                </button>
              </li>
            )}
          </For>
        </ul>
      </Show>
    </div>
  )
}
