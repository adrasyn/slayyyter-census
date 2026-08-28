/*
 * Fine accrual for the 2026 Australian Census.
 *
 * Failing to complete the Census when formally directed carries a penalty of
 * up to $364 per day. The clock here starts at midnight on Census night —
 * 11 August 2026 — anchored to AEST (UTC+10) rather than the visitor's local
 * timezone, so everyone looking at the page sees the same number.
 */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else Object.assign(root, api);
})(typeof self !== 'undefined' ? self : this, function () {

  const CENSUS_START = Date.parse('2026-08-11T00:00:00+10:00');
  const DAILY_RATE = 364;
  const MS_PER_DAY = 86400000;

  // Dollars owed at a given instant, accruing continuously rather than in
  // daily steps, so the counter visibly moves.
  function fineAt(now) {
    return elapsedDays(now) * DAILY_RATE;
  }

  // Whole days elapsed since Census night.
  function daysAt(now) {
    return Math.floor(elapsedDays(now));
  }

  function elapsedDays(now) {
    return Math.max(0, (now - CENSUS_START) / MS_PER_DAY);
  }

  const currency = new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
    currencyDisplay: 'narrowSymbol',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });

  function formatFine(amount) {
    return currency.format(amount);
  }

  return { CENSUS_START, DAILY_RATE, fineAt, daysAt, formatFine };
});
