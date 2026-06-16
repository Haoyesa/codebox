// @created 2026-06-16 v0.1 - 调混元解析简历为结构化 JSON
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');
const { getHunyuan, HunyuanError } = require('../_shared/hunyuan');

exports.main = async (event, context) => {
  try {
    const { fileID } = event;
    if (!fileID) return fail('BAD_REQUEST', 'fileID 必填');

    // 1. 从云存储下载文件
    const dl = await cloud.downloadFile({ fileID });
    const fileBuffer = dl.fileContent;

    // 2. 推断 mime(简化版:按扩展名)
    const mimeType = fileID.endsWith('.pdf') ? 'application/pdf'
      : fileID.endsWith('.docx') ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      : fileID.endsWith('.doc') ? 'application/msword'
      : 'image/jpeg';

    // 3. 调混元
    const adapter = getHunyuan();
    const result = await adapter.parseResume({ fileBuffer, mimeType, filename: fileID });

    return ok({ data: result.data });
  } catch (err) {
    console.error('[parseResume]', err);
    if (err instanceof HunyuanError) return fail('PARSE_FAIL', err.message);
    return fail('INTERNAL', err.message);
  }
};