# EXER3: 阅读分析源代码，理解进程执行 fork/exec/wait/exit 的实现，以及系统调用的实现

在 preview 中已经分析了系统调用的普遍实现过程：

`int 0x80 --> vector[128](vector.S) --> __alltraps(trapentry.S) --> trap(trap.c) --> trap_dispatch(trap.c) --> syscall(syscall.c)`

应用程序调用的 exit/fork/wait/getpid 等库函数最终都会调用 syscall 函数，实际上就是将系统调用号放到 eax，其他 5 个参数 a[0~4] 分别保存到 edx/ecx/ebx/edi/esi 寄存器中，即最多用 6 个寄存器来传递系统调用的参数，且系统调用的返回结果是 eax。

## Q1: 请分析 fork/exec/wait/exit 在实现中是如何影响进程的执行状态的?

### 1.1 fork

内核中的 fork 的系统调用对应的就是 sys_fork 函数：

```C
// ./kern/syscall/syscall.c
static int
sys_fork(uint32_t arg[]) {
    struct trapframe *tf = current->tf;
    uintptr_t stack = tf->tf_esp;
    return do_fork(0, stack, tf);
}
```

最后要执行的就是 ./kern/process/proc.c 中的 do_fork 函数，在 lab4 练习 2 中已经详细地分析了这个函数的执行过程：

1. alloc_proc 函数，分配并初始化进程控制块；
2. setup_stack 函数，分配并初始化内核栈；
3. copy_mm 函数，根据 clone_flag 标志复制或共享进程内存管理结果；
4. copy_thread 函数，设置进程在内核（将来也包括用户态）正常运行和调度所需的中断帧和执行上下文；
5. 把设置好的进程控制块放入到 hash_list 和 proc_list 两个全局变量中；
6. 进程已准备好，设置为就绪态；
7. 返回子进程的 pid。

do_fork 函数负责生成一个以当前进程为父进程的进程，并将当前进程的地址空间 copy 操新产生的进程中去（当然，如果是 COW 机制则不用真的 copy）。

分析 fork 对于父进程返回子进程 pid 而对子进程返回 0 的原因：

- 对于父进程，即系统调用的发起者，返回时经过 `do_fork --> sys_fork --> syscall(in kernel) --> __trapret --> syscall(for user)` 的传递路径，子进程的 pid 在 eax 中返回给父进程。
- 对于子进程，经过 `copy_thread: proc->tf->tf_regs.reg_eax = 0 --> forkrets --> __trapret: popal`，相当于执行了 fork 并且返回了 0。

### 1.2 exec

exec 系统调用最终执行的就是 do_execve 函数，在练习 1 中已经分析过了。它完成的是用户进程的创建过程，但是并不创建新进程，而是用新的内容覆盖原来的进程内存空间。用户态执行这个系统调用的区别在于会判断 `mm != NULL` 成立后执行后面尝试释放内存的过程。之后就调用 load_icode 加载并解析一个处于内存中的 ELF 格式的应用程序，建立相应的用户内存空间来放置应用程序的代码段、数据段等，且要设置好 proc_struct 结构中的成员变量 trapframe 中的内容，确保在执行此进程后，能够从应用程序设定的起始执行地址开始执行。

### 1.3 wait

do_wait 在 preview 里面也已经看到过，它负责等待由 pid 指定的一个子进程或任一个子进程，当它进入 PROC_ZOMBIE 状态后取出它的返回值并彻底回收这个子进程。如果没有等到就进入睡眠，交由 schedule 调度。

### 1.4 exit

do_exit 在 preview 中也分析过了，它负责回收当前进程的绝大部分内存，将本进程的状态设置为 PROC_ZOMBIE 并通知正在等待的父进程来回收它的内核栈和进程控制块。将当前进程的所有子进程归于 initproc，如果子进程是 PROC_ZOMBIE 状态，还需要通知 initproc。最后调度交出控制权。

## Q2: 请给出 ucore 中一个用户态进程的执行状态生命周期图

```shell
[NOT EXIST]                             [PROC_RUNNING]
    |                                          ⬆
alloc_proc                                  proc_run
    ⬇                                          ⬇
[PROC_UINIT] --wakeup_proc/proc_init--> [PROC_RUNNABLE] --do_exit
                                            |   ⬆                \\
                    free_page/do_wait/do_sleep  wakeup_proc      [PROC_ZOMBIE]
                                            ⬇   |                //
                                        [PROC_SLEEPING] --do_exit
```
