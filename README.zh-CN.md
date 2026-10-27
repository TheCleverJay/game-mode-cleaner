# game-mode-cleaner · 游戏模式一键清理

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](./pyproject.toml)

开游戏前，把占用内存/CPU 的后台干扰项先安静掉。默认只**预览**，不会真关程序。可自定义排除名单。

- 中文 · [English](./README.md)
- 许可：MIT · 主要支持：**Windows**（双击 `.bat` 即可）· Linux 为次要辅助
- 仓库：[`YuanAqi/game-mode-cleaner`](https://github.com/YuanAqi/game-mode-cleaner)

---

## 三步走（推荐，不用懂代码）

1. **下载**本仓库，解压到任意文件夹。  
2. **（可选）改排除名单**：用记事本打开同目录的 `exclusions.txt`，**把不想关的程序名加进这个文件**（一行一个，例如 `Discord.exe`）。`#` 开头是注释。  
3. **双击运行**  
   - `GameMode-Preview.bat` → **只预览**会动到谁（安全，默认推荐先点这个）  
   - `GameMode-Apply.bat` → 真正清理；会先问你输入 `Y` 才继续  

做完后，从开始菜单重新打开还需要的软件即可。

> 诚实说明：这是给低配电脑减少后台抢资源的便利工具，**不保证**任何游戏跑到 60 帧。

---

## 排除名单怎么写？

文件：`exclusions.txt`（仓库根目录，已带中文说明）

```
# 一行一个进程名
Discord.exe
chrome.exe
mygame.exe
```

- 任务管理器 → **详细信息** → 看「名称」列，把名字抄进来。  
- 可写 `Discord` 或 `Discord.exe`，都行。  
- 系统关键进程（如 `csrss`、`lsass`、杀毒核心等）写不写都会被保护，关不掉。  

更细的说明：[docs/zh/exclusions.md](./docs/zh/exclusions.md)

---

## 会动什么？不会动什么？

| 会考虑关掉（在干扰名单里且未排除） | 永远不会动 |
|---|---|
| 后台浏览器、云同步、RGB 灯控、部分更新器、语音/聊天客户端等（见预设） | 系统关键进程、资源管理器（默认）、Windows 安全中心核心等硬编码「永不杀」列表 |

预设：

- `light`（默认）：常见占内存的干扰项  
- `aggressive`：范围更广（仍尊重永不杀 + 你的排除）  
- `custom`：只处理你在目标名单里写的名字  

预览默认；只有 Apply / `--apply` 才会真正结束进程。本工具**不做**未公开内核清理、**不**永久关闭 Windows Defender、**不**删你的文件。

---

## 进阶：命令行（可选）

装了 Python ≥ 3.10 时：

```bash
pip install -e .
game-mode-cleaner --help

# 用内置假进程表做预览（Linux / CI 也能跑）
PYTHONPATH=src python3 -m game_mode_cleaner.cli --source mock --lang zh

# 指定排除文件
PYTHONPATH=src python3 -m game_mode_cleaner.cli --source mock --exclude-file exclusions.txt
```

Windows 上更推荐 PowerShell：

```powershell
.\scripts\GameModeCleaner.ps1
.\scripts\GameModeCleaner.ps1 -Apply -Lang zh
.\scripts\GameModeCleaner.ps1 -Preset aggressive -ExcludeFile .\exclusions.txt
```

---

## 文档

- [docs/zh/exclusions.md](./docs/zh/exclusions.md) — 排除名单教程  
- [docs/zh/safety.md](./docs/zh/safety.md) — 安全与限制  
- [docs/en/exclusions.md](./docs/en/exclusions.md) · [docs/en/safety.md](./docs/en/safety.md)

## 参与贡献 / 安全

[CONTRIBUTING.zh-CN.md](./CONTRIBUTING.zh-CN.md) · [CONTRIBUTING.md](./CONTRIBUTING.md)  
[SECURITY.md](./SECURITY.md) · [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) · [CHANGELOG.md](./CHANGELOG.md)

## 明确不会做的事

不删盘、不勒索、不写恶意注册表、不永久关掉 Defender、不含交易/券商/MiniQMT 代码、不夸大帧数收益。
