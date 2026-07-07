// BareCount conceptual deck — generated from bc-docs source material.
// Visual: Midnight Executive (deep navy + brass accent). Dark title/closing, light content.
// Tone: declarative, third-person, no contractions, no em dashes in titles.

const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 inches
pres.title = "BareCount — The enterprise observation platform";
pres.author = "BareCount";

// ---- Palette ----
const C = {
  navy:     "0B1F3A", // dark backgrounds
  navyDeep: "06142A",
  ink:      "0F172A", // primary text on light
  cream:    "FAFBFC", // light backgrounds
  off:      "E5E9F0", // primary text on dark
  muted:    "5B6478", // captions, secondary
  rule:     "CFD6E1", // hairlines / table borders
  brass:    "B8945F", // accent
  brassDk:  "8E6F3F",
  card:     "FFFFFF", // card fill on cream
  shade:    "F2F4F8", // alt row / soft card
};

const F = {
  head: "Georgia",
  body: "Calibri",
  mono: "Consolas",
};

const W = 13.333, H = 7.5;

// ---- Reusable helpers ----
function brassMark(slide, x, y, size = 0.18) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: size, h: size, fill: { color: C.brass }, line: { type: "none" },
  });
}

function pageTitle(slide, text, opts = {}) {
  const x = opts.x ?? 0.7;
  const y = opts.y ?? 0.55;
  brassMark(slide, x, y + 0.18);
  slide.addText(text, {
    x: x + 0.38, y, w: W - x - 0.7, h: 0.7,
    fontFace: F.head, fontSize: 30, bold: true, color: C.ink,
    align: "left", valign: "middle", margin: 0,
  });
}

function pageFooter(slide, citation, pageNum) {
  slide.addText("BareCount  ·  conceptual reference  ·  bc-docs", {
    x: 0.7, y: H - 0.42, w: 8, h: 0.3,
    fontFace: F.body, fontSize: 9, color: C.muted, align: "left", margin: 0,
  });
  if (citation) {
    slide.addText(citation, {
      x: 0.7, y: H - 0.62, w: W - 1.4, h: 0.22,
      fontFace: F.body, fontSize: 9, italic: true, color: C.brassDk, align: "left", margin: 0,
    });
  }
  if (pageNum) {
    slide.addText(String(pageNum), {
      x: W - 1.0, y: H - 0.42, w: 0.3, h: 0.3,
      fontFace: F.body, fontSize: 9, color: C.muted, align: "right", margin: 0,
    });
  }
}

function lightSlide() {
  const slide = pres.addSlide();
  slide.background = { color: C.cream };
  return slide;
}

function darkSlide() {
  const slide = pres.addSlide();
  slide.background = { color: C.navy };
  return slide;
}

// ============================================================
// SLIDE 1 — TITLE (dark)
// ============================================================
{
  const s = darkSlide();
  // Brass marker top-left
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 0.7, w: 0.32, h: 0.32, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("bc-docs", {
    x: 1.15, y: 0.7, w: 4, h: 0.32,
    fontFace: F.body, fontSize: 11, color: C.off, valign: "middle", margin: 0,
    charSpacing: 4,
  });

  // Big title
  s.addText("BareCount", {
    x: 0.7, y: 2.4, w: W - 1.4, h: 1.1,
    fontFace: F.head, fontSize: 72, bold: true, color: C.brass,
    align: "left", valign: "bottom", margin: 0, charSpacing: -1,
  });
  s.addText("The enterprise observation platform", {
    x: 0.7, y: 3.55, w: W - 1.4, h: 0.6,
    fontFace: F.head, fontSize: 26, italic: true, color: C.off,
    align: "left", valign: "top", margin: 0,
  });

  // Thin brass underline (short, not full-width — acts as marker, not a banner bar)
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 4.45, w: 1.6, h: 0.04, fill: { color: C.brass }, line: { type: "none" },
  });

  s.addText("Conceptual reference. Architecture, not marketing.", {
    x: 0.7, y: 4.65, w: W - 1.4, h: 0.4,
    fontFace: F.body, fontSize: 14, color: C.off, italic: false, margin: 0,
  });

  // Bottom strap — eight sections
  s.addText(
    "Foundation  ·  Operating Model  ·  Implementation  ·  AI  ·  Development  ·  Onboarding  ·  Operations  ·  Compliance",
    {
      x: 0.7, y: H - 0.95, w: W - 1.4, h: 0.35,
      fontFace: F.body, fontSize: 10, color: C.muted, charSpacing: 2, margin: 0,
    }
  );
  s.addText("The documentation. One home plus eight sections.", {
    x: 0.7, y: H - 0.6, w: W - 1.4, h: 0.3,
    fontFace: F.body, fontSize: 9, italic: true, color: C.brassDk, margin: 0,
  });
}

// ============================================================
// SLIDE 2 — THE WRONG FRAME
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "The frame that does not hold");

  s.addText(
    "An intelligence layer placed on top of one vendor's modules answers the wrong question. The enterprise does not run on one vendor.",
    {
      x: 0.7, y: 1.4, w: W - 1.4, h: 0.7,
      fontFace: F.body, fontSize: 14, color: C.muted, italic: true, margin: 0,
    }
  );

  // Two columns
  const colY = 2.3, colH = 4.0, colW = 5.85;

  // Left column — what is offered
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: colY, w: colW, h: colH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: colY, w: 0.08, h: colH, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("What is offered", {
    x: 0.95, y: colY + 0.2, w: colW - 0.4, h: 0.35,
    fontFace: F.head, fontSize: 16, bold: true, color: C.ink, margin: 0, charSpacing: 1,
  });
  s.addText(
    [
      { text: "Natural-language interfaces over one vendor's modules.", options: { bullet: true, breakLine: true } },
      { text: "Agents bounded to one vendor's data graph.", options: { bullet: true, breakLine: true } },
      { text: "Migration accelerated within one vendor's cloud.", options: { bullet: true, breakLine: true } },
      { text: "Governance scoped to one vendor's runtime.", options: { bullet: true } },
    ],
    {
      x: 0.95, y: colY + 0.7, w: colW - 0.4, h: colH - 0.9,
      fontFace: F.body, fontSize: 14, color: C.ink, paraSpaceAfter: 8, margin: 0,
    }
  );

  // Right column — what is preserved
  const rx = 0.7 + colW + 0.45;
  s.addShape(pres.shapes.RECTANGLE, {
    x: rx, y: colY, w: colW, h: colH, fill: { color: C.shade }, line: { color: C.rule, width: 0.75 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: rx, y: colY, w: 0.08, h: colH, fill: { color: C.ink }, line: { type: "none" },
  });
  s.addText("What is left unsolved", {
    x: rx + 0.25, y: colY + 0.2, w: colW - 0.4, h: 0.35,
    fontFace: F.head, fontSize: 16, bold: true, color: C.ink, margin: 0, charSpacing: 1,
  });
  s.addText(
    [
      { text: "Meaning still assigned and reassigned at read time.", options: { bullet: true, breakLine: true } },
      { text: "Audit still reconstructed from logs and replays.", options: { bullet: true, breakLine: true } },
      { text: "Reference still resolves to whichever version is current.", options: { bullet: true, breakLine: true } },
      { text: "Facts in every other source remain outside the frame.", options: { bullet: true } },
    ],
    {
      x: rx + 0.25, y: colY + 0.7, w: colW - 0.4, h: colH - 0.9,
      fontFace: F.body, fontSize: 14, color: C.ink, paraSpaceAfter: 8, margin: 0,
    }
  );

  pageFooter(s, "Foundation. The Problem.", 2);
}

// ============================================================
// SLIDE 3 — THE THREE FAILURE CLASSES
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "Three failure classes that no AI layer fixes");

  s.addText(
    "Architectural rather than operational. Each degrades reliability, traceability, or both.",
    {
      x: 0.7, y: 1.4, w: W - 1.4, h: 0.45,
      fontFace: F.body, fontSize: 13, italic: true, color: C.muted, margin: 0,
    }
  );

  const items = [
    {
      title: "Meaning drift after observation",
      body:
        "Business meaning is assigned, reassigned, and reinterpreted along the execution path. The same observed value carries different meanings across components. Historical comparisons are unreliable.",
    },
    {
      title: "Reconstruction-based audit",
      body:
        "Historical outputs are explained by replaying the original observation, re-running intermediate operations, and reconstructing context. Inputs change. Logic changes. Configuration changes. The answer is an approximation.",
    },
    {
      title: "Implicit reference",
      body:
        "Consumers refer to data by identity alone. Requests for current state resolve at read time. The same reference returns different values at different times. Decisions cannot be traced to the state on which they were made.",
    },
  ];

  const cardY = 2.0, cardH = 4.6, gap = 0.3;
  const cardW = (W - 1.4 - gap * 2) / 3;

  items.forEach((it, i) => {
    const cx = 0.7 + i * (cardW + gap);
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cardY, w: cardW, h: cardH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cardY, w: cardW, h: 0.08, fill: { color: C.brass }, line: { type: "none" },
    });
    s.addText(String(i + 1).padStart(2, "0"), {
      x: cx + 0.35, y: cardY + 0.35, w: 1, h: 0.5,
      fontFace: F.head, fontSize: 28, color: C.brass, bold: true, margin: 0,
    });
    s.addText(it.title, {
      x: cx + 0.35, y: cardY + 0.95, w: cardW - 0.7, h: 0.9,
      fontFace: F.head, fontSize: 18, bold: true, color: C.ink, margin: 0,
    });
    s.addText(it.body, {
      x: cx + 0.35, y: cardY + 1.85, w: cardW - 0.7, h: cardH - 2.1,
      fontFace: F.body, fontSize: 13, color: C.ink, margin: 0, paraSpaceAfter: 4,
    });
  });

  pageFooter(s, "Foundation. The Problem.", 3);
}

// ============================================================
// SLIDE 4 — PROCEDURAL CONTROLS ARE INSUFFICIENT
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "Why procedural controls are insufficient");

  s.addText(
    "Policies and review gates are useful. None is sufficient on its own. The failure modes follow from an architecture that embeds semantic interpretation in procedural code and treats evidence as a secondary artifact.",
    {
      x: 0.7, y: 1.4, w: W - 1.4, h: 0.8,
      fontFace: F.body, fontSize: 13, italic: true, color: C.muted, margin: 0,
    }
  );

  const items = [
    {
      title: "Participant dependence",
      body:
        "A policy is effective only when every component and operator knows it, understands it, and implements it correctly. Each new participant is a new failure surface.",
    },
    {
      title: "Drift from runtime",
      body:
        "The policy recorded in governance documents and the behavior implemented in code are revised through different mechanisms. Over time, the two diverge.",
    },
    {
      title: "Delayed detection",
      body:
        "Review identifies violations after outputs have already been produced and consumed. The cost of correction grows with every downstream act that depended on the violated state.",
    },
  ];

  const rowY = 2.45, rowH = 1.35, rowGap = 0.18;
  items.forEach((it, i) => {
    const ry = rowY + i * (rowH + rowGap);
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: ry, w: W - 1.4, h: rowH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y: ry, w: 0.08, h: rowH, fill: { color: C.brass }, line: { type: "none" },
    });
    s.addText(it.title, {
      x: 0.95, y: ry + 0.18, w: 4.0, h: 0.4,
      fontFace: F.head, fontSize: 17, bold: true, color: C.ink, margin: 0,
    });
    s.addText(it.body, {
      x: 5.05, y: ry + 0.18, w: W - 1.4 - 4.4, h: rowH - 0.3,
      fontFace: F.body, fontSize: 13, color: C.ink, margin: 0, valign: "top",
    });
  });

  pageFooter(s, "Foundation. The Problem.", 4);
}

// ============================================================
// SLIDE 5 — THE STRUCTURAL RESPONSE
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "The structural response");

  s.addText(
    "One response to each failure class. Realized at a single boundary in the execution model. Governed by an authoritative artifact. Bound to the same act that produces authoritative state.",
    {
      x: 0.7, y: 1.4, w: W - 1.4, h: 0.7,
      fontFace: F.body, fontSize: 13, italic: true, color: C.muted, margin: 0,
    }
  );

  const headerFill = { color: C.ink };
  const headerStyle = { color: C.cream, bold: true, fontFace: F.head, fontSize: 13, align: "left", valign: "middle" };
  const cellBaseDark  = { color: C.ink,  fontFace: F.body, fontSize: 12, align: "left", valign: "top", margin: 0.12 };
  const cellBaseBrass = { color: C.ink,  fontFace: F.body, fontSize: 12, bold: true, align: "left", valign: "top", margin: 0.12 };
  const altFill = { color: C.shade };
  const whiteFill = { color: C.card };

  const rows = [
    [
      { text: "Failure class", options: { ...headerStyle, fill: headerFill, margin: 0.12 } },
      { text: "Structural response", options: { ...headerStyle, fill: headerFill, margin: 0.12 } },
      { text: "Operational effect", options: { ...headerStyle, fill: headerFill, margin: 0.12 } },
    ],
    [
      { text: "Meaning drift after observation", options: { ...cellBaseBrass, fill: whiteFill } },
      { text: "Business meaning is produced once at the canonical evaluation boundary by applying a Canonical Contract to one or more Source Objects.", options: { ...cellBaseDark, fill: whiteFill } },
      { text: "Consumers read preserved semantic state. No component reinterprets meaning at read time.", options: { ...cellBaseDark, fill: whiteFill } },
    ],
    [
      { text: "Reconstruction-based audit", options: { ...cellBaseBrass, fill: altFill } },
      { text: "Evidence and Lineage are emitted at the same act that produces authoritative state. Both are immutable and append-only.", options: { ...cellBaseDark, fill: altFill } },
      { text: "Audit reads preserved proof. The platform does not assemble historical answers from logs and replays.", options: { ...cellBaseDark, fill: altFill } },
    ],
    [
      { text: "Implicit reference", options: { ...cellBaseBrass, fill: whiteFill } },
      { text: "Every reference identifies the object's type, identity, and version. Resolutions such as latest or current are not admitted.", options: { ...cellBaseDark, fill: whiteFill } },
      { text: "Two consumers issuing nominally identical requests receive the same value. Decisions are traceable to specific historical state.", options: { ...cellBaseDark, fill: whiteFill } },
    ],
  ];

  s.addTable(rows, {
    x: 0.7, y: 2.25, w: W - 1.4,
    colW: [3.0, 4.93, 4.0],
    rowH: [0.5, 1.05, 1.05, 1.05],
    border: { type: "solid", pt: 0.5, color: C.rule },
    fontFace: F.body,
  });

  pageFooter(s, "Foundation. The Solution.", 5);
}

// ============================================================
// SLIDE 6 — FOUR EVALUATION BOUNDARIES
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "Four governed evaluation boundaries");

  s.addText(
    "Authoritative state is produced only at these boundaries. Read access produces nothing. Evidence and Lineage are emitted at each act.",
    {
      x: 0.7, y: 1.4, w: W - 1.4, h: 0.55,
      fontFace: F.body, fontSize: 13, italic: true, color: C.muted, margin: 0,
    }
  );

  const stages = [
    { name: "Admission",            produces: "Source Object",     note: "External state admitted under a Source and Admission Contract." },
    { name: "Canonical evaluation", produces: "Canonical Object",  note: "Business meaning produced once per version under a Canonical Contract." },
    { name: "Metric evaluation",    produces: "Metric Snapshot",   note: "Metrics computed under a Metric Contract over one or more Canonical Objects." },
    { name: "Action evaluation",    produces: "Action Object",     note: "An action recorded as authoritative state under an Intervention Contract." },
  ];

  const boxW = 2.85, boxH = 3.1, boxY = 2.4;
  const totalW = boxW * 4 + 0.35 * 3;
  const startX = (W - totalW) / 2;

  stages.forEach((st, i) => {
    const bx = startX + i * (boxW + 0.35);
    // Card
    s.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: boxY, w: boxW, h: boxH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
    });
    // Brass strip top
    s.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: boxY, w: boxW, h: 0.1, fill: { color: C.brass }, line: { type: "none" },
    });
    // Number
    s.addText("0" + (i + 1), {
      x: bx + 0.25, y: boxY + 0.25, w: 1, h: 0.5,
      fontFace: F.head, fontSize: 22, color: C.brass, bold: true, margin: 0,
    });
    // Stage name
    s.addText(st.name, {
      x: bx + 0.25, y: boxY + 0.85, w: boxW - 0.5, h: 0.8,
      fontFace: F.head, fontSize: 16, bold: true, color: C.ink, margin: 0,
    });
    // Produces
    s.addText("produces", {
      x: bx + 0.25, y: boxY + 1.55, w: boxW - 0.5, h: 0.25,
      fontFace: F.body, fontSize: 9, italic: true, color: C.muted, margin: 0, charSpacing: 2,
    });
    s.addText(st.produces, {
      x: bx + 0.25, y: boxY + 1.78, w: boxW - 0.5, h: 0.35,
      fontFace: F.mono, fontSize: 13, bold: true, color: C.brassDk, margin: 0,
    });
    // Note
    s.addText(st.note, {
      x: bx + 0.25, y: boxY + 2.2, w: boxW - 0.5, h: boxH - 2.35,
      fontFace: F.body, fontSize: 11, color: C.ink, margin: 0, valign: "top",
    });

    // Arrow between boxes
    if (i < 3) {
      const ax = bx + boxW + 0.04;
      s.addText("→", {
        x: ax, y: boxY + boxH / 2 - 0.25, w: 0.27, h: 0.5,
        fontFace: F.head, fontSize: 24, bold: true, color: C.brass, align: "center", valign: "middle", margin: 0,
      });
    }
  });

  s.addText(
    "Evidence and Lineage are emitted at every boundary. Read access never triggers evaluation.",
    {
      x: 0.7, y: H - 1.0, w: W - 1.4, h: 0.35,
      fontFace: F.body, fontSize: 12, color: C.ink, align: "center", italic: true, margin: 0,
    }
  );

  pageFooter(s, "Foundation. The Evaluation Boundaries.", 6);
}

// ============================================================
// SLIDE 7 — SIX AUTHORITATIVE OBJECTS
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "Six authoritative objects");

  s.addText(
    "Four progression objects carry state. Two proof objects carry evidence. All six are immutable. Corrections create new versions; the original remains addressable.",
    {
      x: 0.7, y: 1.4, w: W - 1.4, h: 0.65,
      fontFace: F.body, fontSize: 13, italic: true, color: C.muted, margin: 0,
    }
  );

  // Row 1 — progression (4 boxes)
  const r1Y = 2.4, objW = 2.85, objH = 1.85;
  const r1TotalW = objW * 4 + 0.3 * 3;
  const r1Start = (W - r1TotalW) / 2;
  s.addText("Progression objects", {
    x: r1Start, y: r1Y - 0.42, w: 4, h: 0.32,
    fontFace: F.body, fontSize: 10, color: C.muted, charSpacing: 3, margin: 0,
  });

  const progression = ["Source Object", "Canonical Object", "Metric Snapshot", "Action Object"];
  progression.forEach((name, i) => {
    const bx = r1Start + i * (objW + 0.3);
    s.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: r1Y, w: objW, h: objH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: r1Y, w: 0.08, h: objH, fill: { color: C.brass }, line: { type: "none" },
    });
    s.addText(name, {
      x: bx + 0.25, y: r1Y + 0.35, w: objW - 0.4, h: 0.5,
      fontFace: F.head, fontSize: 16, bold: true, color: C.ink, margin: 0,
    });
    s.addText("immutable. versioned.", {
      x: bx + 0.25, y: r1Y + 0.95, w: objW - 0.4, h: 0.3,
      fontFace: F.body, fontSize: 10, italic: true, color: C.muted, margin: 0,
    });
    const role = ["state admitted", "meaning evaluated", "metric resolved", "action recorded"][i];
    s.addText(role, {
      x: bx + 0.25, y: r1Y + 1.25, w: objW - 0.4, h: 0.45,
      fontFace: F.body, fontSize: 11, color: C.ink, margin: 0,
    });
  });

  // Row 2 — proof (2 boxes, wider)
  const r2Y = r1Y + objH + 0.7;
  const proofW = (r1TotalW - 0.4) / 2;
  s.addText("Proof objects", {
    x: r1Start, y: r2Y - 0.42, w: 4, h: 0.32,
    fontFace: F.body, fontSize: 10, color: C.muted, charSpacing: 3, margin: 0,
  });

  ["Evidence", "Lineage"].forEach((name, i) => {
    const bx = r1Start + i * (proofW + 0.4);
    s.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: r2Y, w: proofW, h: 1.85, fill: { color: C.shade }, line: { color: C.rule, width: 0.75 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: r2Y, w: 0.08, h: 1.85, fill: { color: C.ink }, line: { type: "none" },
    });
    s.addText(name, {
      x: bx + 0.3, y: r2Y + 0.3, w: proofW - 0.5, h: 0.5,
      fontFace: F.head, fontSize: 18, bold: true, color: C.ink, margin: 0,
    });
    const role = i === 0
      ? "Per-record outcomes recorded at the same act that produced the object. Append-only."
      : "References that bind a produced object to its predecessors. Append-only.";
    s.addText(role, {
      x: bx + 0.3, y: r2Y + 0.95, w: proofW - 0.5, h: 0.85,
      fontFace: F.body, fontSize: 12, color: C.ink, margin: 0, valign: "top",
    });
  });

  pageFooter(s, "Foundation. The Object Model.", 7);
}

// ============================================================
// SLIDE 8 — MULTI-SOURCE, MULTI-STANDARD
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "Multi-source by design. Multi-standard by binding.");

  s.addText(
    "The same admitted facts bind to every standard the enterprise reports under. The canonical layer sits between the systems the enterprise actually runs and the standards the enterprise actually reports.",
    {
      x: 0.7, y: 1.4, w: W - 1.4, h: 0.7,
      fontFace: F.body, fontSize: 13, italic: true, color: C.muted, margin: 0,
    }
  );

  // Three columns: sources | canonical | standards
  const colY = 2.55, colH = 3.9;
  const lw = 3.6, mw = 4.6, rw = 3.6;
  const lx = 0.7;
  const mx = lx + lw + 0.3;
  const rx = mx + mw + 0.3;

  // Left — sources
  s.addShape(pres.shapes.RECTANGLE, {
    x: lx, y: colY, w: lw, h: colH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: lx, y: colY, w: lw, h: 0.1, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("Source systems", {
    x: lx + 0.25, y: colY + 0.25, w: lw - 0.5, h: 0.45,
    fontFace: F.head, fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  s.addText("any system the enterprise runs", {
    x: lx + 0.25, y: colY + 0.7, w: lw - 0.5, h: 0.3,
    fontFace: F.body, fontSize: 10, italic: true, color: C.muted, margin: 0,
  });
  s.addText(
    [
      { text: "ERPs (one or many)", options: { bullet: true, breakLine: true } },
      { text: "Payroll systems", options: { bullet: true, breakLine: true } },
      { text: "Billing platforms", options: { bullet: true, breakLine: true } },
      { text: "Treasury systems", options: { bullet: true, breakLine: true } },
      { text: "Subsidiary ledgers", options: { bullet: true, breakLine: true } },
      { text: "Spreadsheets and exports", options: { bullet: true } },
    ],
    {
      x: lx + 0.25, y: colY + 1.15, w: lw - 0.5, h: colH - 1.3,
      fontFace: F.body, fontSize: 12, color: C.ink, paraSpaceAfter: 4, margin: 0,
    }
  );

  // Middle — canonical layer (highlighted, dark)
  s.addShape(pres.shapes.RECTANGLE, {
    x: mx, y: colY, w: mw, h: colH, fill: { color: C.ink }, line: { type: "none" },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: mx, y: colY, w: mw, h: 0.1, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("Canonical evaluation", {
    x: mx + 0.3, y: colY + 0.3, w: mw - 0.6, h: 0.45,
    fontFace: F.head, fontSize: 17, bold: true, color: C.brass, margin: 0,
  });
  s.addText("one semantic act per object version", {
    x: mx + 0.3, y: colY + 0.78, w: mw - 0.6, h: 0.3,
    fontFace: F.body, fontSize: 10, italic: true, color: C.off, margin: 0,
  });
  s.addText(
    [
      { text: "Governed by Canonical Contracts", options: { bullet: true, breakLine: true } },
      { text: "Produced once per Canonical Object version", options: { bullet: true, breakLine: true } },
      { text: "Evidence and Lineage emitted at the same act", options: { bullet: true, breakLine: true } },
      { text: "Versions never modified, never overwritten", options: { bullet: true, breakLine: true } },
      { text: "Tenant binding selects which standards apply", options: { bullet: true } },
    ],
    {
      x: mx + 0.3, y: colY + 1.2, w: mw - 0.6, h: colH - 1.35,
      fontFace: F.body, fontSize: 12, color: C.off, paraSpaceAfter: 4, margin: 0,
    }
  );

  // Right — standards
  s.addShape(pres.shapes.RECTANGLE, {
    x: rx, y: colY, w: rw, h: colH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: rx, y: colY, w: rw, h: 0.1, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("Reporting standards", {
    x: rx + 0.25, y: colY + 0.25, w: rw - 0.5, h: 0.45,
    fontFace: F.head, fontSize: 16, bold: true, color: C.ink, margin: 0,
  });
  s.addText("every standard bound to the same facts", {
    x: rx + 0.25, y: colY + 0.7, w: rw - 0.5, h: 0.3,
    fontFace: F.body, fontSize: 10, italic: true, color: C.muted, margin: 0,
  });
  s.addText(
    [
      { text: "GAAP", options: { bullet: true, breakLine: true } },
      { text: "IFRS", options: { bullet: true, breakLine: true } },
      { text: "Ind-AS", options: { bullet: true, breakLine: true } },
      { text: "Tax (per jurisdiction)", options: { bullet: true, breakLine: true } },
      { text: "Management reporting", options: { bullet: true, breakLine: true } },
      { text: "Regulator-specific filings", options: { bullet: true } },
    ],
    {
      x: rx + 0.25, y: colY + 1.15, w: rw - 0.5, h: colH - 1.3,
      fontFace: F.body, fontSize: 12, color: C.ink, paraSpaceAfter: 4, margin: 0,
    }
  );

  pageFooter(s, "Operating Model. Tenancy and Binding. Multi-standard Onboarding.", 8);
}

// ============================================================
// SLIDE 9 — WHAT THIS IS NOT
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "What this is not");

  const items = [
    {
      h: "Not ETL",
      b: "Authority lives at the evaluation boundary, not in a movement step. The vocabulary of pipelines, stages, and refreshes is not admitted by the platform's grammar.",
    },
    {
      h: "Not BI",
      b: "BI reads. The platform produces authoritative state and emits proof at the producing act. A dashboard placed on top of unobserved facts does not preserve meaning.",
    },
    {
      h: "Not AI on one ERP",
      b: "The platform admits sources from every system the enterprise runs. An intelligence layer scoped to one vendor's data graph cannot answer questions that span the enterprise.",
    },
    {
      h: "Not procedural governance",
      b: "Correctness is a structural property of the contract grammar. Policies and review gates supplement the grammar; they do not substitute for it.",
    },
  ];

  const gridY = 1.65, gridH = 5.0;
  const cW = (W - 1.4 - 0.3) / 2;
  const cH = (gridH - 0.3) / 2;

  items.forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const cx = 0.7 + col * (cW + 0.3);
    const cy = gridY + row * (cH + 0.3);
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cy, w: cW, h: cH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cy, w: 0.08, h: cH, fill: { color: C.brass }, line: { type: "none" },
    });
    s.addText(it.h, {
      x: cx + 0.3, y: cy + 0.25, w: cW - 0.5, h: 0.5,
      fontFace: F.head, fontSize: 18, bold: true, color: C.ink, margin: 0,
    });
    s.addText(it.b, {
      x: cx + 0.3, y: cy + 0.85, w: cW - 0.5, h: cH - 1.0,
      fontFace: F.body, fontSize: 13, color: C.ink, margin: 0, valign: "top",
    });
  });

  pageFooter(s, "Platform Overview. Foundation.", 9);
}

// ============================================================
// SLIDE 10 — GOVERNANCE POSTURE
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "Governance posture");

  s.addText(
    "Discipline preserved as artifacts, not as practice. Every architectural decision recorded before code lands.",
    {
      x: 0.7, y: 1.4, w: W - 1.4, h: 0.45,
      fontFace: F.body, fontSize: 13, italic: true, color: C.muted, margin: 0,
    }
  );

  const items = [
    { h: "Patent-backed execution model", b: "The four boundaries, the six objects, and the contract grammar are recorded as a granted invention." },
    { h: "Immutable evidence chain",       b: "Evidence and Lineage are append-only. Authoritative state is never altered in place. Corrections create new versions." },
    { h: "ISO 27001 and SOC 2 posture",    b: "Conformance documented in the Compliance section. Controls map to preserved state, not to participant attestation." },
    { h: "ADR-first decision discipline",  b: "Every architectural decision recorded as an authoritative artifact under the Decisions peer. The ADR file is the source of truth." },
  ];

  const gridY = 2.1, gridH = 4.5;
  const cW = (W - 1.4 - 0.3) / 2;
  const cH = (gridH - 0.3) / 2;

  items.forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const cx = 0.7 + col * (cW + 0.3);
    const cy = gridY + row * (cH + 0.3);
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cy, w: cW, h: cH, fill: { color: C.shade }, line: { color: C.rule, width: 0.75 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: cx, y: cy, w: 0.18, h: 0.18, fill: { color: C.brass }, line: { type: "none" },
    });
    s.addText(it.h, {
      x: cx + 0.3, y: cy + 0.4, w: cW - 0.5, h: 0.5,
      fontFace: F.head, fontSize: 16, bold: true, color: C.ink, margin: 0,
    });
    s.addText(it.b, {
      x: cx + 0.3, y: cy + 0.95, w: cW - 0.5, h: cH - 1.1,
      fontFace: F.body, fontSize: 12, color: C.ink, margin: 0, valign: "top",
    });
  });

  pageFooter(s, "Compliance. Development. Decision and Change Procedure.", 10);
}

// ============================================================
// SLIDE 11 — WHERE BARECOUNT SITS
// ============================================================
{
  const s = lightSlide();
  pageTitle(s, "Where BareCount sits");

  s.addText(
    "Between every source the enterprise runs and every standard the enterprise reports under. The layer the enterprise cannot replace with a single-vendor SKU.",
    {
      x: 0.7, y: 1.4, w: W - 1.4, h: 0.7,
      fontFace: F.body, fontSize: 13, italic: true, color: C.muted, margin: 0,
    }
  );

  // Three large bands stacked
  const bandY = 2.55, bandH = 1.15, gap = 0.25;

  // Sources
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: bandY, w: W - 1.4, h: bandH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: bandY, w: 0.08, h: bandH, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("Every source the enterprise runs", {
    x: 0.95, y: bandY + 0.2, w: 5.5, h: 0.45,
    fontFace: F.head, fontSize: 17, bold: true, color: C.ink, margin: 0,
  });
  s.addText("ERPs, payroll, billing, treasury, subsidiary ledgers, spreadsheets, exports.", {
    x: 0.95, y: bandY + 0.65, w: W - 2.0, h: 0.4,
    fontFace: F.body, fontSize: 12, color: C.ink, margin: 0,
  });

  // Arrow
  s.addText("↓", {
    x: W / 2 - 0.25, y: bandY + bandH + 0.02, w: 0.5, h: 0.22,
    fontFace: F.head, fontSize: 18, bold: true, color: C.brass, align: "center", margin: 0,
  });

  // Canonical
  const b2 = bandY + bandH + gap;
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: b2, w: W - 1.4, h: bandH + 0.2, fill: { color: C.ink }, line: { type: "none" },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: b2, w: 0.08, h: bandH + 0.2, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("BareCount", {
    x: 0.95, y: b2 + 0.2, w: 4.0, h: 0.5,
    fontFace: F.head, fontSize: 20, bold: true, color: C.brass, margin: 0,
  });
  s.addText("Canonical evaluation. Governed contracts. Immutable Evidence and Lineage.", {
    x: 0.95, y: b2 + 0.7, w: W - 2.0, h: 0.5,
    fontFace: F.body, fontSize: 13, color: C.off, margin: 0,
  });

  // Arrow
  s.addText("↓", {
    x: W / 2 - 0.25, y: b2 + bandH + 0.24, w: 0.5, h: 0.22,
    fontFace: F.head, fontSize: 18, bold: true, color: C.brass, align: "center", margin: 0,
  });

  // Standards
  const b3 = b2 + bandH + 0.2 + gap;
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: b3, w: W - 1.4, h: bandH, fill: { color: C.card }, line: { color: C.rule, width: 0.75 },
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: b3, w: 0.08, h: bandH, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("Every standard the enterprise reports under", {
    x: 0.95, y: b3 + 0.2, w: 7.5, h: 0.45,
    fontFace: F.head, fontSize: 17, bold: true, color: C.ink, margin: 0,
  });
  s.addText("GAAP, IFRS, Ind-AS, tax (per jurisdiction), management, regulator filings.", {
    x: 0.95, y: b3 + 0.65, w: W - 2.0, h: 0.4,
    fontFace: F.body, fontSize: 12, color: C.ink, margin: 0,
  });

  pageFooter(s, "Platform Overview. Operating Model.", 11);
}

// ============================================================
// SLIDE 12 — CLOSING (dark)
// ============================================================
{
  const s = darkSlide();

  // Top brass marker
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 0.7, w: 0.32, h: 0.32, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("Closing", {
    x: 1.15, y: 0.7, w: 4, h: 0.32,
    fontFace: F.body, fontSize: 11, color: C.off, valign: "middle", charSpacing: 4, margin: 0,
  });

  // Quote
  s.addText("“", {
    x: 0.7, y: 2.1, w: 1.5, h: 1.5,
    fontFace: F.head, fontSize: 120, color: C.brass, bold: true, margin: 0,
  });
  s.addText(
    "Correctness is a structural property of the contract grammar, not an operational property of any particular run.",
    {
      x: 1.7, y: 2.5, w: W - 2.4, h: 2.4,
      fontFace: F.head, fontSize: 30, italic: true, color: C.off, margin: 0, valign: "top",
    }
  );

  // Source citation
  s.addShape(pres.shapes.RECTANGLE, {
    x: 1.7, y: 5.2, w: 0.5, h: 0.03, fill: { color: C.brass }, line: { type: "none" },
  });
  s.addText("Platform Overview. bc-docs.", {
    x: 1.7, y: 5.28, w: W - 2.4, h: 0.4,
    fontFace: F.body, fontSize: 13, color: C.brass, charSpacing: 2, margin: 0,
  });

  // Bottom strap
  s.addText("BareCount  ·  the enterprise observation platform", {
    x: 0.7, y: H - 0.7, w: W - 1.4, h: 0.4,
    fontFace: F.body, fontSize: 11, color: C.muted, charSpacing: 3, margin: 0,
  });
}

// ---- Write file ----
pres
  .writeFile({ fileName: "C:/MyProjects/bc-docs/docs/assets/barecount-conceptual-deck.pptx" })
  .then((f) => console.log("Wrote:", f));

