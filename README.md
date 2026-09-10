# Vagrant Story Recomp

美版 **SLUS-01040** 的 Windows x64 重编译研究项目。使用 PSXRecomp 转换原程序，以 rood-reverse 的同版本地址/区段资料补齐入口，并用 PCSX-Redux 做参考采集。

**当前是可运行的实验原型，不是已完成的完整移植。** 已验证 New Game、角色移动/跳跃、摄像机、主菜单、地图、操作手册和进入 Worker’s Breakroom。仍有解释执行回退；敌人战斗、游戏存档写入后重载、音频和完整流程未验收。详见 [STATUS.md](STATUS.md)。

仓库只包含项目代码、配置、地址种子和文档，不包含游戏镜像、BIOS、转换后的游戏代码、可执行文件或存档。

## 构建

已验证环境：Windows x64、GCC 13.2、Python 3.13。需要已有的 Git、uv 和 MinGW-w64 GCC/G++。Python、CMake、Ninja、PyYAML 安装在项目环境，不执行全局安装。

```powershell
git clone https://github.com/mobius/psx-vagrantstory-recomp.git
cd psx-vagrantstory-recomp
./tools/bootstrap.ps1
```

bootstrap 初始化根级子模块并创建 `.venv`。不需要框架内可选的联网/倒带子模块。GCC 须在 PATH 中；便携工具链可用 `PSXRECOMP_GCC` 环境变量指定 gcc.exe 的完整路径。

将自己提供的游戏 ZIP 解压，保留 CUE 和 BIN 相邻，再验证输入：

```powershell
./tools/prepare-inputs.ps1 -Disc 'D:/dumps/Vagrant Story (USA).cue' -Bios 'D:/dumps/SCPH1001.BIN'
./tools/build.ps1
./tools/build-aot.ps1
./tools/run.ps1
```

当前只接受以下已验证输入，摘要不匹配会停止：

| 输入 | 摘要 |
| --- | --- |
| USA BIN，750643152 字节，单轨 MODE2/2352 | SHA1 `38c63db6c49a06b91d87cd5a4e31b1ec68fe212c` |
| SCPH1001.BIN，524288 字节 | SHA256 `71af94d1e47a68c11e8fdb9f8368040601514a42a5a399cda48c7d3bff1e99d3` |

build.ps1 生成主程序/BIOS C 并构建运行程序；build-aot.ps1 另外处理 20 个非空 PRG、BIOS 常驻代码及有实际执行证据的中部入口。转换代码和本机代码缓存均留在忽略目录。

## 目录与工具

| 路径 | 用途 |
| --- | --- |
| `game.toml`, `CMakeLists.txt`, `seeds/` | 身份、构建配置、入口及其来源 |
| `psxrecomp/`, `references/` | 固定版本子模块；[依赖与许可](THIRD_PARTY.md) |
| `tools/bootstrap.ps1`, `prepare-inputs.ps1` | 本地环境和自备输入准备 |
| `tools/build*.ps1`, `compile-*.ps1`, `run.ps1` | 构建、增量编译和启动 |
| `tools/*probe*.py`, `input_action.py`, `room_state.py` | 开发诊断，不是通关脚本 |
| `docs/research`, `docs/plan`, `docs/impl`, `docs/architecture` | 带时间戳的迭代记录 |
| `local/`, `generated/`, `build/` | 不提交的输入、代码、二进制、截图、捕获和存档 |

地址和布局依赖当前美版及子模块版本。更新依赖后需重新生成缓存。navigate_door.py 只验证过单出口的第一房间，不适用于任意房间。

开发构建启用仅回环监听的 PSXRecomp 诊断服务。probe_new_game.py 在加速标题超时前发送正常 Start 输入；`--keep` 会保留进程，PID 写入本地结果目录。普通启动不自动操作角色。

## 验证与提交检查

```powershell
.venv/Scripts/python.exe tools/test_prg_map.py
.venv/Scripts/python.exe tools/audit_staged.py --self-test
# git add 后检查真正待提交的内容：
.venv/Scripts/python.exe tools/audit_staged.py
git diff --cached --check
```

类似工作：[rood-reverse](https://github.com/ser-pounce/rood-reverse) 是本游戏匹配反编译；[另一原生移植作者的报告](https://www.reddit.com/r/VagrantStory/comments/1v5rm74/personal_project_running_vagrant_story_natively/) 在发帖时称仓库仍为私有。本项目未将其报告视作自己的验证结果。
