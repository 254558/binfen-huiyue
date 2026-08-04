# Kimi Doodle Rive 动画预览

kimi.com 对话框上方 doodle 动画的**离线**预览。动画是 Rive 格式（`.riv`），用 kimi 同款的官方运行时 `@rive-app/canvas` 2.32.0 本地播放，不依赖任何 CDN。

## 快速开始（推荐）

**双击 `rive-preview-standalone.html` 即可**——这是独立版：运行时、wasm、动画文件全部内嵌（约 2.2 MB），`file://` 下也能跑，完全离线。

> 更新动画文件后，用 `python3 build-standalone.py` 重新生成独立版。

或者用本地服务打开普通版：

```bash
python3 -m http.server 8765
```

打开 http://localhost:8765/rive-preview.html

> `rive-preview.html` 需要本地 HTTP 服务（Rive 运行时加载 `.wasm` 受 CORS 限制，直接双击 `file://` 打开不行，页面会显示提示）。

## 文件

| 文件 | 说明 |
|---|---|
| `rive-preview-standalone.html` | **双击即用**的独立版（内嵌全部资源，离线可用） |
| `rive-preview.html` | 普通版（需本地 HTTP 服务，体积小） |
| `build-standalone.py` | 生成独立版的构建脚本 |
| `kimi_linear_attention.riv` | 动画文件（源自 kimi.com 的 A/B 灰度资产） |
| `rive.min.js` / `rive.wasm` / `rive_fallback.wasm` | @rive-app/canvas 2.32.0 运行时（kimi 同款，本地离线） |

## 参数（URL 追加即可，可组合）

| 参数 | 作用 | 默认 |
|---|---|---|
| `?s=<倍率>` | 显示大小（相对设计分辨率 391×185） | 自适应：≤1000 宽（且不超过视口 92% 宽/78% 高） |
| `?ss=<倍率>` | 超采样倍数（越高边缘越锐，约线性提升清晰度） | 2 |
| `?file=xxx.riv` | 播放其他 Rive 文件 | `kimi_linear_attention.riv` |

示例：

- `?s=0.83` 模拟原站大小（325×154）
- `?s=1` 按设计分辨率 1:1 显示（最锐）
- `?ss=4` 4 倍超采样

## 动画结构

- artboard：`doodle`（设计分辨率 391×185）
- 动画：`dark`、`light`、`change color`、`keep change`
- 状态机：`State Machine 1`（`light/dark` 输入控制明暗主题，0=浅色 1=深色）
- 内嵌一张 2463×598 的 PNG 位图（Linear Attention 公式文字）

## 来源与版权

动画资产源自 kimi.com（https://www.kimi.com/）对话框上方 doodle（A/B 灰度资产），仅用于技术研究与学习。
