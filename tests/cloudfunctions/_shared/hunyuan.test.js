jest.mock('../../../cloudfunctions/_shared/config', () => ({
  HUNYUAN_MODE: 'mock',
  HUNYUAN_SECRET_ID: '',
  HUNYUAN_SECRET_KEY: '',
  HUNYUAN_REGION: 'ap-guangzhou',
}));

const { getHunyuan } = require('../../../cloudfunctions/_shared/hunyuan');

describe('HunyuanAdapter (mock)', () => {
  let adapter;
  beforeEach(() => { adapter = getHunyuan(); });

  test('parseResume returns structured data ignoring file content', async () => {
    const result = await adapter.parseResume({ fileBuffer: Buffer.from('xxx'), mimeType: 'application/pdf' });
    expect(result.data).toMatchObject({
      name: expect.any(String),
      phone: expect.any(String),
      education: expect.any(Array),
      work: expect.any(Array),
      projects: expect.any(Array),
      skills: expect.any(Array),
    });
  });

  test('optimizeResume returns optimized + score + suggestions', async () => {
    const result = await adapter.optimizeResume({
      structuredResume: { name: 'X', work: [], education: [] },
      identity: 'social', industry: 'internet', level: 'mid', job: 'frontend',
      promptTemplate: 'system: optimize {identity} {job}',
    });
    expect(result.optimized).toBeDefined();
    expect(result.score).toMatchObject({
      match: expect.any(Number), completeness: expect.any(Number),
      professional: expect.any(Number), quantified: expect.any(Number), total: expect.any(Number),
    });
    expect(Array.isArray(result.suggestions)).toBe(true);
  });

  test('mock has artificial latency between 700-2000ms', async () => {
    const t0 = Date.now();
    await adapter.parseResume({ fileBuffer: Buffer.from('x'), mimeType: 'application/pdf' });
    const dt = Date.now() - t0;
    expect(dt).toBeGreaterThanOrEqual(700);
    expect(dt).toBeLessThan(2000);
  });
});