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

export async function pdfToPngs({ pdfPath, scale = 1 }) {
  // Read the PDF bytes through main process (renderer can't fs.readFile).
  const data = await window.electronAPI.readFile(pdfPath);
  const bytes = new Uint8Array(data);

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
  await doc.destroy();
  return out;
}
