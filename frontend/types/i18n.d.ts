// Makes $t and $term known to the template type checker in every component.
import type { TermKind } from '~/i18n/handbook-terms'

declare module 'vue' {
  interface ComponentCustomProperties {
    $t: (key: string, params?: Record<string, string | number>) => string
    $term: (kind: TermKind, value: string | null | undefined) => string | null
    $assessmentName: (value: string | null | undefined) => string | null
  }
}

export {}
