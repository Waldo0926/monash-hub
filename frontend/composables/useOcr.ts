/**
 * Reading marks off a screenshot, in the browser.
 *
 * The honest summary: this is the worst of the three ways to get results into
 * the calculator, and it exists because it is the one students will reach for.
 * Typing is exact. Pasting from WES is exact and takes two keystrokes. A
 * screenshot is neither, and OCR of a table loses column alignment often enough
 * that the results always land in the editable table for checking rather than
 * straight into a total.
 *
 * Three decisions worth keeping:
 *
 * **It loads on demand.** `tesseract.js` is the project's only runtime
 * dependency and it is imported dynamically inside the click handler, so a
 * student who never touches the button downloads none of it. The main bundle is
 * unchanged.
 *
 * **English only.** A WES results page is unit codes, numbers and grade letters
 * - `FIT1008 6 78 D`. Loading the Chinese model would multiply the download for
 * text that is not there.
 *
 * **The image never leaves the device.** Tesseract runs as WebAssembly in the
 * browser. A student's transcript is not uploaded anywhere, which is the same
 * promise the rest of the calculator makes and the reason this is not a server
 * endpoint calling a vision API.
 *
 * What does come off the network, once, on first use: the wasm core and the
 * English model, from the library's default CDN. Nothing happens until the
 * button is pressed, and a failure is reported rather than swallowed.
 */

export type OcrStage = 'idle' | 'loading' | 'recognising' | 'done' | 'error'

export function useOcr() {
  const stage = ref<OcrStage>('idle')
  /** 0-1, or null while the download progress is not yet known. */
  const progress = ref<number | null>(null)
  const error = ref('')

  /**
   * Read an image and return whatever text is on it.
   *
   * Returns an empty string rather than throwing: the caller shows `error` and
   * the student can still type the marks in, which is the fallback that always
   * works.
   */
  async function recognise(file: File): Promise<string> {
    if (!import.meta.client) return ''
    stage.value = 'loading'
    progress.value = null
    error.value = ''

    let worker: { recognize: (f: File) => Promise<any>; terminate: () => Promise<any> } | null =
      null
    try {
      const { createWorker } = await import('tesseract.js')
      worker = await createWorker('eng', 1, {
        logger: (message: { status?: string; progress?: number }) => {
          // The first run downloads the model, which is the slow part and the
          // one worth showing a bar for.
          if (typeof message.progress === 'number') progress.value = message.progress
          if (message.status === 'recognizing text') stage.value = 'recognising'
        }
      })
      const result = await worker.recognize(file)
      stage.value = 'done'
      return String(result?.data?.text ?? '')
    } catch (caught: any) {
      stage.value = 'error'
      error.value = caught?.message || 'OCR failed'
      return ''
    } finally {
      // The worker holds the wasm instance and the model; leaving it around
      // after a one-off read is tens of megabytes for nothing.
      try {
        await worker?.terminate()
      } catch {
        /* already gone */
      }
    }
  }

  function reset() {
    stage.value = 'idle'
    progress.value = null
    error.value = ''
  }

  return { recognise, reset, stage, progress, error }
}
