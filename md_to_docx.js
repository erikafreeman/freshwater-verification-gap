// Convert freshwater_prediction_v23.md → freshwater_prediction_v23.docx
// Usage: node md_to_docx.js [input.md] [output.docx]

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, PageBreak,
  AlignmentType, LevelFormat, LineNumberRestartFormat,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  ImageRun, Header, Footer, PageNumber,
} = require('docx');

// Positional args, with optional --linenums flag anywhere in argv
const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const flags = process.argv.slice(2).filter(a => a.startsWith('--'));
const inputPath = args[0] || 'freshwater_prediction_v23.md';
const outputPath = args[1] || 'freshwater_prediction_v23.docx';
const wantLineNumbers = flags.includes('--linenums');

const raw = fs.readFileSync(inputPath, 'utf8');
const lines = raw.split(/\r?\n/);

// --- inline parser: handles **bold**, *italic*, backticks `code` ---
function parseInline(text) {
  // Unescape \[ \] \# etc.
  text = text.replace(/\\([\[\]#*_`])/g, '$1');

  const runs = [];
  let i = 0;
  let buf = '';
  let bold = false;
  let italic = false;

  const flush = () => {
    if (buf) {
      runs.push(new TextRun({ text: buf, bold, italics: italic }));
      buf = '';
    }
  };

  while (i < text.length) {
    // Bold ** (check first so ** isn't mistaken for two *)
    if (text[i] === '*' && text[i + 1] === '*') {
      flush();
      bold = !bold;
      i += 2;
      continue;
    }
    // Italic *
    if (text[i] === '*') {
      flush();
      italic = !italic;
      i += 1;
      continue;
    }
    buf += text[i];
    i++;
  }
  flush();
  if (runs.length === 0) runs.push(new TextRun({ text: '' }));
  return runs;
}

// --- strip enclosing ** from a heading line like "# **Abstract**" ---
function stripOuterBold(text) {
  const m = text.match(/^\*\*(.+)\*\*$/);
  return m ? m[1] : text;
}

// --- table helpers ---
function isTableRow(line) {
  return /^\|.*\|\s*$/.test(line);
}
function isTableSeparator(line) {
  return /^\|\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|\s*$/.test(line);
}
function parseTableRow(line) {
  // Split on | but drop the leading/trailing empty fields
  const cells = line.replace(/^\|/, '').replace(/\|\s*$/, '').split('|');
  return cells.map(c => c.trim());
}
function buildTable(rowLines) {
  // rowLines: [header, separator, ...body]
  const header = parseTableRow(rowLines[0]);
  const body = rowLines.slice(2).map(parseTableRow);
  const nCols = header.length;

  const headerFill = 'E5E7EB'; // light grey
  const cellBorder = { style: BorderStyle.SINGLE, size: 4, color: '9CA3AF' };

  // Compute proportional column widths from content length. Page text area
  // is ~9360 twips (US Letter 8.5" minus two 1" margins ≈ 6.5"). We give each
  // column a share proportional to its max cell character length, with a
  // floor so no column collapses and a mild damping so one very long column
  // doesn't starve the others.
  // For wide tables (many columns) the floor is reduced to avoid overflow.
  // Content width after 1" L/R margins:
  //   portrait  US Letter: 8.5" − 2" = 6.5" = 9360 twips
  //   landscape US Letter: 11"  − 2" = 9"   = 12960 twips
  // (The previous 14400 figure was the full page width, not content area,
  //  and caused tables to overflow the right margin by 1 inch.)
  const PAGE_TWIPS = flags.includes('--landscape') ? 12960 : 9360;
  const FLOOR = nCols >= 7 ? 350 : (nCols >= 6 ? 600 : (nCols >= 5 ? 900 : 1200));
  const DAMPING = 0.55;  // sub-linear scaling; lower = flatter distribution
  // Measure column content length after stripping markdown link syntax so that
  // long URLs don't dominate the width calculation.
  function strip(s) {
    return (s || '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // [text](url) -> text
      .replace(/\*+/g, '');
  }
  const maxLens = Array(nCols).fill(0);
  const allRows = [header, ...body];
  for (const row of allRows) {
    for (let c = 0; c < nCols; c++) {
      const text = strip(row[c] ?? '');
      if (text.length > maxLens[c]) maxLens[c] = text.length;
    }
  }
  const damped = maxLens.map(l => Math.pow(Math.max(l, 3), DAMPING));
  const dampedSum = damped.reduce((a, b) => a + b, 0);
  let widths = damped.map(d => Math.max(FLOOR, Math.round((d / dampedSum) * PAGE_TWIPS)));
  const wSum = widths.reduce((a, b) => a + b, 0);
  widths = widths.map(w => Math.round(w * PAGE_TWIPS / wSum));

  // Build cell runs directly from raw markdown text (parseInline returns docx
  // TextRun objects whose `.text` is internal; safer to re-tokenise here for
  // the small set of inline styles that tables actually use).
  function cellRuns(text, forceBold) {
    text = text.replace(/\\([\[\]#*_`|])/g, '$1');
    // Collapse markdown links [text](url) to just "text" — keeps cells narrow.
    text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
    const runs = [];
    let i = 0, buf = '', bold = false, italic = false;
    const flush = () => {
      if (buf.length) {
        runs.push(new TextRun({ text: buf, bold: forceBold || bold, italics: italic }));
        buf = '';
      }
    };
    while (i < text.length) {
      if (text[i] === '*' && text[i + 1] === '*') { flush(); bold = !bold; i += 2; continue; }
      if (text[i] === '*') { flush(); italic = !italic; i += 1; continue; }
      buf += text[i]; i++;
    }
    flush();
    if (runs.length === 0) runs.push(new TextRun({ text: '', bold: forceBold }));
    return runs;
  }

  // Use smaller text in wide tables so they fit the page width.
  // Half-point units: 22=11pt, 20=10pt, 18=9pt, 16=8pt, 14=7pt, 12=6pt.
  // Landscape gives more width so we can keep larger text.
  const isLandscape = flags.includes('--landscape');
  const cellFontSize = isLandscape
    ? (nCols >= 7 ? 18 : (nCols >= 5 ? 20 : 22))
    : (nCols >= 7 ? 12 : (nCols >= 5 ? 16 : 22));
  const headerFontSize = cellFontSize;

  function cellRunsSized(text, forceBold, size) {
    const runs = cellRuns(text, forceBold);
    return runs.map(r => new TextRun({
      text: r.options ? r.options.text : text,
      bold: forceBold,
      size,
    }));
  }

  const makeCell = (text, isHeader, colIdx) => new TableCell({
    children: [new Paragraph({
      children: cellRunsSized(text, isHeader, isHeader ? headerFontSize : cellFontSize),
      spacing: { before: 40, after: 40 },
    })],
    shading: isHeader ? { type: ShadingType.SOLID, fill: headerFill, color: 'auto' } : undefined,
    margins: nCols >= 7
      ? { top: 40, bottom: 40, left: 60, right: 60 }
      : { top: 80, bottom: 80, left: 100, right: 100 },
    width: { size: widths[colIdx], type: WidthType.DXA },
  });

  const headerRow = new TableRow({
    tableHeader: true,
    children: header.map((c, i) => makeCell(c, true, i)),
  });
  const bodyRows = body.map(row => new TableRow({
    children: Array.from({ length: nCols }, (_, i) => makeCell(row[i] ?? '', false, i)),
  }));

  return new Table({
    rows: [headerRow, ...bodyRows],
    width: { size: PAGE_TWIPS, type: WidthType.DXA },
    columnWidths: widths,
    borders: {
      top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder,
      insideHorizontal: cellBorder, insideVertical: cellBorder,
    },
  });
}

// --- main pass: build paragraphs and tables ---
// We collect all content into `paragraphs`, but also track orientation
// markers (<!-- landscape-start --> / <!-- landscape-end -->) as split
// points so we can produce multiple sections with different page sizes.
const paragraphs = [];
const orientationBreaks = []; // [{ atIndex, orientation }]

for (let i = 0; i < lines.length; i++) {
  const raw = lines[i];
  const line = raw.replace(/\s+$/, ''); // rtrim

  if (line === '') continue; // blank line: paragraph separator

  // Orientation markers — switch page orientation for the following content.
  // Emits a split point; paragraphs before the split form one section, those
  // after form the next section (with the new orientation).
  if (line === '<!-- landscape-start -->') {
    orientationBreaks.push({ atIndex: paragraphs.length, orientation: 'landscape' });
    continue;
  }
  if (line === '<!-- landscape-end -->') {
    orientationBreaks.push({ atIndex: paragraphs.length, orientation: 'portrait' });
    continue;
  }

  // Markdown image: ![alt](path)
  const imgMatch = line.match(/^!\[([^\]]*)\]\(([^)]+)\)\s*$/);
  if (imgMatch) {
    const imgPath = path.resolve(path.dirname(inputPath), imgMatch[2]);
    try {
      const imgData = fs.readFileSync(imgPath);
      const ext = path.extname(imgPath).toLowerCase().replace('.', '') || 'png';
      // Default: 720 px wide (fills 6.5" text column). Images whose filename
      // starts with "Signature" or "signature" get rendered smaller (2" wide)
      // so they sit inline above a typed name without overwhelming the layout.
      // Logo images (filename containing "logo") are sized to ~5" wide.
      const baseName = path.basename(imgPath).toLowerCase();
      let targetWidthPx = 720;
      if (baseName.includes('signature')) targetWidthPx = 200;  // ~2.08"
      else if (baseName.includes('logo')) targetWidthPx = 480;  // ~5.0"
      let aspect = 0.56; // fallback if we can't read the header
      if (ext === 'png' && imgData.length >= 24) {
        // PNG IHDR: width at bytes 16-19, height at bytes 20-23 (big-endian)
        const w = imgData.readUInt32BE(16);
        const h = imgData.readUInt32BE(20);
        if (w > 0 && h > 0) aspect = h / w;
      }
      paragraphs.push(new Paragraph({
        children: [new ImageRun({
          data: imgData,
          transformation: { width: targetWidthPx, height: Math.round(targetWidthPx * aspect) },
          type: ext === 'jpg' ? 'jpg' : ext,
        })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 120, after: 120 },
      }));
      continue;
    } catch (err) {
      console.error(`Could not embed image ${imgPath}: ${err.message}`);
    }
  }

  // Markdown table detection — look ahead for the separator row on the next line.
  if (isTableRow(line) && i + 1 < lines.length && isTableSeparator(lines[i + 1].replace(/\s+$/, ''))) {
    const tableLines = [line, lines[i + 1].replace(/\s+$/, '')];
    let j = i + 2;
    while (j < lines.length && isTableRow(lines[j].replace(/\s+$/, ''))) {
      tableLines.push(lines[j].replace(/\s+$/, ''));
      j++;
    }
    paragraphs.push(buildTable(tableLines));
    // Spacer paragraph after the table so the next block doesn't jam against it
    paragraphs.push(new Paragraph({ children: [new TextRun({ text: '' })], spacing: { after: 120 } }));
    i = j - 1;
    continue;
  }

  // Markdown thematic break (---, ***, ___): render as a thin centred
  // horizontal rule paragraph, NOT a page break. (The previous behaviour of
  // treating these as page breaks was a legacy cover-letter-only hack and
  // caused orphaned blank pages in supplements that use --- as section
  // dividers.)
  if (/^(?:-{3,}|\*{3,}|_{3,})$/.test(line)) {
    paragraphs.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: '\u2500\u2500\u2500\u2500\u2500', color: '9CA3AF', size: 16 })],
      spacing: { before: 60, after: 60 },
    }));
    continue;
  }

  // Headings
  let m;
  if ((m = line.match(/^#\s+(.+)$/))) {
    paragraphs.push(new Paragraph({
      heading: HeadingLevel.HEADING_1,
      children: parseInline(stripOuterBold(m[1])),
    }));
    continue;
  }
  if ((m = line.match(/^##\s+(.+)$/))) {
    paragraphs.push(new Paragraph({
      heading: HeadingLevel.HEADING_2,
      children: parseInline(stripOuterBold(m[1])),
    }));
    continue;
  }
  if ((m = line.match(/^###\s+(.+)$/))) {
    paragraphs.push(new Paragraph({
      heading: HeadingLevel.HEADING_3,
      children: parseInline(stripOuterBold(m[1])),
    }));
    continue;
  }

  // Plain paragraph (numbered list items like "1. ..." stay as paragraphs with
  // the number preserved — simpler and matches manuscript formatting for refs
  // and abstract bullet-points)
  paragraphs.push(new Paragraph({
    children: parseInline(line),
    spacing: { after: 120 }, // small spacing between paragraphs
  }));
}

// --- build document ---
const wantAnonymous = flags.includes('--anonymous');
const doc = new Document({
  creator: wantAnonymous ? 'DBPR' : 'Erika Freeman',
  title: wantAnonymous ? 'DBPR manuscript' : 'Freshwater prediction is not a modelling problem',
  styles: {
    default: {
      document: {
        run: { font: 'Arial', size: 22 }, // 11pt
        paragraph: { spacing: { line: 360, lineRule: 'auto' } }, // 1.5-line spacing
      },
    },
    paragraphStyles: [
      {
        id: 'Heading1',
        name: 'Heading 1',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { size: 32, bold: true, font: 'Arial', color: '000000' },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 },
      },
      {
        id: 'Heading2',
        name: 'Heading 2',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { size: 26, bold: true, font: 'Arial', color: '000000' },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 },
      },
      {
        id: 'Heading3',
        name: 'Heading 3',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { size: 24, bold: true, italics: true, font: 'Arial', color: '000000' },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 2 },
      },
    ],
  },
  sections: buildSections(),
});

function buildSectionProps(orientation) {
  return {
    page: {
      size: orientation === 'landscape'
        ? { width: 12240, height: 15840, orientation: 'landscape' }
        : { width: 12240, height: 15840 },
      margin: orientation === 'landscape'
        ? { top: 1080, right: 1440, bottom: 1080, left: 1440 }
        : { top: 1440, right: 1440, bottom: 1440, left: 1440 },
    },
    ...(wantLineNumbers ? {
      lineNumbers: {
        countBy: 1,
        start: 1,
        restart: LineNumberRestartFormat.CONTINUOUS,
        distance: 360,
      },
    } : {}),
  };
}

function pageFooter() {
  return {
    default: new Footer({
      children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: 'Page ', size: 18, color: '6B7280' }),
          new TextRun({ children: [PageNumber.CURRENT], size: 18, color: '6B7280' }),
          new TextRun({ text: ' of ', size: 18, color: '6B7280' }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, color: '6B7280' }),
        ],
      })],
    }),
  };
}

function buildSections() {
  const baseOrientation = flags.includes('--landscape') ? 'landscape' : 'portrait';
  if (orientationBreaks.length === 0) {
    return [{
      properties: buildSectionProps(baseOrientation),
      footers: pageFooter(),
      children: paragraphs,
    }];
  }
  const out = [];
  let currentOrient = baseOrientation;
  let cursor = 0;
  for (const brk of orientationBreaks) {
    if (brk.atIndex > cursor) {
      out.push({
        properties: buildSectionProps(currentOrient),
        footers: pageFooter(),
        children: paragraphs.slice(cursor, brk.atIndex),
      });
    }
    cursor = brk.atIndex;
    currentOrient = brk.orientation;
  }
  if (cursor < paragraphs.length) {
    out.push({
      properties: buildSectionProps(currentOrient),
      footers: pageFooter(),
      children: paragraphs.slice(cursor),
    });
  }
  return out;
}

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(outputPath, buffer);
  console.log(`Wrote ${outputPath} (${buffer.length} bytes, ${paragraphs.length} paragraphs)`);
}).catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
