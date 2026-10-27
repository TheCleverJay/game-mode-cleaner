# 排除名单教程

目标：告诉清理工具「这些程序不要关」。

## 文件在哪？

仓库根目录的 `exclusions.txt`。用记事本打开即可。  
也可以复制 `examples/exclusions.example.txt` 再改名。

## 怎么写？

- **一行一个**进程名  
- `#` 后面是注释  
- 可写 `Discord.exe` 或 `Discord`  
- 路径会自动取最后一段文件名  

示例：

```
# 语音要留着
Discord.exe

# 还要查攻略
chrome.exe

# 游戏本体（一般不在干扰名单；误伤时加上）
HollowKnight.exe
```

## 怎么查进程名？

1. `Ctrl+Shift+Esc` 打开任务管理器  
2. 切到 **详细信息**  
3. 看 **名称** 列，原样抄进 `exclusions.txt`  
4. 保存文件  
5. 再双击 `GameMode-Preview.bat` 确认名单里已没有它  

## 和「永不杀」的关系

工具内置一份硬编码永不杀列表（系统关键、杀毒核心等）。  
你的排除名单会与它**合并**：两边只要有一边保护，就不会关。

## 命令行等价写法

```bash
game-mode-cleaner --source mock --exclude-file exclusions.txt --exclude notepad.exe
```

PowerShell：

```powershell
.\scripts\GameModeCleaner.ps1 -ExcludeFile .\exclusions.txt -Exclude notepad.exe
```
