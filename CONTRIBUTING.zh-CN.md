# 参与贡献 game-mode-cleaner

感谢帮忙。请保持 Windows 上「双击就能用」的傻瓜路径。

## 底线

- **不要**在提交、Issue、样例里放密钥或真实账号。  
- Python 运行时依赖保持为零（除非有充分讨论）。  
- 不要加入真下单、券商适配、MiniQMT/`xtquant`。  
- 不要加入删盘、关 Defender、未公开内核清内存手法。  
- 优先预览/清理 `.bat` 体验和测试，而不是长文。  
- 文档写给**外部用户**：安装、用法、排除、安全——不要写求 star 话术。  

## 开发

```bash
git clone https://github.com/TheCleverJay/game-mode-cleaner.git
cd game-mode-cleaner
PYTHONPATH=src python3 tests/test_smoke.py
./scripts/smoke.sh
```

## Pull Request

1. 从 `main` 拉分支。  
2. 补测试（成功路径 + 边界）；Linux 上 `--source mock` 必须绿。  
3. 冒烟输出 `SMOKE_OK`。  
4. 用户可见改动写入 `CHANGELOG.md` 的 `[Unreleased]`。  
5. 中英文 README/docs 同步。  
6. 改干扰名单时更新 `src/game_mode_cleaner/data/catalog.json`（PS1 读同一份）。  

贡献即表示同意以 MIT 许可发布。
