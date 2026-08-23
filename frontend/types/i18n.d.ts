// Makes $t known to the template type checker in every component.
declare module 'vue' {
  interface ComponentCustomProperties {
    $t: (key: string, params?: Record<string, string | number>) => string
  }
}

export {}
