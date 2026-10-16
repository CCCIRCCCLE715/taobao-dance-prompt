# 舞蹈视频运镜提示词 Skill

给舞蹈视频写连续摄影路线：180°半环绕、俯视升降、大幅横移和推拉都要在单个镜头里发生。每镜说明开镜位置、中途路径和结束构图，同时保留舞步的承重、手臂路径、胸腰伸展与回收。

默认30秒、9:16，每镜不超过4秒。前10秒重点安排机位、高度和景别变化；全片保持原舞顺序、稳定节拍及同一场地的空间关系。人物、商品与场景描述保持简短，完整动作时间线予以保留。

## 使用

将仓库根目录作为 `taobao-dance-prompt` 技能文件夹，放入你的 Agent 支持的 skills 目录。入口文件为 [SKILL.md](SKILL.md)，详细镜头示例见 [camera-patterns.md](references/camera-patterns.md)。已有同名技能时请合并所需规则，保留本地配置。

可以这样提出任务：

> 分析这段舞蹈，写一份30秒视频提示词。动作充分伸展后利落回收，前10秒加入连续180°半环绕、俯视下降和大幅横移，每镜不超过4秒。人物与商品按上传图片引用，背景和光色保持连续。

需要实际提供参考视频或可核对的带时间抽帧。只有图片时可以设计编舞，但不能称为原视频的动作复刻。

## 检查提示词

镜头标题使用 `镜头1：`，后接 `【0—2秒】` 形式的动作时间段。Python脚本仅使用标准库：

```bash
python3 scripts/check_camera_timeline.py prompt.txt --duration 30
```

它检查时间覆盖、镜长、镜头编号、前段镜头密度和短脸部近景时长。实际镜内位移、环绕角度、舞步准确性与背景是否闪变，需要看生成视频才能判断。用户要求不同的前段镜头数时，可以用 `--opening-min-shots` 调整检查。

## 内容

- [SKILL.md](SKILL.md)：工作范围、动作记录、五段式提示词与交付规则。
- [camera-patterns.md](references/camera-patterns.md)：各类镜头的路线写法和可复用示例。
- [camera-motion-rhythm.md](references/camera-motion-rhythm.md)：前10秒、全局节奏、柔韧动作和背景连续性。
- [check_camera_timeline.py](scripts/check_camera_timeline.py)：文本时间轴检查。

镜头参数是可调整的创作目标，不保证任何生成模型都能准确执行。平台生成和外部发布由使用者另行授权配置。
