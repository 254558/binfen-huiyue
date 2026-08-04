# 缤纷辉月 · Kimi Doodle Rive 动画预览

> 动画名：**缤纷辉月**——色彩缤纷 × 辉月，呼应 Moonshot 登月意象。
> 仓库名用拼音 `binfen-huiyue`（GitHub 仓库名仅支持英文/数字/连字符，不支持中文）。

kimi.com 对话框上方的 doodle 动画，是 **Rive** 制作的（`.riv` 矢量动画格式）。本仓库是它的 **Vue 3 + Vite** 版离线预览：用 Kimi 同款的官方运行时 `@rive-app/canvas` 2.32.0 播放，深色主题，资源本地托管。

## 它是 Rive 做的

- **动画文件**：`public/kimi_linear_attention.riv` —— Rive 编辑器（[editor.rive.app](https://editor.rive.app)）制作的标准 `.riv` 文件
- **播放引擎**：Rive 官方 Web 运行时（JavaScript + WebAssembly），通过 npm 包 `@rive-app/canvas` 集成
- **想改动画**：用 Rive 编辑器打开 `.riv` 直接编辑，无需碰代码

## 快速开始

```bash
npm install
npm run dev      # 开发预览（http://localhost:5173）
npm run build    # 生产构建（输出到 dist/）
npm run preview  # 本地预览构建产物
```

## 文件结构

| 路径 | 说明 |
|---|---|
| `src/App.vue` | 页面布局（黑底居中舞台） |
| `src/components/RivePreview.vue` | 核心组件：创建 Rive 实例、播放、深色主题、`s/ss` 参数与超采样 |
| `public/kimi_linear_attention.riv` | 动画源文件（Rive 格式，源自 kimi.com 的 A/B 灰度资产） |

## 播放参数（URL 追加，可组合）

| 参数 | 作用 | 默认 |
|---|---|---|
| `?s=<倍率>` | 显示大小（相对设计分辨率 391×185） | 自适应：≤1200 宽（且不超过视口 94% 宽 / 85% 高） |
| `?ss=<倍率>` | 超采样倍数（越高边缘越锐） | 2 |

示例：

- `?s=0.83` 模拟原站大小（325×154）
- `?s=1` 按设计分辨率 1:1 显示（最锐）
- `?ss=4` 4 倍超采样

## 怎么用到你自己的网页里

### 方式一：npm 集成（推荐，本仓库即这种方式）

```bash
npm install @rive-app/canvas@2.32.0
```

```js
import { Rive, RuntimeLoader } from "@rive-app/canvas";
import riveWasmUrl from "@rive-app/canvas/rive.wasm?url";

RuntimeLoader.setWasmUrl(riveWasmUrl); // Vite 下需显式指定 wasm 路径

const r = new Rive({
  src: "/kimi_linear_attention.riv",
  canvas: document.getElementById("rive-canvas"),
  autoplay: true,
  stateMachines: "State Machine 1",
});
```

> 注意：`RuntimeLoader` 是独立导出的类，不是 `Rive` 的静态属性（`Rive.RuntimeLoader` 为 `undefined`）。

## 动画结构

- artboard：`doodle`（设计分辨率 391×185）
- 动画：`dark`、`light`、`change color`、`keep change`
- 状态机：`State Machine 1`（`light/dark` 输入控制明暗主题，本预览固定深色）
- 内嵌一张 2463×598 的 PNG 位图（Linear Attention 公式文字）

## 来源与版权

动画资产源自 kimi.com（https://www.kimi.com/）对话框上方 doodle（A/B 灰度资产），仅用于技术研究与学习。
