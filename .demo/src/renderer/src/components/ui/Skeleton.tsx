import { For } from 'solid-js'

export interface SkeletonProps {
  rows?: number
  columns?: number
}

/** Placeholder rows displayed while the mock data is loading. */
export function TableSkeleton(props: SkeletonProps) {
  const rows = () => props.rows ?? 6
  const columns = () => props.columns ?? 9

  return (
    <div class="overflow-hidden rounded-[6px] border border-border">
      <div class="bg-header-bg px-[10px] py-[10px] text-[12px] font-bold uppercase text-text-dim">
        …
      </div>
      <For each={Array.from({ length: rows() })}>
        {(_, rowIndex) => (
          <div
            class={[
              'flex gap-2 px-[5px] py-[6px]',
              rowIndex() % 2 === 1 ? 'bg-surface-panel' : 'bg-surface',
            ].join(' ')}
          >
            <For each={Array.from({ length: columns() })}>
              {(_, columnIndex) => (
                <div
                  class="h-3 animate-pulse rounded-full bg-white/10"
                  style={{ width: `${60 + ((rowIndex() * 7 + columnIndex() * 13) % 40)}%` }}
                />
              )}
            </For>
          </div>
        )}
      </For>
    </div>
  )
}
