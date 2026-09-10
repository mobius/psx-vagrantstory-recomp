# 上游与版本

| 项目 | 用途 | 固定提交 | 许可文件 |
| --- | --- | --- | --- |
| [PSXRecomp](https://github.com/mstan/psxrecomp) | 重编译器及运行时 | `ed55299be34710a90fc080484a83e8634bd41fa9` | `psxrecomp/LICENSE`：PolyForm Noncommercial 1.0.0 |
| [rood-reverse](https://github.com/ser-pounce/rood-reverse) | 同版本文件摘要、地址及区段研究 | `714e647a94a75d2412b6f66a055a223dcae8b373` | `references/rood-reverse/LICENSE`：CC0 1.0 |
| [PCSX-Redux](https://github.com/grumpycoders/pcsx-redux) | 调试接口研究与运行对照 | `3a38cb4657daf594915c6e97d7847d95a4935ad5` | `references/pcsx-redux/LICENSE` 及源码头：GPL-2.0-or-later |

Git 子模块记录以上固定版本。框架所用 SDL、fmt、OpenBIOS 等依赖的说明保留在上游仓库及产物中；本项目不重新授权这些依赖。

实际 PCSX-Redux 参考采集使用官方下载的便携 CLI `25316.20260909.6.x64`，提交 `954677b50a0d1d8485f894c3778c38d6e3a4bf1a`。包清单和下载摘要只保存在本地，未纳入二进制。

本项目新增脚本暂未单独指定许可证。游戏内容与零售 BIOS 不属于上述源码许可范围，均不随仓库提供。
