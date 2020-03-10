# EXER1: 理解通过 make 生成执行文件的过程

> 首先回顾一下 make，在 lab0 的已有对 make 的介绍，另有[gnu 的官方文档](https://www.gnu.org/software/make/manual/)。
>
> make 是一个命令工具，make 命令执行时，需要一个 makefile 文件来告诉 make 以何种方式编译源代码和链接程序。
>
> make 编译链接文件的规则：
>
> - 所有的源文件没有被编译过，则对各个源文件进行编译和链接，生成最后的可执行程序；
> - 每一个在上次执行 make 之后修改过的源文件在本次执行 make 时将会被重新编译；
> - 头文件在上一次执行 make 之后被修改，则包含此头文件的源文件在本次执行 make 时将会被重新编译。
>
> 一个简单的 makefile 描述规则组成：
>
> ```makefile
> target... : prerequisites...
> 	command
> 	...
> 	...
> ```
>
> - target：规则的目标。通常是最后生成的文件名或者为了实现这个目的而必须的中间过程文件名。可以是.o 文件、也可以是最后的可执行程序的文件名等。另外，目标也可以是一个 make 执行的动作的名称，如 “clean”，称为伪目标。
> - prerequisites：规则的依赖。生成规则目标所需要的文件名或目标列表。通常一个目标依赖于一个或者多个文件。
> - command：规则的命令行。规则所要执行的动作（任意的 shell 命令或者是可在 shell 下执行的程序）。
>
> 当规则的目标是一个文件，在它的任何一个依赖文件被修改后，在执行“make”时这个目标文件将会被重新编译或重新链接。

## Q1: 操作系统镜像文件 `ucore.img` 是如何一步一步生成的?

makefile 中 `ucore.img` 相关代码：

```makefile
V       := @
...
include tools/function.mk
...
# create ucore.img
UCOREIMG	:= $(call totarget,ucore.img)

$(UCOREIMG): $(kernel) $(bootblock)
	$(V)dd if=/dev/zero of=$@ count=10000
	$(V)dd if=$(bootblock) of=$@ conv=notrunc
	$(V)dd if=$(kernel) of=$@ seek=1 conv=notrunc

$(call create_target,ucore.img)
```

首先调用了 call 函数, 将 ucore.img 传入了 totarget 表达式，结果赋值给 UCOREIMG，这里的 totarget 表达式是在包含的文件 tools/function.mk 文件中（找了半天 tcl：

```makefile
totarget = $(addprefix $(BINDIR)$(SLASH),$(1))
```

所以最后赋值给 UCOREIMG 的值为 bin/ucore.img，即目标镜像文件。

可以看到镜像的依赖有 bootblock 、kernel，依赖生成后才会执行下面的命令。下面查看依赖的相关代码。

1. bootblock

   ```makefile
   # create bootblock
   bootfiles = $(call listf_cc,boot)
   $(foreach f,$(bootfiles),$(call cc_compile,$(f),$(CC),$(CFLAGS) -Os -nostdinc))

   bootblock = $(call totarget,bootblock)

   $(bootblock): $(call toobj,$(bootfiles)) | $(call totarget,sign)
   	@echo + ld $@
   	$(V)$(LD) $(LDFLAGS) -N -e start -Ttext 0x7C00 $^ -o $(call toobj,bootblock)
   	@$(OBJDUMP) -S $(call objfile,bootblock) > $(call asmfile,bootblock)
   	@$(OBJCOPY) -S -O binary $(call objfile,bootblock) $(call outfile,bootblock)
   	@$(call totarget,sign) $(call outfile,bootblock) $(bootblock)
   $(call create_target,bootblock)
   ```

   这里的宏定义看起来很复杂，通过 warning 函数输出对应变量的方式确定文件名。
   首先 bootblock 依赖于 obj/boot/bootasm.o 、obj/boot/bootmain.o 和 bin/sign 三个文件：

   1. bootasm.o 、bootmain.o 分别由 bootasm.S、bootmain.c 编译生成，make 时执行的命令如下：

      ```shell
      + cc boot/bootasm.S
      gcc -Iboot/ -march=i686 -fno-builtin -fno-PIC -Wall -ggdb -m32 -gstabs -nostdinc  -fno-stack-protector -Ilibs/ -Os -nostdinc -c boot/b
      ootasm.S -o obj/boot/bootasm.o
      + cc boot/bootmain.c
      gcc -Iboot/ -march=i686 -fno-builtin -fno-PIC -Wall -ggdb -m32 -gstabs -nostdinc  -fno-stack-protector -Ilibs/ -Os -nostdinc -c boot/b
      ootmain.c -o obj/boot/bootmain.o
      ```

      > 涉及的 gcc 参数，主要参考 [gcc onlinedocs](https://gcc.gnu.org/onlinedocs/gcc-7.4.0/gcc/Option-Summary.html#Option-Summary)
      >
      > - -Iboot、-Ilibs 即 -Idir 指定了头文件目录
      > - -march=i686 生成符合指定 CPU 架构的指令
      > - -fno-builtin 不识别不以 "\_\_builtin\_" 开头的内置函数
      > - -fno-PIC pic 为 position-independent code，即生成适用于共享库的位置无关代码
      > - -Wall 开启几乎所有常用的警告
      > - -ggdb 生成 gdb 可用的调试信息
      > - -m32 编译兼容 32 位
      > - -gstabs 生成 stabs 格式的调试信息
      > - -nostdinc 不使用 C 的标准库，所有需要的函数都要自己写
      > - -fno-stack-protecter 去掉检查缓冲区溢出的代码，堆栈上的保护信息可能影响调试
      > - -Os 优化代码大小

   2. sign 工具由 sign.c 编译生成，make 时执行的命令如下：

      ```shell
      + cc tools/sign.c
      gcc -Itools/ -g -Wall -O2 -c tools/sign.c -o obj/sign/tools/sign.o
      gcc -g -Wall -O2 obj/sign/tools/sign.o -o bin/sign
      ```

      可见就是比较简单的编译过程，最终生成可以运行的 sign 工具

   依赖生成后，开始执行下面的命令，最终生成 ucore.img 的依赖文件 bootblock 的命令如下：

   ```shell
   + ld bin/bootblock
   ld -m    elf_i386 -nostdlib -N -e start -Ttext 0x7C00 obj/boot/bootasm.o obj/boot/bootmain.o -o obj/bootblock.o
   objdump -S obj/bootblock.o > obj/bootblock.asm
   objcopy -S -O binary obj/bootblock.o obj/bootblock.out
   bin/sign obj/bootblock.out bin/bootblock
   'obj/bootblock.out' size: 492 bytes
   ```

   > ld 链接器的参数，参考 [ld docs](https://sourceware.org/binutils/docs/ld/Options.html#Options)
   >
   > - -m elf_i386 模拟 i386 上的链接器
   > - -nostdlib 不链接 C 标准库
   > - -N 设置代码段和数据段均可读写
   > - -e 设置程序入口为 start
   > - -Ttext 指定代码段的开始位置为 0x7C00

   bootasm.o、bootmain.o 链接生成 bootblock.o。然后 objdump 反汇编到 bootblock.asm 文件， objcopy 将 bootblock.o 文件复制到 bootblock.out 文件，其中的 -S 选项表示不复制重定位和符号信息，-O 选项表示指定输出的格式。最后用 sign 工具处理 bootblock.out 得到最终的 bootblock 文件，大小为 492 bytes。

2. kernel

   ```makefile
   # create kernel target
   kernel = $(call totarget,kernel)

   $(kernel): tools/kernel.ld

   $(kernel): $(KOBJS)
      @echo + ld $@
      $(V)$(LD) $(LDFLAGS) -T tools/kernel.ld -o $@ $(KOBJS)
      $(OBJDUMP) -S $@ > $(call asmfile,kernel)
      $(OBJDUMP) -t $@ | $(SED) '1,/SYMBOL TABLE/d; s/ .* / /; /^$$/d' > $(call symfile,kernel)

   $(call create_target,kernel)
   ```

   相比之下 kernel 的依赖文件更多，tools/kernel.ld obj/kern/init/init.o obj/kern/libs/stdio.o obj/kern/libs/readline.o obj/kern/debug/panic.o obj/kern/debug/kdebug.o obj/kern/debug/kmonitor.o obj/kern/driver/clock.o obj/kern/driver/console.o obj/kern/driver/picirq.o obj/kern/driver/intr.o obj/kern/trap/trap.o obj/kern/trap/vectors.o obj/kern/trap/trapentry.o obj/kern/mm/pmm.o obj/libs/string.o obj/libs/printfmt.o

   其中 obj/kern\/\*\/\*.o 文件由 kern/ 和 libs/ 文件夹中的文件编译生成，对应的 makefile 代码：

   ```makefile
   $(call add_files_cc,$(call listf_cc,$(KSRCDIR)),kernel,$(KCFLAGS))
   ```

   对应的命令行都与之前 bootblock 中类似。

   依赖文件生成后，开始执行生成最终 kernel 文件的命令行，主要就是将所有的 .o 文件都使用链接脚本 kernel.ld 链接生成 kernel：

   ```shell
   ld -m    elf_i386 -nostdlib -T tools/kernel.ld -o bin/kernel  obj/kern/init/init.o obj/kern/libs/stdio.o obj/kern/libs/readline.o obj/kern/debug/panic.o obj/kern/debug/kdebug.o obj/kern/debug/kmonitor.o obj/kern/driver/clock.o obj/kern/driver/console.o obj/kern/driver/picirq.o obj/kern/driver/intr.o obj/kern/trap/trap.o obj/kern/trap/vectors.o obj/kern/trap/trapentry.o obj/kern/mm/pmm.o  obj/libs/string.o obj/libs/printfmt.o
   ```

   新增了一个 -T 选项即为指定使用连接脚本 kernel.ld。

   后面的进行的操作就是反汇编到文件，以及输出符号表通过 sed 命令处理后输出到文件。

至此，ucore.img 的依赖文件就绪，开始执行后面的指令：

\$(V) 即 '@'，表示在执行命令时不会输出命令，'\$@' 表示目标文件即 ucore.img ， dd 命令创建了一个大小为 10000×512 字节的空文件，然后将 bootblock 从头复制到目标文件，前面已经看到了 bootblock 文件大小为 492 bytes，仅占用了第一个块，最后将 kernel 跳过第一块复制到后续的块中。

> dd 命令参数
>
> - if/of 输入/输出文件
> - count=n 表示读取指定的区块数，ibs 块的默认大小为 512 字节
> - conv=notrunc 指定转换文件的方式，notrunc 表示不截断输出
> - seek=n 表示输出时跳过的区块数

## Q2: 一个被系统认为是符合规范的硬盘主引导扇区的特征是什么?

符合规范的硬盘主引导扇区即大小为 512bytes，且最后两个字节为 0x55AA 的一个硬盘扇区。

生成主引导扇区文件 bootblock 的最后一步是用 sign 工具处理，查看其源代码：

```C
printf("'%s' size: %lld bytes\n", argv[1], (long long)st.st_size);
if (st.st_size > 510) {
   fprintf(stderr, "%lld >> 510!!\n", (long long)st.st_size);
   return -1;
}
char buf[512];
memset(buf, 0, sizeof(buf));
FILE *ifp = fopen(argv[1], "rb");
int size = fread(buf, 1, st.st_size, ifp);
if (size != st.st_size) {
   fprintf(stderr, "read '%s' error, size is %d.\n", argv[1], size);
   return -1;
}
fclose(ifp);
buf[510] = 0x55;
buf[511] = 0xAA;
```

要求可执行文件的大小不大于 510bytes，在 511，512 两个字节加上 0x55AA 后，它就是一个符合规范的硬盘主引导扇区。
