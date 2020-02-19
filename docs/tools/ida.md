## IDA

> IDA 入手还是比较简单的，主要再熟悉一下远程调试

### IDA 远程调试

使用 vmware 下的 kali linux 调试，将 <IDADIR>/dbgsrv 下的 linux_server64 复制到 kali，运行，监听 kali 端口。

Debugger - Select debugger - Remote Linux debugger

设置 kali 的地址，开始调试即可。

也可以在 kali 的 docker 中调试。