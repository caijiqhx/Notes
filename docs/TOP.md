# TOP

> 2020/11/22 随查随记

#### 大需求 AutoHotKey ！！！

之前都在用 Terminus，主要是因为 Windows Terminal 不支持全透明只有模糊透明，所以只能忍受 Terminus 慢得要死的速度。

今天发现可以通过 AutoHotKey 调节窗口透明度，终于可以有快速的终端体验了。而且 AutoHotKey 这个东西是真滴牛🐮🍺，把各种 Win API 封装成一个脚本语言，可以很方便地绑定键盘等操作。

#### 自建 overleaf

用 nginx 反代 overleaf 的时候要添加 `client_max_body_size 50M;`，默认值是 1M，就上传不了压缩包了。

#### 网盘

MEGA 还是很好用的，免费基础 15 G，下载电脑端和移动端之后有 180 天内 70G 存储 + 70G 传输的 bonus。Pro Lite 400GB 存储 + 1TB 传输，4.99€/月，还可以。

> MEGA 这玩意挺恶心 明明有 70G 传输流量还是下载很慢（好像不开会员就用不了传输流量？？？

Onedrive 有学校的账户给了 1T 的空间，速度还是还可以，但是没用来存什么大文件，就是用来同步一些文件。

Multcloud 支持多个网盘之间传输数据，比如把资源从 Baidu 传到 MEGA，但是如果不开会员速度跟直接从百度下载没什么区别。

买了个 三星 Tab S6，三星笔记似乎是可以同步到 Onedrive。

#### Win10 任务栏右键菜单是英文

原因是 NetSpeedMonitor 插件里语言设置为英文，随便改成别的就好了。

#### POSIX 是啥玩意

可移植操作系统接口 Portable Operating System Interface of UNIX，定义了操作系统应该为应用程序提供的接口标准。

POSIX 标准意在期望获得源代码级别的软件可以执行。即为一个 POSIX 兼容的操作系统编写的程序，应该可以在任何其他的 POSIX 操作系统上编译执行。

实际上很多兼容 POSIX 标准的操作系统所作的实现是在自身原有 API 接口的基础之上再封装创建一层 POSIX 兼容从提供支持。“舍高效率而取可移植性”

#### VMware 收缩虚拟磁盘

Linux 里安装了 vmware-tools 即可执行命令：

```shell
$ vmware-toolbox-cmd disk shrink /		# 也可指定其他分区
```

或使用 VMware 提供的 vmware-vdiskmanager 工具：

```powershell
$ vmware-vdiskmanager -k target.vmdk
```

此方法需要虚拟机关机且无快照

#### test 指令咋总记不住

