# 缤纷辉月 · Kimi Doodle Rive 动画预览

> 动画名：**缤纷辉月**——色彩缤纷 × 辉月，呼应 Moonshot 登月意象。
> 仓库名用拼音 `binfen-huiyue`（GitHub 仓库名仅支持英文/数字/连字符，不支持中文）。

kimi.com 对话框上方的 doodle 动画，是 **Rive** 制作的（`.riv` 矢量动画格式）。本仓库提供它的离线预览，用 Kimi 同款的官方运行时 `@rive-app/canvas` 2.32.0 播放，不依赖任何 CDN。

## 它是 Rive 做的

- **动画文件**：`kimi_linear_attention.riv` —— Rive 编辑器（[editor.rive.app](https://editor.rive.app)）制作的标准 `.riv` 文件
- **播放引擎**：Rive 官方 Web 运行时（JavaScript + WebAssembly）
- **想改动画**：用 Rive 编辑器打开 `.riv` 直接编辑，无需碰代码

## 快速开始

**双击 `rive-preview-standalone.html`** —— 运行时、wasm、动画全部内嵌（约 2.2 MB），完全离线，无需服务器。

> 想重新生成独立版：`python3 build-standalone.py`（它读入 `rive.min.js` / `rive.wasm` / `.riv` 打包进模板，需要时先恢复这三个源文件）。

## 怎么用到你自己的网页里

### 方式一：iframe 嵌入（最简单）

把 `rive-preview-standalone.html` 传到你的服务器或对象存储，然后：

```html
<iframe
  src="rive-preview-standalone.html"
  style="border:0;width:800px;height:420px;background:#000"
></iframe>
```

### 方式二：官方运行时 + .riv（正规做法）

```html
<canvas id="rive-canvas" width="800" height="400"></canvas>

<script src="https://unpkg.com/@rive-app/canvas@2.32.0"></script>
<script>
  const r = new rive.Rive({
    src: "kimi_linear_attention.riv", // 你的 .riv 文件，需与页面同域
    canvas: document.getElementById("rive-canvas"),
    autoplay: true,
    stateMachines: "State Machine 1", // 状态机，控制明暗主题
  });
</script>
```

要点：

- `.riv` 通过 fetch 加载，受 CORS 限制，必须和页面同域（或给服务端配 CORS 头）
- 本地调试需起 HTTP 服务（`python3 -m http.server 8765`），直接双击 `file://` 打开不行
- 如果 wasm 加载失败（本地托管时常见），显式指定路径：

  ```js
  rive.RuntimeLoader.setWasmUrl("/rive.wasm"); // 放在调用 Rive() 之前
  ```

- 状态机里有 `light/dark` 输入，可动态切换明暗主题：

  ```js
  const inputs = r.stateMachineInputs("State Machine 1");
  inputs[0].value = 1; // 0 = 浅色，1 = 深色
  ```

### 方式三：npm 集成

```bash
npm install @rive-app/canvas@2.32.0
```

```js
import { Rive } from "@rive-app/canvas";

const r = new Rive({
  src: "/kimi_linear_attention.riv",
  canvas: document.getElementById("rive-canvas"),
  autoplay: true,
  stateMachines: "State Machine 1",
});
```

## 文件

| 文件 | 说明 |
|---|---|
| `rive-preview-standalone.html` | **双击即用**的独立版（内嵌全部资源，离线可用） |
| `kimi_linear_attention.riv` | 动画源文件（Rive 格式，源自 kimi.com 的 A/B 灰度资产） |
| `build-standalone.py` | 生成独立版的构建脚本（一次性打包工具） |

## 播放参数（URL 追加，可组合）

| 参数 | 作用 | 默认 |
|---|---|---|
| `?s=<倍率>` | 显示大小（相对设计分辨率 391×185） | 自适应：≤1200 宽（且不超过视口 94% 宽 / 85% 高） |
| `?ss=<倍率>` | 超采样倍数（越高边缘越锐） | 2 |

示例：

- `?s=0.83` 模拟原站大小（325×154）
- `?s=1` 按设计分辨率 1:1 显示（最锐）
- `?ss=4` 4 倍超采样

## 动画结构

- artboard：`doodle`（设计分辨率 391×185）
- 动画：`dark`、`light`、`change color`、`keep change`
- 状态机：`State Machine 1`（`light/dark` 输入控制明暗主题）
- 内嵌一张 2463×598 的 PNG 位图（Linear Attention 公式文字）

## 来源与版权

动画资产源自 kimi.com（https://www.kimi.com/）对话框上方 doodle（A/B 灰度资产），仅用于技术研究与学习。
