<script setup>
/**
 * 缤纷辉月 · Rive 动画预览组件
 *
 * 播放 public/kimi_linear_attention.riv（源自 kimi.com doodle，Rive 格式），
 * 固定深色主题（状态机 light/dark 输入 = 1），支持 URL 参数：
 *   ?s=<倍率>  显示大小（相对设计分辨率 391×185），默认自适应
 *   ?ss=<倍率> 超采样倍数（越高边缘越锐），默认 2
 */
import { onBeforeUnmount, onMounted, ref } from "vue";
import { Rive, RuntimeLoader } from "@rive-app/canvas";
// 显式指定 wasm 路径：Vite 下用 ?url 拿到的 URL，dev / build 都能正确加载
import riveWasmUrl from "@rive-app/canvas/rive.wasm?url";

const canvasRef = ref(null);
let rive = null;
let destroyed = false;

/** 状态机 light/dark 输入，固定为深色主题 */
function setDarkTheme(instance) {
  const sm = (instance.stateMachineNames || [])[0];
  if (!sm) return;
  const inputs = instance.stateMachineInputs(sm);
  for (const input of inputs) {
    if (input.name === "light/dark") input.value = 1; // 0 = 浅色，1 = 深色
  }
}

/** 超采样缓冲：canvas.width/height = CSS 尺寸 × dpr × ss */
function applySharpness(instance, sharp) {
  if (!sharp) return;
  instance.resizeDrawingSurfaceToCanvas((window.devicePixelRatio || 1) * sharp.ss);
}

/** 等 artboard 就绪后：选第一个状态机播放、定深色主题、按 s/ss 定尺寸 */
function playAfterReady(instance) {
  const canvas = canvasRef.value;
  if (!canvas) return;
  let tries = 0;
  const timer = setInterval(() => {
    tries++;
    const art = instance.artboard;
    if (art || tries > 60) {
      clearInterval(timer);
      const machines = instance.stateMachineNames || [];
      const anims = instance.animationNames || [];
      if (art) {
        if (machines.length > 0) instance.play(machines[0]);
        else if (anims.length > 0) instance.play(anims[0]);
        setDarkTheme(instance);

        const qs = new URLSearchParams(location.search);
        let s = parseFloat(qs.get("s"));
        if (!(s > 0)) {
          // 默认：尽量大，方便分享展示（≤1200 宽，且不超过视口的 94% 宽 / 85% 高）
          const vw = window.innerWidth || 1280;
          const vh = window.innerHeight || 720;
          const targetW = Math.min(
            1200,
            vw * 0.94,
            vh * 0.85 * (instance.artboardWidth / instance.artboardHeight)
          );
          s = targetW / instance.artboardWidth;
        }
        let ss = parseFloat(qs.get("ss"));
        if (!(ss >= 1)) ss = 2;

        const displayW = Math.round(instance.artboardWidth * s);
        const displayH = Math.round(instance.artboardHeight * s);
        canvas.style.width = `${displayW}px`;
        canvas.style.height = `${displayH}px`;

        const sharp = { s, ss, displayW, displayH };
        applySharpness(instance, sharp);
        // 运行时内部监听 canvas 尺寸变化会按 dpr 重建缓冲，可能覆盖超采样；延迟重放确保生效
        setTimeout(() => {
          if (!destroyed) applySharpness(instance, sharp);
        }, 80);
        setTimeout(() => {
          if (!destroyed) applySharpness(instance, sharp);
        }, 400);
      }
    }
  }, 500);
}

onMounted(() => {
  const canvas = canvasRef.value;
  RuntimeLoader.setWasmUrl(riveWasmUrl);
  rive = new Rive({
    src: "/kimi_linear_attention.riv",
    canvas,
    autoplay: true,
    stateMachines: "State Machine 1",
    onLoad: () => playAfterReady(rive),
    onError: (e) => console.error("Rive 加载失败", e),
  });
});

onBeforeUnmount(() => {
  destroyed = true;
  rive?.cleanup();
});
</script>

<template>
  <canvas ref="canvasRef" width="800" height="400" class="rive-preview"></canvas>
</template>

<style scoped>
.rive-preview {
  border-radius: 12px;
  background: #000;
  /* 动画内容在 artboard 内偏下约 16%（实测 3 帧稳定），上移使其视觉居中 */
  transform: translateY(-16%);
}
</style>
