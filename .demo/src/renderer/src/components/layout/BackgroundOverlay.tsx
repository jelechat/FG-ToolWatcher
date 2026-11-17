export interface BackgroundOverlayProps {
  class?: string
}

/**
 * Application background.
 * The original GUI used `FGbackground8.jpg` (missing from the repository):
 * a CSS gradient reproduces the same dark atmosphere.
 */
export function BackgroundOverlay(props: BackgroundOverlayProps) {
  return (
    <div
      aria-hidden="true"
      class={['pointer-events-none absolute inset-0 z-0', props.class].join(' ')}
      style={{
        'background-image':
          'radial-gradient(circle at 20% 15%, rgba(0,145,62,0.18), transparent 45%), radial-gradient(circle at 85% 80%, rgba(255,255,255,0.06), transparent 40%), linear-gradient(160deg, #242424 0%, #1e1e1e 55%, #161616 100%)',
      }}
    />
  )
}
