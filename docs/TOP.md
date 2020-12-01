# TOP

> 2020/11/22 随查随记

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

