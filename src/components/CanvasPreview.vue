<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const canvasRef = ref(null);
let animId = null;

// ═══════════════════════════════════════════════════
//  Configuration
// ═══════════════════════════════════════════════════
const DOT_SPACING  = 26;
const BLOCK_GAP    = 50;
const ROWS         = 7;
const COLS         = 7;
const NUM_BLOCKS   = 4;
const MOUSE_RADIUS = 20;
const ENTER_TIME   = 2.0;

// ══════════════════════════════════════════════════
//  Pre-computed color tables — 消除每帧 parseInt
// ═══════════════════════════════════════════════════
const hx = (s) => [
  parseInt(s.slice(1, 3), 16),
  parseInt(s.slice(3, 5), 16),
  parseInt(s.slice(5, 7), 16),
];

const GRAYS = [
  "#ffffff", "#f0f0f0", "#e8e8e8", "#e0e0e0", "#d8d8d8", "#d0d0d0",
  "#c8c8c8", "#c0c0c0", "#b8b8b8", "#b0b0b0", "#a8a8a8", "#a0a0a0",
  "#989898", "#909090", "#888888", "#808080", "#787878", "#707070",
  "#686868", "#606060", "#585858", "#505050", "#484848", "#404040",
  "#383838", "#303030", "#282828", "#202020", "#181818", "#101010",
].map(hx);

const ACCENTS = ["#5b9bd5", "#70c070", "#d07070", "#9070b0", "#d070b0"].map(hx);

// ═══════════════════════════════════════════════════
//  Letter patterns (7×7 grid)
// ═══════════════════════════════════════════════════
const PATTERNS = [
  // K
  [
    [0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0],
    [0, 1, 0, 1, 0, 0, 0],
    [0, 1, 0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
  ],
  // i
  [
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
  ],
  // m
  [
    [1, 1, 0, 0, 0, 1, 1],
    [1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
  ],
  // i
  [
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
  ],
];

// ═══════════════════════════════════════════════════
//  Runtime state
// ═══════════════════════════════════════════════════
let dots = [];
let time = 0;
let hovering = false;
let hoverT = 0;
let elapsed = 0;
let lastTs = 0;
let mouse = { x: -9999, y: -9999, active: false };
let cachedW = 0;
let cachedH = 0;
let cachedDpr = 0;

// ═══════════════════════════════════════════════════
//  Easing helpers
// ═══════════════════════════════════════════════════
const clamp01 = (v) => (v < 0 ? 0 : v > 1 ? 1 : v);
const easeOutExpo = (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t));

// ═══════════════════════════════════════════════════
//  createDots
// ═══════════════════════════════════════════════════
function createDots() {
  dots = [];
  let ox = 0;
  let ai = 0;

  for (let b = 0; b < NUM_BLOCKS; b++) {
    const pat = PATTERNS[b];
    const cr = (ROWS - 1) / 2;
    const cc = (COLS - 1) / 2;
    const md = Math.sqrt(cr * cr + cc * cc);

    // 每个方块 3-5 个彩色点
    const accentCount = 3 + ~~(Math.random() * 3);
    const accentSet = new Set();
    for (let i = 0; i < accentCount; i++) {
      accentSet.add(~~(Math.random() * ROWS * COLS));
    }

    for (let r = 0; r < ROWS; r++) {
      for (let c = 0; c < COLS; c++) {
        const dr = r - cr;
        const dc = c - cc;
        const d = Math.sqrt(dr * dr + dc * dc) / md;
        const sf = 1 - d * 0.2;
        const tx =
          ox + (c - cc) * DOT_SPACING * sf + cc * DOT_SPACING;
        const ty = (r - cr) * DOT_SPACING * sf + cr * DOT_SPACING;

        let color;
        let accent = false;
        const idx = r * COLS + c;
        if (accentSet.has(idx)) {
          color = ACCENTS[ai++ % ACCENTS.length];
          accent = true;
        } else {
          color = GRAYS[~~(Math.pow(Math.random(), 0.7) * GRAYS.length)];
        }

        dots.push({
          tx,
          ty,
          x: tx,
          y: ty,
          color,
          accent,
          letter: pat[r][c] === 1,
          phase: Math.random() * Math.PI * 2,
          baseR: DOT_SPACING * 0.38 * (1 - d * 0.5),
          sx: (Math.random() - 0.5) * 200,
          sy: (Math.random() - 0.5) * 200,
          delay: d * 0.4 + b * 0.08 + Math.random() * 0.1,
        });
      }
    }
    ox += COLS * DOT_SPACING + BLOCK_GAP;
  }

  const cx = -(ox - BLOCK_GAP) / 2;
  dots.forEach((d) => {
    d.tx += cx;
    d.sx += d.tx;
    d.sy += d.ty;
  });
}

// ═══════════════════════════════════════════════════
//  drawDot
// ═══════════════════════════════════════════════════
function drawDot(ctx, dot, t, ht, ent) {
  const pulse = Math.sin(t * 1.2 + dot.phase);
  const breathR = Math.max(
    dot.baseR * 0.6,
    dot.baseR * (0.7 + 0.3 * pulse)
  );
  const breathA = 0.7 + 0.15 * (pulse + 1);

  // 鼠标靠近时点变小
  let mouseScale = 1;
  if (mouse.active) {
    const dx = dot.x - mouse.x;
    const dy = dot.y - mouse.y;
    const md = Math.sqrt(dx * dx + dy * dy);
    if (md < MOUSE_RADIUS && md > 0.1) {
      const f = 1 - md / MOUSE_RADIUS;
      mouseScale = 1 - f * 0.5; // 最近时缩小到 50%
    }
  }

  const px = dot.x;
  const py = dot.y;

  const hoverScale = dot.letter ? 1 + 0.1 * ht : 1 - 0.05 * ht;
  const r = (breathR + (dot.baseR - breathR) * ht) * ent * hoverScale * mouseScale;

  const [cr, cg, cb] = dot.color;
  const nr = Math.max(cr, 0x33);
  const ng = Math.max(cg, 0x33);
  const nb = Math.max(cb, 0x33);

  // 彩色点的灰度版本（RGB 平均值）
  const grayVal = ~~((cr + cg + cb) / 3);

  // 彩色↔灰度呼吸：用 sin 让颜色在原始彩色和灰度之间周期性摆动
  // 频率 0.8，相位用 dot.phase，hover 时压制这个效果
  const colorBreath = Math.sin(t * 0.8 + dot.phase) * 0.5 + 0.5; // 0~1
  const colorBlend = dot.accent ? colorBreath * (1 - ht * 0.8) : 0; // hover 时减弱

  // 混合后的基础颜色：彩色点会在彩色和灰度之间呼吸
  const baseR = nr + (grayVal - nr) * colorBlend;
  const baseG = ng + (grayVal - ng) * colorBlend;
  const baseB = nb + (grayVal - nb) * colorBlend;

  let fr, fg, fb, fa;
  if (dot.letter) {
    fr = baseR + (0xf0 - baseR) * ht;
    fg = baseG + (0xf0 - baseG) * ht;
    fb = baseB + (0xf0 - baseB) * ht;
    fa = breathA + (1 - breathA) * ht;
  } else {
    fr = baseR + (0x40 - baseR) * ht;
    fg = baseG + (0x40 - baseG) * ht;
    fb = baseB + (0x40 - baseB) * ht;
    fa = breathA + (0.45 - breathA) * ht;
  }

  fa *= ent;

  if (fr > 255) fr = 255;
  if (fg > 255) fg = 255;
  if (fb > 255) fb = 255;

  if (dot.accent && ht < 0.8) {
    const glowA = 0.5 * (1 - ht) * ent;
    ctx.shadowColor = `rgba(${~~baseR},${~~baseG},${~~baseB},${glowA.toFixed(2)})`;
    ctx.shadowBlur = 10 + pulse * 4;
  }

  const s = r * 2;
  const rr = r * 0.8;
  ctx.beginPath();
  ctx.roundRect(px - r, py - r, s, s, rr);
  ctx.fillStyle = `rgba(${~~fr},${~~fg},${~~fb},${fa.toFixed(3)})`;
  ctx.fill();

  if (dot.accent) {
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
  }
}

// ═══════════════════════════════════════════════════
//  Main loop
// ══════════════════════════════════════════════════
function animate(ts) {
  if (!lastTs) lastTs = ts;
  const dt = Math.min((ts - lastTs) * 0.001, 0.05);
  lastTs = ts;
  elapsed += dt;
  time += dt;

  const canvas = canvasRef.value;
  if (!canvas) {
    animId = requestAnimationFrame(animate);
    return;
  }

  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;

  if (w !== cachedW || h !== cachedH || dpr !== cachedDpr) {
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.scale(dpr, dpr);
    cachedW = w;
    cachedH = h;
    cachedDpr = dpr;
  }

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, w, h);

  const htTarget = hovering ? 1 : 0;
  hoverT += (htTarget - hoverT) * (1 - Math.exp(-6 * dt));
  if (Math.abs(hoverT - htTarget) < 0.001) hoverT = htTarget;

  const entProg = clamp01(elapsed / ENTER_TIME);

  ctx.save();
  ctx.translate(w / 2, h / 2);

  for (let i = 0; i < dots.length; i++) {
    const d = dots[i];

    let ent = 1;
    if (entProg < 1) {
      const lt = clamp01(
        (entProg - d.delay) / Math.max(0.001, 1 - d.delay)
      );
      const e = easeOutExpo(lt);
      d.x = d.sx + (d.tx - d.sx) * e;
      d.y = d.sy + (d.ty - d.sy) * e;
      ent = e;
    } else {
      d.x = d.tx;
      d.y = d.ty;
    }

    drawDot(ctx, d, time, hoverT, ent);
  }

  ctx.restore();
  animId = requestAnimationFrame(animate);
}

// ═══════════════════════════════════════════════════
//  Events
// ═══════════════════════════════════════════════════
function onMove(e) {
  const rect = canvasRef.value.getBoundingClientRect();
  mouse.x = e.clientX - rect.left - rect.width / 2;
  mouse.y = e.clientY - rect.top - rect.height / 2;
}

function onEnter() {
  hovering = true;
  mouse.active = true;
}

function onLeave() {
  hovering = false;
  mouse.active = false;
  mouse.x = mouse.y = -9999;
}

// ═══════════════════════════════════════════════════
//  Lifecycle
// ═══════════════════════════════════════════════════
onMounted(() => {
  createDots();
  const c = canvasRef.value;
  if (c) {
    c.addEventListener("mouseenter", onEnter);
    c.addEventListener("mouseleave", onLeave);
    c.addEventListener("mousemove", onMove);
  }
  animId = requestAnimationFrame(animate);
});

onBeforeUnmount(() => {
  if (animId) cancelAnimationFrame(animId);
  const c = canvasRef.value;
  if (c) {
    c.removeEventListener("mouseenter", onEnter);
    c.removeEventListener("mouseleave", onLeave);
    c.removeEventListener("mousemove", onMove);
  }
});
</script>

<template>
  <div class="preview-wrap">
    <canvas ref="canvasRef" class="canvas-preview"></canvas>
  </div>
</template>

<style scoped>
.preview-wrap {
  position: relative;
  transform: translateY(-16%);
}
.canvas-preview {
  display: block;
  border-radius: 12px;
  background: #000;
  width: 1200px;
  height: 600px;
}
</style>
