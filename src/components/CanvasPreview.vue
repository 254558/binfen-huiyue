<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

const canvasRef = ref(null);
let animationId = null;
let dots = [];
let time = 0;
let isHovering = false;
let hoverTransition = 0;

// 点与点之间的间距（同时影响点的大小，因为 baseRadius 是它的倍数）
const DOT_SPACING = 26;
// 四个方块之间的间距
const BLOCK_GAP = 50;
// 每个方块的行数
const ROWS = 7;
// 每个方块的列数
const COLS = 7;
// 方块数量（kimi 四个字母）
const NUM_BLOCKS = 4;

const GRAYS = [
  "#ffffff", "#f0f0f0", "#e8e8e8", "#e0e0e0", "#d8d8d8",
  "#d0d0d0", "#c8c8c8", "#c0c0c0", "#b8b8b8", "#b0b0b0",
  "#a8a8a8", "#a0a0a0", "#989898", "#909090", "#888888",
  "#808080", "#787878", "#707070", "#686868", "#606060",
  "#585858", "#505050", "#484848", "#404040", "#383838",
  "#303030", "#282828", "#202020", "#181818", "#101010"
];

const ACCENTS = ["#5b9bd5", "#70c070", "#d07070", "#9070b0", "#d070b0"];

// "kimi" 字母在 7×7 网格中的形状 (1=字母部分，0=背景)
const LETTER_PATTERNS = [
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

function createDots() {
  dots = [];
  let offsetX = 0;
  let accentIdx = 0;

  for (let block = 0; block < NUM_BLOCKS; block++) {
    const accentR = Math.floor(Math.random() * ROWS);
    const accentC = Math.floor(Math.random() * COLS);
    const pattern = LETTER_PATTERNS[block];

    const centerR = (ROWS - 1) / 2;
    const centerC = (COLS - 1) / 2;
    const maxDist = Math.sqrt(centerR * centerR + centerC * centerC);

    for (let row = 0; row < ROWS; row++) {
      for (let col = 0; col < COLS; col++) {
        const dr = row - centerR;
        const dc = col - centerC;
        const dist = Math.sqrt(dr * dr + dc * dc) / maxDist;

        // 鱼眼畸变：点的大小衰减系数，值越大边缘点越小（0~1）
        const sizeFactor = 1 - dist * 0.7;
        // 鱼眼畸变：位置向中心收缩系数，值越大边缘越内收、弧形越明显（0~1）
        const shrinkFactor = 1 - dist * 0.25;
        const x = offsetX + (col - centerC) * DOT_SPACING * shrinkFactor + centerC * DOT_SPACING;
        const y = (row - centerR) * DOT_SPACING * shrinkFactor + centerR * DOT_SPACING;

        let color;
        if (row === accentR && col === accentC) {
          color = ACCENTS[accentIdx % ACCENTS.length];
          accentIdx++;
        } else {
          const idx = Math.floor(Math.pow(Math.random(), 0.7) * GRAYS.length);
          color = GRAYS[idx];
        }

        dots.push({
          x,
          y,
          color,
          row,
          col,
          block,
          isLetterDot: pattern[row][col] === 1,
          phase: Math.random() * Math.PI * 2,
          // 点的基础半径：DOT_SPACING 的倍数，值越大点越大
          baseRadius: DOT_SPACING * 0.38 * sizeFactor,
        });
      }
    }

    offsetX += COLS * DOT_SPACING + BLOCK_GAP;
  }

  const totalWidth = offsetX - BLOCK_GAP;
  const centerX = -totalWidth / 2;
  dots.forEach((dot) => {
    dot.x += centerX;
  });
}

function drawDot(ctx, dot, t) {
  const pulse = Math.sin(t * 1.2 + dot.phase);
  const minRadius = dot.baseRadius * 0.6;
  const normalRadius = Math.max(minRadius, dot.baseRadius * (0.7 + 0.3 * pulse));

  const r = parseInt(dot.color.slice(1, 3), 16);
  const g = parseInt(dot.color.slice(3, 5), 16);
  const b = parseInt(dot.color.slice(5, 7), 16);
  const minBright = 0x33;
  const normalR = Math.max(r, minBright);
  const normalG = Math.max(g, minBright);
  const normalB = Math.max(b, minBright);

  const hoverRadius = dot.baseRadius * 1.1;
  const hoverTargetR = dot.isLetterDot ? 0xf0 : 0x40;
  const hoverTargetG = dot.isLetterDot ? 0xf0 : 0x40;
  const hoverTargetB = dot.isLetterDot ? 0xf0 : 0x40;
  const hoverAlpha = dot.isLetterDot ? 1.0 : 0.5;

  const ht = hoverTransition;
  const radius = normalRadius + (hoverRadius - normalRadius) * ht;
  const cr = Math.floor(normalR + (hoverTargetR - normalR) * ht);
  const cg = Math.floor(normalG + (hoverTargetG - normalG) * ht);
  const cb = Math.floor(normalB + (hoverTargetB - normalB) * ht);
  const normalAlpha = 0.7 + 0.3 * ((pulse + 1) / 2);
  const alpha = normalAlpha + (hoverAlpha - normalAlpha) * ht;

  // 绘制圆角矩形（边长 = radius * 2）
  const size = radius * 2;
  // 圆角半径系数，0=直角矩形，1=圆形，0.8 接近圆形
  const cornerRadius = radius * 0.8;
  const halfSize = radius;

  ctx.beginPath();
  ctx.moveTo(dot.x - halfSize + cornerRadius, dot.y - halfSize);
  ctx.lineTo(dot.x + halfSize - cornerRadius, dot.y - halfSize);
  ctx.arcTo(dot.x + halfSize, dot.y - halfSize, dot.x + halfSize, dot.y - halfSize + cornerRadius, cornerRadius);
  ctx.lineTo(dot.x + halfSize, dot.y + halfSize - cornerRadius);
  ctx.arcTo(dot.x + halfSize, dot.y + halfSize, dot.x + halfSize - cornerRadius, dot.y + halfSize, cornerRadius);
  ctx.lineTo(dot.x - halfSize + cornerRadius, dot.y + halfSize);
  ctx.arcTo(dot.x - halfSize, dot.y + halfSize, dot.x - halfSize, dot.y + halfSize - cornerRadius, cornerRadius);
  ctx.lineTo(dot.x - halfSize, dot.y - halfSize + cornerRadius);
  ctx.arcTo(dot.x - halfSize, dot.y - halfSize, dot.x - halfSize + cornerRadius, dot.y - halfSize, cornerRadius);
  ctx.closePath();

  ctx.fillStyle = `rgb(${cr},${cg},${cb})`;
  ctx.globalAlpha = alpha;
  ctx.fill();
  ctx.globalAlpha = 1;
}

function animate() {
  const canvas = canvasRef.value;
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;

  canvas.width = w * dpr;
  canvas.height = h * dpr;
  ctx.scale(dpr, dpr);

  ctx.fillStyle = "#000000";
  ctx.fillRect(0, 0, w, h);

  // 平滑过渡 hover 状态（系数越小过渡越慢越柔和）
  const targetHover = isHovering ? 1 : 0;
  hoverTransition += (targetHover - hoverTransition) * 0.04;

  ctx.save();
  ctx.translate(w / 2, h / 2);
  dots.forEach((dot) => drawDot(ctx, dot, time));
  ctx.restore();

  time += 0.016;
  animationId = requestAnimationFrame(animate);
}

function handleMouseEnter() {
  isHovering = true;
}

function handleMouseLeave() {
  isHovering = false;
}

onMounted(() => {
  createDots();
  animate();

  const canvas = canvasRef.value;
  if (canvas) {
    canvas.addEventListener("mouseenter", handleMouseEnter);
    canvas.addEventListener("mouseleave", handleMouseLeave);
  }
});

onBeforeUnmount(() => {
  if (animationId) cancelAnimationFrame(animationId);
  const canvas = canvasRef.value;
  if (canvas) {
    canvas.removeEventListener("mouseenter", handleMouseEnter);
    canvas.removeEventListener("mouseleave", handleMouseLeave);
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
