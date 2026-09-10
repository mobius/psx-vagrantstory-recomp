# PCSX-Redux 对照接入
已下载固定源码 3a38cb4657daf594915c6e97d7847d95a4935ad5，尚未构建或启动模拟器。
源码 src/core/web-server.cc 确认以下接口可用于后续本地对照：
- GET /api/v1/execution-flow：读取是否运行。
- POST /api/v1/execution-flow?function=pause 或 resume：暂停/恢复。
- /api/v1/cpu/ram/raw：读取原机内存。
- /api/v1/gpu/vram/raw：读取显存。
main.cc 支持 --webserver 和 --webserver-port。
后续针对 TITLE/TITLE.PRG、BATTLE/BATTLE.PRG 加载前后保存内存，与重编译运行库调度入口和画面比较。
当前只验证了源码接口存在，未宣称完成动态对照。
