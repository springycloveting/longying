# 龙胤立志传 - Web 存档修改器（Rust 版）

用 Rust 重构 `web_server.py`（Flask）的存档修改器后端，产物为**单文件绿色版 exe**：
前端页面与技能/天赋/标签映射数据全部**压缩内嵌**进可执行文件，不依赖任何外部文件。

## 特性

- 单文件绿色版：`cargo build --release` 产物约 **557KB**（<800KB 目标）
- 前端（index.html / world.html）+ 4 个数据映射 JSON 全部内嵌（deflate 压缩，运行时解压）
- 功能与原 Python 版 1:1 对齐：角色存档全部修改 + Save 世界存档（区域/势力/资源点/监狱/府库/解锁/天气等）
- 默认自动检测游戏存档目录（Steam `LongYinLiZhiZhuan_Data\Save`），按 `SaveSlot0~10` 槽位加载
- 支持 `--port` 指定端口（默认 5000）
- 无 Python 运行环境依赖，仅依赖 serde_json

## 构建

```bash
cargo build --release
# 产物: target/release/web_server.exe
```

尺寸优化配置见 `Cargo.toml`（opt-level=z / lto=fat / codegen-units=1 / panic=abort / strip=symbols）。
资源在 `build.rs` 中编译期压缩，`src/main.rs` 运行时解压。

## 使用

1. 双击 `web_server.exe`，浏览器自动打开 `http://localhost:5000`
2. 页面下拉框选择存档槽位（SaveSlot0~10）→ 加载
3. 修改 → 保存（自动生成 `.backup_时间戳` 备份）

## 目录

```
rust_doubao/
├── Cargo.toml          # 构建配置（尺寸优化）
├── build.rs            # 编译期压缩内嵌资源
├── src/main.rs         # 单文件实现（HTTP 服务器 + 全部 API）
└── assets/             # 内嵌资源源文件（前端 + JSON 映射）
```