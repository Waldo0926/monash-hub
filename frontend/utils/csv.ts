/**
 * CSV for spreadsheets people actually open in Excel.
 *
 * Every cell is quoted because Handbook titles contain commas. A cell that
 * starts with = + - or @ gets a leading apostrophe, otherwise Excel reads it
 * as a formula; nothing in a plan should start with one, but a unit title or
 * an imported plan is still text from somewhere else.
 */
export function csvCell(value: unknown): string {
  const text = String(value ?? '')
  const safe = /^[=+\-@]/.test(text) ? `'${text}` : text
  return `"${safe.replace(/"/g, '""')}"`
}

/** The BOM is what makes Excel open a UTF-8 file as UTF-8 rather than mojibake. */
export function toCsv(rows: unknown[][]): string {
  return '﻿' + rows.map((row) => row.map(csvCell).join(',')).join('\r\n')
}
