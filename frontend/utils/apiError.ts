/**
 * What to tell the reader when an API call fails, in their language.
 *
 * The API answers in English, and the pages used to show that sentence as it
 * came: a Chinese reader signing in with the wrong password read "Wrong email
 * or password", and one who was rate limited read "Something went wrong
 * loading this page" - nginx's 429 is an HTML page with no detail in it.
 *
 * Known sentences map to a key; the status decides the rest. An unknown
 * sentence is still shown as written - an English explanation beats a vague
 * translated one.
 */
const KNOWN: Record<string, string> = {
  'Wrong email or password': 'error.wrongPassword',
  'This account is suspended': 'error.suspended',
  'That code is not valid': 'error.badCode',
  'That email is already registered.': 'error.emailTaken',
  'That nickname is taken.': 'error.nicknameTaken',
  'That password is too long.': 'error.passwordTooLong',
  'Mix at least two of: lower case, upper case, digits, symbols.': 'error.passwordMix',
  'Do not build the password out of your nickname or email.': 'error.passwordPersonal',
  'Use letters, numbers, underscore, dot or hyphen only.': 'error.nicknameChars',
  'We could not send the email just now. Try again shortly.': 'error.emailDown',
  'Sign in to do that': 'error.signIn',
  'Post not found': 'error.postGone',
  'Answer not found': 'error.postGone',
  'Nothing to vote on': 'error.postGone',
  'Nothing to report': 'error.postGone',
  'The reply you are replying to is not in this thread': 'error.postGone',
  'Only its author can delete this': 'error.notYours',
  'Only the person who asked can mark an answer as helpful': 'error.notYours',
  'That vote is already counted': 'error.alreadyVoted',
  'That is not a unit code (for example FIT2004).': 'error.unitCode',
  'Write a real title and a question with some detail.': 'error.postTooShort',
  'Write a reply first.': 'error.replyEmpty',
  'The file is empty.': 'error.imageUnreadable',
  'That file is not an image we can read.': 'error.imageUnreadable',
  'That image is larger than 4MB.': 'error.imageTooLarge',
  'That image has too many pixels to process.': 'error.imageTooLarge',
  'We could not save that picture just now.': 'error.imageSave'
}

const LENGTH = /^Use at (least|most) (\d+) characters\.$/

type Translate = (key: string, params?: Record<string, string | number>) => string

export function apiErrorMessage(caught: any, t: Translate, fallbackKey = 'error.generic'): string {
  const status: number | undefined = caught?.status ?? caught?.statusCode ?? caught?.response?.status
  const detail = caught?.data?.detail

  if (status === 429) {
    const retry = Number(caught?.response?.headers?.get?.('retry-after'))
    return Number.isFinite(retry) && retry > 0
      ? t('error.tooManyWait', { minutes: Math.max(1, Math.ceil(retry / 60)) })
      : t('error.tooMany')
  }
  if (status === 413) return t('error.imageTooLarge')
  if (!status) return t('state.offline')
  if (status >= 500) return t('state.serverError')

  if (typeof detail === 'string') {
    if (KNOWN[detail]) return t(KNOWN[detail])
    const length = LENGTH.exec(detail)
    if (length) {
      return t(length[1] === 'least' ? 'error.tooShort' : 'error.tooLong', { n: length[2]! })
    }
    return detail
  }
  // FastAPI's own validation errors are a list; the form already says what
  // it expects, so a short sentence is enough.
  if (status === 422) return t('error.invalid')
  return t(fallbackKey)
}
