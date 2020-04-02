# 操作系统实验

南开大学操作系统课程，基于 [ucore](https://github.com/chyyuu/ucore_os_lab) 的课程实验。

## Lab 1

`trapframe` 结构体保存中断位置的程序上下文，`ss, esp` 入栈，`eflags, cs, eip` 入栈，错误代码 `error_code` 入栈，无对应代码填入 0，然后填入中断号 `trapno`。调用 `__alltraps`，依次填入 `ds, es, fs, gs`，`pushal` 依次将 `eax, ecs, edx, ebx, old esp, ebp, esi, edi` 入栈。

## Lab 2

探测物理内存：`int 15h` 中断，参数为 `eax: e820h`。

分页管理物理内存，使用 `free_area_t` 结构维护空闲的内存块。

段页式管理，逻辑地址 => 线性地址 => 物理地址。

## Lab 3

虚拟内存管理。

几种 `page_fault`：

- 目标页帧不存在，页表项全为 0，未建立映射或已撤销。
- 相应的物理页帧不在内存中，页表项非空，Present 标志位为 0。
- 不满足访问权限，页表项 Present 标志为 1，但低权限试图访问高权限，或者程序试图写只读页面。

`vma_struct` 维护应用程序运行所需的合法内存空间。

缺页中断流程，跟普通中断的流程类似。

页面替换算法：

- FIFO：Belady 现象，增加页帧数，访问异常数增多。
- Clock：环形链表，扫描，找到第一个访问位为 0 的换出。
- ExClock：还要考虑是否修改过。

## Lab 4

创建内核线程，共用内核内存空间。第 0 个进程 idleproc，第 1 个进程 initproc。

创建进程控制块，包括进程状态、内核栈、是否需要调度、父进程、上下文、中断帧、页表地址等。

kernel_thread 函数调用设置中断帧，然后调用 do_fork 创建线程。

do_fork 函数流程：

- 分配并初始化进程控制块。
- 分配并初始化内核栈。
- 复制或共享进程内存管理。
- 设置进程中断帧和执行上下文。
- 控制块插入 `hash_list` 和 `proc_list`。
- 设置为就绪态。
- 返回子进程的 pid。

## Lab 5

