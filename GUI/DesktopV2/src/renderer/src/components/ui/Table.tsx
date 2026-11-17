import { For, Show, type JSX } from 'solid-js'

export interface Column<T> {
  key: string
  header: string
  /** Cell renderer. */
  cell: (row: T) => JSX.Element
  /** Extra class applied to every cell of the column. */
  cellClass?: string
  class?: string
}

export interface TableProps<T> {
  columns: Column<T>[]
  rows: T[]
  /** Key extractor used by Solid's `<For>`. */
  rowKey: (row: T) => string
  onRowClick?: (row: T) => void
  emptyMessage?: string
  class?: string
}

/**
 * Comparison table (9 columns, alternating rows, accent header border).
 */
export function ComparisonTable<T>(props: TableProps<T>) {
  return (
    <div class={['overflow-auto rounded-[6px] border border-border', props.class].join(' ')}>
      <table class="w-full border-collapse bg-surface text-left">
        <thead>
          <tr class="bg-header-bg">
            <For each={props.columns}>
              {(column) => (
                <th
                  scope="col"
                  class={[
                    'border-b-2 border-accent px-[10px] py-[10px] text-[12px] font-bold uppercase text-text-dim',
                    column.class,
                  ].join(' ')}
                >
                  {column.header}
                </th>
              )}
            </For>
          </tr>
        </thead>
        <tbody>
          <Show
            when={props.rows.length > 0}
            fallback={
              <tr>
                <td
                  class="px-[10px] py-3 text-center text-text-dim"
                  colspan={props.columns.length}
                >
                  {props.emptyMessage ?? ''}
                </td>
              </tr>
            }
          >
            <For each={props.rows}>
              {(row, index) => (
                <tr
                  class={[
                    'border-b border-border transition-colors',
                    index() % 2 === 1 ? 'bg-surface-panel' : 'bg-surface',
                    props.onRowClick ? 'cursor-pointer hover:bg-[#2f2f31]' : '',
                  ].join(' ')}
                  onClick={() => props.onRowClick?.(row)}
                >
                  <For each={props.columns}>
                    {(column) => (
                      <td class={['px-[5px] py-[5px] text-[#e0e0e0]', column.cellClass].join(' ')}>
                        {column.cell(row)}
                      </td>
                    )}
                  </For>
                </tr>
              )}
            </For>
          </Show>
        </tbody>
      </table>
    </div>
  )
}
