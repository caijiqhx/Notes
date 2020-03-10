# EXER2: 使用 qemu 执行并调试 lab1 中的软件

## 1. 从 CPU 加电后执行的第一条指令开始，单步跟踪 BIOS 的执行

根据附录，修改 `./tools/gdbinit` 文件内容如下：

```
# 将gdb设置为i8086模式
set architecture i8086
target remote :1234
```

此时应该就可以执行 `make debug-nox` 进入调试，在此之前先看一下 makefile 中的 debug 是如何定义的：

```makefile
debug-nox: $(UCOREIMG)
	$(V)$(QEMU) -S -s -serial mon:stdio -hda $< -nographic &
	$(V)sleep 2
	$(V)$(TERMINAL) -e "gdb -q -x tools/gdbinit"
```

可以看到 debug 依赖于镜像文件 ucore.img，执行以下三条命令：

1. `qemu-system-i386 -S -s -serial mon:stdio -hda bin/ucore.img -nographic &`
   > 相关 qemu 参数
   >
   > - -S freeze CPU at startup (use 'c' to start execution)
   > - -s shorthand for -gdb tcp::1234
   > - -serial redirect the serial port to char device 'dev'
   > - -hda \$< use ucore.img as IDE hard disk 0/1 image
   > - -nographic disable graphical output and redirect serial I/Os to console
2. `sleep 2`
3. `gnome-terminal -e "gdb -q -x tools/gdbinit"`

   创建新的终端窗口执行 gdb，-q 启动时不输出版本信息，-x 指定要执行的 gdb 命令文件。

知道了 debug 的原理，下面就可以执行 `make debug-nox` 命令开始 debug，根据附录中一堆英文，其实就是告诉我们第一条指令应该就是在 \$cs<<4+\$pc 地址处。为了方便调试我们再在 gdbinit 后加上 hook-stop：

```
# gdb在每次断点事件时调用的特殊定义
define hook-stop
# 每次都显示当前指令及以下四行
x /4i (($cs<<4)+$pc)
end
```

执行 `make debug-nox` ：

```
0x0000fff0 in ?? ()
(gdb) x /2i (($cs<<4)+$pc)
   0xffff0:     ljmp   $0x3630,$0xf000e05b
   0xffff7:     das
(gdb) si
   0xfe05b:	cmpw   $0xffc8,%cs:(%esi)
   0xfe060:	jo     0xfe062
   0xfe062:	jne    0xd241d416
   0xfe068:	mov    %edx,%ss
0x0000e05b in ?? ()
```

> 可以看到，第一条指令就是跳转指令，`ljmp $0x3630,$0xf000e05b`，
> 在 gdb 中：
>
> ```
> (gdb) x /4x 0xffff0
> 0xffff0:	0x00e05bea	0x2f3630f0	0x392f3332	0x00fc0039
> ```
>
> 这里显然是 gdb 的锅，在 makefile 的 qemu 命令中加入 `-d in_asm -D $(BINDIR)/q.log` 选项，即将 qemu 运行的汇编指令写入 q.log 文件中:
>
> ```
> IN:
> 0xfffffff0:  ljmp   $0xf000,$0xe05b
> ----------------
> IN:
> 0x000fe05b:  cmpl   $0x0,%cs:0x70c8
> ```
>
> 清楚地看到第一条指令就是 `ljmp $0xf000,$0xe05b`

## 2. 在初始化位置 0x7c00 设置实地址断点,测试断点正常

在 `./tools/gdbinit` 文件后添加：

```
# 在0x7c00下断点后运行
b *0x7c00
c
```

得到对应的汇编代码：

```
=> 0x7c00:	cli
   0x7c01:	cld
   0x7c02:	xor    %eax,%eax
   0x7c04:	mov    %eax,%ds
   0x7c06:	mov    %eax,%es
   0x7c08:	mov    %eax,%ss
   0x7c0a:	in     $0x64,%al
   0x7c0c:	test   $0x2,%al
   0x7c0e:	jne    0x7c0a
   0x7c10:	mov    $0xd1,%al
   0x7c12:	out    %al,$0x64
   0x7c14:	in     $0x64,%al
   0x7c16:	test   $0x2,%al
   0x7c18:	jne    0x7c14
   0x7c1a:	mov    $0xdf,%al
   0x7c1c:	out    %al,$0x60
   0x7c1e:	lgdtl  (%esi)
   0x7c21:	insb   (%dx),%es:(%edi)
   0x7c22:	jl     0x7c33
   0x7c24:	and    %al,%al
```

## 3. 从 0x7c00 开始跟踪代码运行,将单步跟踪反汇编得到的代码与 bootasm.S 和 bootblock.asm 进行比较

对比代码，发现调试反汇编得到的代码与 bootasm.S 和 bootblock.asm 文件中代码相同。

这段代码的作用就是各种初始化，从实模式转换到保护模式。

## 4. 自己找一个 bootloader 或内核中的代码位置，设置断点并进行测试

在 ucore_os_lab 中 lab1/tools/gdbinit 的原始内容：

```
file bin/kernel
target remote :1234
break kern_init
continue
```

稍加修改可以调试 kernel_init 函数，使用 gdb 的 -tui 参数可以打开代码查看窗口，方便调试。
