const { findTemplate } = require('../../../cloudfunctions/_shared/promptMatcher');

const TEMPLATES = [
  { type: 'optimize', identity: 'social', industry: 'internet', level: 'mid', version: 3, template: 'A' },
  { type: 'optimize', identity: 'social', industry: '*', level: '*', version: 1, template: 'B' },
  { type: 'optimize', identity: '*', industry: '*', level: '*', version: 0, template: 'C' },
  { type: 'parse', identity: '*', industry: '*', level: '*', version: 0, template: 'PARSE' },
];

describe('findTemplate', () => {
  test('exact match wins', () => {
    const t = findTemplate(TEMPLATES, { type: 'optimize', identity: 'social', industry: 'internet', level: 'mid' });
    expect(t.template).toBe('A');
  });

  test('falls back to identity wildcard', () => {
    const t = findTemplate(TEMPLATES, { type: 'optimize', identity: 'social', industry: 'finance', level: 'mid' });
    expect(t.template).toBe('B');
  });

  test('falls back to full wildcard', () => {
    const t = findTemplate(TEMPLATES, { type: 'optimize', identity: 'freshgrad', industry: 'finance', level: 'junior' });
    expect(t.template).toBe('C');
  });

  test('filters by type', () => {
    const t = findTemplate(TEMPLATES, { type: 'parse', identity: 'social', industry: 'internet', level: 'mid' });
    expect(t.template).toBe('PARSE');
  });

  test('returns null when nothing matches', () => {
    expect(findTemplate([], { type: 'optimize', identity: 'x', industry: 'y', level: 'z' })).toBeNull();
  });
});