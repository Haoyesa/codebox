// Render a PDF file to one PNG per page using pdfjs-dist + Canvas.
// Pure JS, no native deps. Used by Tab1Export when the user wants an
// image format but the underlying file is .pptx/.doc (LO only produces
// PDF, we do the PNG conversion client-side).
//
// Input:  { pdfPath, scale }
// Output: [{ pageIndex, width, height, blob }]

import * as pdfjs from 'pdfjs-dist';
import workerSrc from 'pdfjs-dist/build/pdf.worker.min.mjs?url';

pdfjs.GlobalWorkerOptions.workerSrc = workerSrc;

export async function pdfToPngs({ pdfPath, pdfBytes, scale = 1 }) {
  // Accept bytes from the main process if they were already read
  // (avoids a re-read of the file and any race with LO).
  let bytes;
  if (pdfBytes && pdfBytes.length) {
    bytes = pdfBytes instanceof Uint8Array ? pdfBytes : new Uint8Array(pdfBytes);
  } else {
    const data = await window.electronAPI.readFile(pdfPath);
    bytes = new Uint8Array(data);
  }
  if (bytes.length === 0) {
    throw new Error(
      'PDF is 0 bytes at ' + pdfPath + '. LO probably wrote an empty file (silent failure). ' +
      '常见原因: 1) 上一次 LO 没退干净, user profile 被锁; ' +
      '2) 杀软拦截 LO 写文件; 3) 输入文件 LO 不识别. ' +
      'Try: 删 C:/Users/25147/AppData/Local/Temp/fulltool-lo-profile 后重试; ' +
      '右键该 PDF 看实际大小; 用 LO 手动 --convert-to pdf 同文件验证.'
    );
  }
  // pdfjs also wants a %PDF- header check. If those magic bytes are
  // missing the file is either empty or not a real PDF, and pdfjs will
  // throw InvalidPDFException with a less actionable message. Catch it
  // up front.
  const head = String.fromCharCode(bytes[0], bytes[1], bytes[2], bytes[3], bytes[4]);
  if (head !== '%PDF-') {
    throw new Error(
      'PDF header missing at ' + pdfPath + ' (got ' + JSON.stringify(head) + ', ' + bytes.length + ' bytes). ' +
      'File is not a real PDF. LO likely wrote garbage or the path is wrong.'
    );
  }

  const doc = await pdfjs.getDocument({ data: bytes }).promise;
  const out = [];
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i);
    const viewport = page.getViewport({ scale: Number(scale) || 1 });
    const canvas = document.createElement('canvas');
    canvas.width = Math.ceil(viewport.width);
    canvas.height = Math.ceil(viewport.height);
    const ctx = canvas.getContext('2d');
    // White background so transparent areas don't render as black in the PNG.
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    await page.render({ canvasContext: ctx, viewport }).promise;
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
    out.push({
      pageIndex: i,
      width: canvas.width,
      height: canvas.height,
      blob
    });
    // Release the page so memory doesn't pile up for big decks.
    page.cleanup();
  }
  await doc.cleanup();
  return out;
}
