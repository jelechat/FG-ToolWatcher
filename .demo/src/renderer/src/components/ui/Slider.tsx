import { Slider } from '@kobalte/core/slider'
import { For } from 'solid-js'

export interface SliderProps {
  /** Index of the current value inside the `labels` array. */
  index: number
  onIndexChange: (index: number) => void
  /** Tick labels (one per step). */
  labels: string[]
  min?: number
  max?: number
}

/**
 * Range slider used for the cache duration.
 * The slider works on indexes (0..4) mapped to the [0, 1, 3, 7, 14] values.
 */
export function CacheSlider(props: SliderProps) {
  const min = () => props.min ?? 0
  const max = () => props.max ?? (props.labels.length - 1)

  return (
    <div class="flex w-full flex-col gap-2">
      <Slider
        value={[props.index]}
        onChange={(value) => props.onIndexChange(value[0] ?? min())}
        minValue={min()}
        maxValue={max()}
        step={1}
        class="w-full"
      >
        <Slider.Track class="relative h-[6px] w-full rounded-full bg-border">
          <Slider.Fill class="absolute h-full rounded-full bg-accent" />
          <Slider.Thumb class="block h-[18px] w-[18px] rounded-full border-[3px] border-black bg-accent transition-colors" />
        </Slider.Track>
      </Slider>
      <div class="flex w-full justify-between">
        <For each={props.labels}>
          {(label) => (
            <span class="text-small text-text-dim">{label}</span>
          )}
        </For>
      </div>
    </div>
  )
}
