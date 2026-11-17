import { QueryClient, QueryClientProvider } from '@tanstack/solid-query'
import type { ParentProps } from 'solid-js'

/** Creates the shared query client (mock friendly: no network retry storms). */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        gcTime: 5 * 60_000,
        retry: false,
        refetchOnWindowFocus: false,
      },
    },
  })
}

export function QueryProvider(props: ParentProps) {
  const client = createQueryClient()
  return <QueryClientProvider client={client}>{props.children}</QueryClientProvider>
}
