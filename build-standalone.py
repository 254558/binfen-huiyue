#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 rive-preview-standalone.html —— 完全自包含的预览页：
把 rive.min.js（运行时）、rive.wasm、kimi_linear_attention.riv 全部 base64 内嵌，
双击即可打开（file:// 协议下也能跑，不依赖本地 HTTP 服务）。

用法：python3 build-standalone.py
"""
import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Kimi Doodle Rive 动画预览（独立版）</title>
<style>
  body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    background: #000;
    color: #f5f5f5;
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  }
  canvas {
    border-radius: 12px;
    background: #000;
    /* 动画内容在 artboard 内偏下约 16%（实测 3 帧稳定），上移使其视觉居中 */
    transform: translateY(-16%);
  }
</style>
</head>
<body>
  <canvas id="rive-canvas" width="800" height="400"></canvas>

  <!-- @rive-app/canvas 2.32.0 运行时（内嵌，完全离线） -->
  <script>
/*__RIVE_JS__*/
  </script>
  <script>
    window.__riveState = { loaded: false, error: null, stateMachines: [], animationNames: [], pageErrors: [] };
    window.addEventListener('error', function (e) { window.__riveState.pageErrors.push('error: ' + (e && e.message)); });
    window.addEventListener('unhandledrejection', function (e) {
      window.__riveState.pageErrors.push('unhandledrejection: ' + (e && e.reason && e.reason.message ? e.reason.message : e.reason));
    });
    (function () {
      var orig = console.error;
      console.error = function () {
        window.__riveState.pageErrors.push('console.error: ' + Array.prototype.slice.call(arguments).map(function (a) { return a && a.message ? a.message : String(a); }).join(' '));
        orig.apply(console, arguments);
      };
    })();

    var riveInstance = null;

    function setTheme(mode) {
      if (!riveInstance) return;
      try {
        var sm = (riveInstance.stateMachineNames || [])[0];
        if (!sm) return;
        var inputs = riveInstance.stateMachineInputs(sm);
        for (var i = 0; i < inputs.length; i++) {
          if (inputs[i].name === "light/dark") { inputs[i].value = mode; }
        }
      } catch (e) { /* 忽略 */ }
    }

    // 超采样缓冲：canvas.width/height = CSS 尺寸 × dpr × ss（幂等）
    function applySharpness(rive) {
      try {
        var st = window.__riveState.sharp;
        if (!st) return;
        rive.resizeDrawingSurfaceToCanvas((window.devicePixelRatio || 1) * st.ss);
        window.__riveState.buffer = { w: rive.canvas.width, h: rive.canvas.height };
      } catch (e) {
        window.__riveState.resizeErr = String(e);
      }
    }

    function playAfterReady(rive) {
      var canvas = document.getElementById("rive-canvas");
      var tries = 0;
      var timer = setInterval(function () {
        tries++;
        var art = rive.artboard;
        if (art || tries > 60) {
          clearInterval(timer);
          var machines = rive.stateMachineNames || [];
          var anims = rive.animationNames || [];
          window.__riveState.stateMachines = machines;
          window.__riveState.animationNames = anims;
          if (art) {
            if (machines.length > 0) rive.play(machines[0]);
            else if (anims.length > 0) rive.play(anims[0]);
            setTheme(1); // 深色背景，默认深色主题
            window.__riveState.artboardSize = {
              w: rive.artboardWidth,
              h: rive.artboardHeight,
              dpr: window.devicePixelRatio,
            };
            var qs = new URLSearchParams(location.search);
            var s = parseFloat(qs.get("s"));
            if (!(s > 0)) {
              // 默认：尽量大，方便分享展示（≤1200 宽，且不超过视口的 94% 宽 / 85% 高）
              var vw = window.innerWidth || 1280;
              var vh = window.innerHeight || 720;
              var targetW = Math.min(1200, vw * 0.94, vh * 0.85 * (rive.artboardWidth / rive.artboardHeight));
              s = targetW / rive.artboardWidth;
            }
            var ss = parseFloat(qs.get("ss"));
            if (!(ss >= 1)) ss = 2;
            var displayW = Math.round(rive.artboardWidth * s);
            var displayH = Math.round(rive.artboardHeight * s);
            canvas.style.width = displayW + "px";
            canvas.style.height = displayH + "px";
            window.__riveState.sharp = { s: s, ss: ss, displayW: displayW, displayH: displayH };
            applySharpness(rive);
            // 运行时内部监听 canvas 尺寸变化会按 dpr 重建缓冲，可能覆盖超采样；延迟重放确保生效
            setTimeout(function () { applySharpness(rive); }, 80);
            setTimeout(function () { applySharpness(rive); }, 400);
          }
        }
      }, 500);
    }

    function init() {
      if (window.__riveState.loaded) return;
      var canvas = document.getElementById("rive-canvas");
      var RiveClass = window.Rive || (window.rive && window.rive.Rive);
      if (!RiveClass) { window.__riveState.error = "Rive 运行时未加载"; return; }
      // WASM 内嵌为 data URL：file:// 下 fetch(data:) 不受 CORS 限制
      try {
        var RL = window.rive.RuntimeLoader;
        if (RL && RL.setWasmUrl) RL.setWasmUrl("data:application/wasm;base64,/*__WASM_B64__*/");
      } catch (e) { window.__riveState.pageErrors.push('wasm url: ' + e); }
      // 动画字节内嵌为 base64，解码后以 ArrayBuffer 直接交给运行时（完全不走 fetch）
      var b64 = "/*__RIV_B64__*/";
      var u8;
      try {
        var bin = atob(b64);
        u8 = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
      } catch (e) {
        window.__riveState.error = "riv base64 解码失败: " + e;
        return;
      }
      var r = new RiveClass({
        canvas: canvas,
        buffer: u8.buffer,
        autoplay: true,
        onLoad: function () {
          // onLoad 回调参数是事件对象 {type, data}，必须用闭包里的实例
          window.__rive = r;
          riveInstance = r;
          onLoad(r);
        },
        onError: onError,
      });
      window.__rive = r;
    }

    function onLoad(rive) {
      window.__riveState.loaded = true;
      playAfterReady(rive);
    }

    function onError(e) {
      window.__riveState.error = String(e && e.message ? e.message : e);
    }

    window.addEventListener("load", function () {
      setTimeout(function () {
        if (typeof Rive !== "undefined" || (window.rive && window.rive.Rive)) init();
      }, 100);
    });
  </script>
</body>
</html>
"""


def main():
    rive_js = (ROOT / "rive.min.js").read_text(encoding="utf-8").replace("</script>", "<\\/script>")
    wasm_b64 = base64.b64encode((ROOT / "rive.wasm").read_bytes()).decode("ascii")
    riv_b64 = base64.b64encode((ROOT / "kimi_linear_attention.riv").read_bytes()).decode("ascii")
    html = (
        TEMPLATE
        .replace("/*__RIVE_JS__*/", rive_js)
        .replace("/*__WASM_B64__*/", wasm_b64)
        .replace("/*__RIV_B64__*/", riv_b64)
    )
    out = ROOT / "rive-preview-standalone.html"
    out.write_text(html, encoding="utf-8")
    print("已生成 %s（%.2f MB）" % (out.name, len(html) / 1024 / 1024))


if __name__ == "__main__":
    main()
