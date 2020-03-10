# Preview

lab5 完成了用户进程的管理，可在用户态运行多个进程。但到目前为止，采用的调度策略是很简单的 FIFO 调度策略。本次实验，主要是熟悉 ucore 的系统调度器框架，以及基于此框架的 Round-Robin(R) 调度算法。然后参考 RR 调度算法的实现，完成 Stride Scheduling 调度算法。

还是先用 meld merge 代码，在 ./kern/process/proc.c 中 alloc_proc 有一处需要更新的，需要对 proc_struct 新增的成员变量初始化：

```C
memset(proc, 0, sizeof(struct proc_struct));
proc->pid = -1;
proc->cr3 = boot_cr3;
list_init(&proc->run_link);
// 相当于就加了个 list_init，因为前面对结构体整体置 0 了
```

## 实验流程概述

lab5 创建了用户进程，并让它们正确运行，这中间也实现了 FIFO 调度策略。lab6 专门需要针对处理器调度框架和各种算法进行设计和实现，为此对 ucore 的调度部分进行了适当的修改，使得 ./kern/schedule/sched.c 只实现了调度器框架，而不再涉及具体的调度算法实现，而调度算法在单独的文件（default_sched.c）中实现。

此外，实验中还设计了 idleproc 的概念，当 cpu 没有进程可以执行时，ucore 已单独的进程 idleproc 作为 cpu 空闲的 idle 进程，通常是个死循环。

lab6 的大致执行过程，在 ./kern/init/init.c 的 kern_init 函数增加了对 sched_init 函数的调用。主要完成了对实现特定调度算法的调度类 sched_class 的绑定，其结构就类似于前面的 pmm_manager，保存了实现调度方法的函数指针。

重点问题在于：

1. 何时或何事件发生后需要调度？
2. 何时或何事件发生后需要调整实现调度算法所涉及的参数？
3. 如何基于调度框架设计具体的调度算法？
4. 如何灵活应用链表等数据结构管理进程调度？

## 进程状态

进程状态之间的转换需要有一个更为清晰的表述，runnable 的进程会被放在运行队列中，running 和 runnable 共享同一状态 PROC_RUNNABLE，不同之处在于处于 running 态的进程不会放在运行队列中。

进程的正常生命周期如下：

1. 进程首先在 cpu 初始化或 sys_fork 时被创建，当为该进程分配了一个进程控制块即 ./kern/process/proc.c::alloc_proc 后，该进程进入 uinit 状态；
2. 当进程完全完成初始化后，进程转为 runnable 态；
3. 当达到调度点时，由调度器 sched_class 根据运行队列 rq 的内容来判断一个进程是否应该被运行，即把处于 runnable 态的进程转换成 running 态，在 cpu 执行；
4. running 态的进程通过 wait 等系统调用被阻塞，进入 sleeping 态；
5. sleeping 态的进程被 wakeup 变成 runnable 态的进程；
6. running 态的进程主动 exit 编程 zombie 态，然后由其父进程完成对其资源的最后释放，子进程的进程控制块成为 unused；
7. 所有从 runnable 态变成其他状态的进程都要出运行队列，反之，被放入某个运行队列中。

## 进程调度实现

调度本质上体现了对 cpu 资源的抢占，对用户进程而言，中断可以随时打断用户进程的执行，转到操作系统内部，从而给了操作系统以调度控制权，让操作系统可以根据具体情况（比如用户进程时间片已经用完）选择其他用户进程执行。这体现了用户进程的可抢占行（preemptive）。ucore 的内核执行是不可抢占的，即在执行任意内核代码时，cpu 控制权不可被强制剥夺。不是在所有情况下 ucore 内核执行都是不可抢占的，有以下几种固定情况是例外：

1. 进程同步互斥操作；
2. 进行磁盘读写等耗时的异步操作，由于等待完成的耗时太长，ucore 会调用 schedule 让其他就绪进程执行。

其实就是由于当前进程所需的某个资源无法得到满足，无法继续执行下去，从而不得不主动放弃对 cpu 的控制权。这些在内核中放弃 cpu 控制权的执行地点是固定而不是任意的，不能体现内核任意位置都可抢占性的特点。

lab6 中的调度点 ：

1. proc.c::do_exit: 用户进程执行结束，主动放弃 cpu 控制权；
2. proc.c::do_wait: 用户等待子进程结束，主动放弃 cpu 控制权；
3. proc.c::init_main: initproc 内核线程等待所有用户进程结束，如果没有结束，就主动放弃 cpu 控制权，initproc 内核线程在所有用户进程结束后，让 kswapd 内核线程执行 10 次，用于回收空闲内核资源；
4. proc.c::cpu_idle: idleproc 内核线程的工作就是等待有处于就绪态的进程或线程，如果有就调用 schedule 函数；
5. sync.h::lock: 在获取锁的过程中，如果无法得到锁，则主动放弃 cpu 控制权；
6. trap.c::trap: 如果在当前进程在用户态被打断去，且当前进程控制块的成员变量 need_resched 置 1，则当前进程会放弃 cpu 控制权。

### 进程切换过程

进程调度函数 schedule 选择下一个将占用 cpu 执行的进程后，将调用进程切换，从而让新的进程得以执行。两个用户进程进行进程切换的过程如下：

1. 首先在执行某进程 A 的用户代码时，出现了一个 trap，这个时候就会从进程 A 的用户态切换到内核态，并保存好进程 A 的 trapframe；
2. 当内核态处理中断时发现需要进行进程切换时，ucore 通过 schedule 函数选择下一个将占用 cpu 执行的进程 B，然后会调用 proc_run 函数进一步调用 switch_to 函数；
3. 切换到 进程 B 的内核态，继续进程 B 上一次在内核态的操作，并通过 iret 指令，最终将执行权转交给进程 B 的用户空间；
4. 当进程 B 由于某种原因发生中断之后，会从进程 B 的用户态切换到内核态，并保存好进程 B 的 trapframe；
5. 当内核处理中断时发现需要进行进程切换时，即需要切换到进程 A，ucore 再次切换到进程 A，会执行进程 A 上一次在内核调用 schedule 函数返回后的下一行代码，这行代码当然还是在进程 A 的上一次中断处理流程中；
6. 最后当进程 A 的中断处理完毕后，执行权反交给进程 A 的用户态代码。

## 调度框架和调度算法

### 设计思路

调度算法都需要选择一个就绪进程来占用 cpu 运行，需要选择对应的数据结构，队列、二叉树、红黑树等不同的组织方式。

操作时，就要从基于某种数据结构的就绪进程集合中选择出一个进程执行，分为选择和提出两个操作。同时要考虑到一个处于运行态的进程还会由于某种原因回到就绪态而不能继续占用 cpu 执行，这样就会重新进入到就绪进程集合中。这样三个基本操作：选择、进入和离开。

在进程的执行过程中，就绪进程的等待时间和执行进程的执行时间是影响调度选择的重要因素，这两个因素随着时间的流逝和各种时间的发生在不停地变化，这就需要调度器实现相关的变化感知操作：timer 时间事件感知操作。在进程运行或等待的过程中，调度器可以调整进程控制块中与进程调度相关的属性值（消耗的时间片、进程优先级等），并可能导致对进程组织形式的调整（以时间片大小的顺序来重排双向链表），并最终可能操作调度选择新的进程占用 cpu 运行，属于调整操作。

### 数据结构

ucore 中引入 run_queue 即运行队列，单 cpu 只有一个全局的运行队列。

运行队列通过链表的形式组织，每个节点是一个 list_entry_t，每个又对应到了 proc_struct\*，通过宏 le2proc 完成。在 proc_struct 中有一个 run_link 的，因此可以通过偏移量找到对

调度器框架：

```C
struct sched_class {
    const char *name;
    // 初始化运行队列
    void (*init)(struct run_queue *rq);
    // 将进程 proc 插入队列 rq
    void (*enqueue)(struct run_queue *rq, struct proc_struct *proc);
    // 将进程 proc 从队列 rq 删除
    void (*dequeue)(struct run_queue *rq, struct proc_struct *proc);
    // 返回运行队列中下一个可执行的进程
    struct proc_struct *(*pick_next)(struct run_queue *rq);
    // timetick 处理函数
    void (*proc_tick)(struct run_queue *rq, struct proc_struct *proc);
};
```

进程控制块中与进程调度相关的信息：

```C
struct proc_struct {

    ...
    // 当前进程是否需要调度
    volatile bool need_resched;
    // 运行队列
    struct run_queue *rq;
    // 当前进程的调度链表结构，该结构内部的连接组成了运行队列
    list_entry_t run_link;
    // 该进程剩余的时间片
    int time_slice;
    // 进程在优先队列中的节点
    skew_heap_entry_t lab6_run_pool;
    // 进程的调度优先级
    uint32_t lab6_stride;
    // 进程的调度步进值
    uint32_t lab6_priority;
    ...
};
```

运行队列：

```C
struct run_queue {
    // 队列头或尾
    list_entry_t run_list;
    // 表示内部的进程总数
    unsigned int proc_num;
    // 每个进程一轮占用的最多时间片
    int max_time_slice;
    // For LAB6 ONLY 优先队列形式的进程容器
    skew_heap_entry_t *lab6_run_pool;
};
```

Round Robin 算法的具体实现分析见练习 1。

## Stride Scheduling

基本思想：

1. 每个 runnable 的进程设置一个当前状态 stride，表示该进程当前的调度权。另外定义其对应的 pass 值，表示对应进程在调度后，stride 需要进行的累加值。
2. 每次需要调度时，从当前 runnable 态的进程中选择 stride 最小的进程调度。
3. 对于获得调度的进程 P，将对应的 stride 加上其对应的步长 pass（只与进程的优先权有关系）。
4. 在一段固定的时间之后，回到 2.步骤，重新调度当前 stride 最小的进程。
5. 可以证明，如果令 P.pass =BigStride / P.priority 其中 P.priority 表示进程的优先权（大于 1），而 BigStride 表示一个预先定义的大常数，则该调度方案为每个进程分配的时间将与其优先级成正比

ucore 提供了斜堆来实现每次选出最小 stride 进程的操作。
