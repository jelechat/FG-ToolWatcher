export interface SpinnerProps {
  /** Radius of the imaginary circle (pixels). */
  radius?: number
  /** Diameter of a single dot (pixels). */
  dotSize?: number
  /** Rotation speed of a tick (milliseconds). */
  speed?: number
  color?: string
  class?: string
}

/**
 * 12 dots spinner, faithful to the original PySide6 `SpinnerProgressBar`.
 */
export function Spinner(props: SpinnerProps) {
  const radius = () => props.radius ?? 40
  const dotSize = () => props.dotSize ?? 10
  const color = () => props.color ?? '#007e2d'
  const size = () => (radius() + dotSize()) * 2

  return (
    <svg
      width={size()}
      height={size()}
      viewBox={`0 0 ${size()} ${size()}`}
      class={['animate-spin-slow', props.class].join(' ')}
      role="status"
      aria-label="loading"
    >
      <g transform={`translate(${size() / 2} ${size() / 2})`}>
        {Array.from({ length: 12 }).map((_, index) => {
          const alpha = Math.round((255 * (index + 1)) / 12)
          return (
            <circle
              cx={radius()}
              cy={0}
              r={dotSize() / 2}
              fill={color()}
              fill-opacity={alpha / 255}
              transform={`rotate(${index * 30})`}
            />
          )
        })}
      </g>
    </svg>
  )
}
