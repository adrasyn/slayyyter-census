// Verifies the fine accrual maths against known timestamps.
// Run: node test.js
const { CENSUS_START, DAILY_RATE, fineAt, daysAt, formatFine } = require('./fine.js');

let failures = 0;
function check(label, actual, expected) {
  const ok = actual === expected;
  if (!ok) failures++;
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}\n        expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
}

const day = 86400000;
const t = (iso) => Date.parse(iso);

// Census night is 11 August 2026, anchored to AEST (UTC+10) so the number
// is identical for every visitor regardless of their own timezone.
check('start anchors to 11 Aug 2026 midnight AEST',
  CENSUS_START, t('2026-08-10T14:00:00Z'));
check('daily rate is $364', DAILY_RATE, 364);

check('nothing owed at the instant census night begins',
  fineAt(CENSUS_START), 0);
check('nothing owed before census night',
  fineAt(CENSUS_START - day), 0);
check('one full day owes exactly the daily rate',
  fineAt(CENSUS_START + day), 364);
check('half a day owes half the rate',
  fineAt(CENSUS_START + day / 2), 182);
check('17 days owes 17x the rate',
  fineAt(CENSUS_START + 17 * day), 6188);

check('day count is 0 during census night itself',
  daysAt(CENSUS_START + day / 2), 0);
check('day count rolls to 1 after a full day',
  daysAt(CENSUS_START + day), 1);
check('day count floors partial days',
  daysAt(CENSUS_START + 17.9 * day), 17);
check('day count never goes negative',
  daysAt(CENSUS_START - 5 * day), 0);

check('formats as Australian currency with cents',
  formatFine(6419.153), '$6,419.15');
check('formats zero',
  formatFine(0), '$0.00');
check('formats thousands separators',
  formatFine(1234567.8), '$1,234,567.80');

console.log(failures === 0 ? '\nAll checks passed.' : `\n${failures} check(s) failed.`);
process.exit(failures === 0 ? 0 : 1);
