# 运行验证与覆盖层
Release 与启用调试接口的 Windows 原型均构建成功，产物 build/runtime/Vagrant_Story_Recompiled.exe。
限时运行已取得 320x224 的片头、实时演出和对白截图（local/ 下）。调试返回 frame=3360；后续独立会话达到 frame=34110，画面持续变化。
上游 TCP 接口一连接一命令，测试工具已修正。quit 命令可能在回复前 shutdown/join 导致 busy 响应；测试改为由父进程终止，不将终止退出码当游戏故障。
开启 overlay_cache 捕获动态代码。第一次离线编译 built OK=4、skipped=12、FAILED=0。运行时重扫后 loads=3、registered=53、dispatch_native=1173；解释回退计数仍很大，绝非完整纯原生移植。
增量再编译 0 新建、0 失败。tools/compile-overlays.ps1 已接入 game.toml 自动编译配置；自动触发链尚待新会话验证。
尚未验收：标题菜单稳定输入、新游戏到可操作场景、战斗、存档读档、声音、长时间运行；PCSX-Redux 动态对照尚未执行。


最终补充：已实际取得 512x448 标题菜单截图 local/title-menu.png，含 Sound / New Game / Continue。输入后有进一步演出画面，但未独立证明进入可操作场景，不能标记新游戏验收通过。
最终捕获计数 692；最后一次增量编译 built OK=4、skipped=13、FAILED=0；这些新库尚未重新运行验收。此前已加载4库、59候选，原生覆盖层累计调用超过560万次，但解释回退仍存在。
测试进程已关闭。自动编译配置已保存但未验证新进程自动触发，手动脚本已验证成功。
