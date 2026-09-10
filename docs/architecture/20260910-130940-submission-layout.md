# 提交目录与私有产物

根目录只保留可复现源码和配置。三个Git子模块固定上游版本；外部许可保留在各上游，不将PSXRecomp误标为MIT。

local/bios 与 local/disc：用户自备输入。generated 与 build：生成代码和构建树。local/newgame-probe：玩法测试截图、计数、卡文件与快照。local/artifacts：本地构建包和校验清单，不上传。

build.ps1负责主程序，build-aot.ps1负责全PRG及已观察的入口补齐，run.ps1使用统一的本地BIOS和可选测试存档目录。GCC通过PATH或PSXRECOMP_GCC解析；uv缓存和Python安装目录均限制到项目local目录。

audit_staged.py扫描Git索引中的实际blob，拒绝私有目录、二进制/媒体、凭证模式和个人绝对路径。子模块只允许已知的三个gitlink。该扫描是提交检查的一部分，不是对任意敏感信息的完整检测保证。
