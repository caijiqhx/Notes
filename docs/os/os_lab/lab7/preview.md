# Preview

**实验目的**：

- 理解操作系统的同步互斥的设计实现；
- 理解底层支撑技术：禁用中断、定时器、等待队列；
- 在 ucore 中理解信号量（semaphore）机制的具体实现；
- 理解管程机制，在 ucore 内核中增加基于管程（monitor）的条件变量（condition variable）的支持；
- 了解经典进程同步问题，并能使用同步机制解决进程同步问题。

实验六完成了用户进程的调度框架和具体的调度算法，可调度运行多个进程。如果多个进程需要协同操作或访问共享资源，则存在如何同步和有序竞争的问题。本次实验，主要是熟悉 ucore 的进程同步机制——信号量（semaphore）机制，以及基于信号量的哲学家就餐问题解决方案。然后掌握管程的概念和原理，并参考信号量机制，实现基于管程的条件变量机制和基于条件变量来解决哲学家就餐问题。

哲学家就餐问题描述如下：有五个哲学家，他们的生活方式是交替地进行思考和进餐。哲学家们公用一张圆桌，周围放有五把椅子，每人坐一把。在圆桌上有五个碗和五根筷子，当一个哲学家思考时，他不与其他人交谈，饥饿时便试图取用其左、右最靠近他的筷子，但他可能一根都拿不到。只有在他拿到两根筷子时，方能进餐，进餐完后，放下筷子又继续思考。

merge 的时候发现还要修改 ./kern/trap/trap.c::trap_dispatch 中时钟中断的操作：

```C
case IRQ_OFFSET + IRQ_TIMER:
    ++ticks;
	// sched_class_proc_tick(current);
    run_timer_list();
```

## 实验流程概述

互斥是指某一资源同时只允许一个进程对其进行访问，具有唯一性和排他性，但互斥不用限制进程对资源的访问顺序。同步是指在进程间的执行必须严格按照规定的某种现后次序来运行，即访问是有序的，这种现后次序取决于要系统完成的任务需求。写资源时要求满足互斥，读可允许同时访问。

lab7 设计实现了多种同步互斥手段，包括时钟中断管理、等待队列、信号量、管程机制（包括条件变量设计）等，并基于信号量实现了哲学家问题的执行过程。练习是要求用管程机制实现哲学家问题的执行过程。当进程无法进入临界区（无法获得信号量）时，可让进程进入等待队列，从而由调度器选择一个就绪态的进程进行进程切换，让新进程有机会占用 CPU 执行，从而让整个系统的运行更加高效。

lab7 中修改了内核线程 initproc 对应的 init_main，增加了 check_sync 函数，这个函数可以理解为是 lab7 的总控函数，实现了基于信号量和管程的哲学家问题。

## 同步互斥的底层支持

定时器、屏蔽/使能中断和等待队列。

### 定时器

ucore 中，时钟 timer 中断给操作系统提供了有一定间隔的时间事件，操作系统将其作为基本的调度和即使单位，记两次时钟中断之间的时间间隔成为一个时间片。可以实现基于时间的睡眠等待和唤醒机制。

```C
typedef struct {
    unsigned int expires;       // 到期时间
    struct proc_struct *proc;   // 使用定时器的进程，到期后唤醒
    list_entry_t timer_link;    // 定时器链表
} timer_t;

// 向系统添加某个初始化的 timer_t，该定时器在指定时间后被激活，并被对应的进程唤醒至 runnable
void add_timer(timer_t *timer)
// 向系统取消某个定时器，取消后不会被系统激活并唤醒进程
void del_timer(timer_t *timer)
// 更新当前系统时间点，遍历当前所有处在系统管理内的定时器，找出所有应该激活的计数器并激活他们。该过程在且旨在每次定时器中断时被调用 就是上面再 trap_dispatch 里时钟中断对应的操作
void run_timer_list(void)
```

timer 的使用主要就是 sleep 系统调用：

```C
int
do_sleep(unsigned int time) {
    if (time == 0) {
        return 0;
    }
    bool intr_flag;
    local_intr_save(intr_flag);
    timer_t __timer, *timer = timer_init(&__timer, current, time);
    current->state = PROC_SLEEPING;
    current->wait_state = WT_TIMER;
    add_timer(timer);
    local_intr_restore(intr_flag);

    schedule();

    del_timer(timer);
    return 0;
}
```

### 屏蔽与使能中断

ucore 中的中断屏蔽/使能控制，已经看到过很多次，就是 local_intr_save 和 local_intr_restore，调用关系如下：

- 关中断：local_intr_save --> \_\_intr_save --> intr_disable -->cli
- 开中断：local_intr_restore --> \_\_intr_restore --> intr_enable --> sti

最终就是通过 x86 的 cli 和 sti 指令，实现了关（屏蔽）和开（使能）中断，即设置了 eflags 寄存器中与中断相关的位。通过关闭中断，可以防止对当前执行的控制流被其他中断事件处理所打断。既然不能打断中断，那也就意味着在内核运行的当前进程无法被打断或被重新调度，即实现了对临界区的互斥操作。

```C
local_intr_save(intr_flag);
{
    // 临界区代码
}
local_intr_restore(intr_flag);
```

对于多处理器情况下，这种情况无法实现互斥，因为屏蔽了一个 cpu 的中断，只能组织本地 cpu 上的进程不会被中断或调度，并不意味着其他 cpu 上的进程无法执行临界区的代码。开关中断机制是实现信号量等高层同步互斥原语的底层支撑基础之一。

### 等待队列

用户进程或内核线程通过转入等待状态以等待某个特定时间（比如睡眠、等待子进程结束、等待信号量等），当该事件发生时这些进程能够被再次唤醒。内核实现这一功能的一个底层支撑机制就是等待队列 wait_queue，等待队列和每一个事件联系起来。需要等待事件的进程在转入休眠状态后插入到等待队列中。当事件发生之后，内核遍历相应等待队列，唤醒休眠的用户进程或内核线程，设置为就绪态，并将程序从等待队列中清除。

```C
typedef struct {
    list_entry_t wait_head; // 等待队列头
} wait_queue_t;

struct proc_struct;

typedef struct {
    struct proc_struct *proc;   // 等待进程
    uint32_t wakeup_flags;      // 进程被放入等待队列的原因标记
    wait_queue_t *wait_queue;   // 指向此 wait 结构所属于的 wait_queue
    list_entry_t wait_link;     // 用来组织 wait_queue 中 wait 节点的链接
} wait_t;

// 实现 wait_t 中成员的指针向 wait_t 指针的转化
#define le2wait(le, member)         \
    to_struct((le), wait_t, member)
```

底层的操作就是对 wait_queue 的初始化、插入、删除和查找操作

```C
void wait_init(wait_t *wait, struct proc_struct *proc);    //初始化wait结构
bool wait_in_queue(wait_t *wait);                          //wait是否在wait queue中
void wait_queue_init(wait_queue_t *queue);                 //初始化wait_queue结构
void wait_queue_add(wait_queue_t *queue, wait_t *wait);    //把wait前插到wait queue中
void wait_queue_del(wait_queue_t *queue, wait_t *wait);    //从wait queue中删除wait
wait_t *wait_queue_next(wait_queue_t *queue, wait_t *wait);//取得wait的后一个链接指针
wait_t *wait_queue_prev(wait_queue_t *queue, wait_t *wait);//取得wait的前一个链接指针
wait_t *wait_queue_first(wait_queue_t *queue);             //取得wait queue的第一个wait
wait_t *wait_queue_last(wait_queue_t *queue);              //取得wait queue的最后一个wait
bool wait_queue_empty(wait_queue_t *queue);
```

高层函数基于底层函数实现了让进程进入等待队列，以及从等待队列中唤醒进程的函数：

```C
//让wait与进程关联，且让当前进程关联的wait进入等待队列queue，当前进程睡眠
void wait_current_set(wait_queue_t *queue, wait_t *wait, uint32_t wait_state);
//把与当前进程关联的wait从等待队列queue中删除
void wait_current_del(queue, wait);
//唤醒与wait关联的进程
void wakeup_wait(wait_queue_t *queue, wait_t *wait, uint32_t wakeup_flags, bool del);
//唤醒等待队列上挂着的第一个wait所关联的进程
void wakeup_first(wait_queue_t *queue, uint32_t wakeup_flags, bool del);
//唤醒等待队列上所有的等待的进程
void wakeup_queue(wait_queue_t *queue, uint32_t wakeup_flags, bool del);
```

对于唤醒进程的函数 wakeup_wait，它会被信号量的 V 操作 up 函数调用，并且它会调用 wait_queue_del 和 wakeup_proc 函数来完成唤醒进程的操作。

对于让进程等待状态的函数 wait_current_set，它会被信号量的 P 操作函数 down 调用，并且会调用 wait_init 完成对等待项的初始化，并进一步调用 wait_queue_add 来把与要处于等待状态的进程所关联的等待项挂到与信号量绑定的等待队列中。

## 信号量

在练习 1 中会分析 ucore 中信号量的实现。

## 管程和条件变量

引入管程是为了将对共享资源的所有访问及其所需要的同步操作集中并封装起来。Hansan 为管程下的定义：“一个管程定义了一个数据结构和能为并发进程所执行（在该数据结构上）的一组操作，这组操作能同步进程和改变管程中的数据。”由此，管程由四部分组成：

- 管程内部的共享变量；
- 管程内部的条件变量；
- 管程内部并发执行的进程；
- 对局部于管程内部的共享数据设置初始值的语句。

局限在管程中的数据结构，只能被局限在管程的操作过程所访问，任何管程之外的操作过程的都不能访问它；另一方面，局限在管程中的操作过程也主要访问管程内的数据结构。由此可见，管程相当于一个隔离区，它把共享变量和对它进行操作的若干个过程围了起来，所有进程要访问临界资源时，都必须经过管程才能进入，而管程每次只允许一个进程进入管程，从而需要学报进程之间互斥。

但在管程中仅仅有互斥操作是不够用的，进程可能需要等待某个条件 Cond 为真才能继续执行。如果采用忙等方式：`while not (Cond) do {}`，则在单处理器情况下，将会导致所有其他进程都无法进入临界区使得该条件 Cond 为真，该管程的执行将会发生死锁。为此，可引入条件变量 Condition Variables。一个条件变量 CV 可理解为一个进程的等待队列，队列中的进程正等待某个条件 Cond 为真。每个条件变量关联着一个条件，如果条件 Cond 不为真，需要等待，如果为真，则进程可以进一步在管程中执行。需要注意当一个进程等待一个条件变量 CV，该进程需要退出管程，这样才能让其他进程可以进入管程执行，并进行相关操作，比如设置条件 Cond 为真，改变条件变量的状态，并唤醒等待在此条件变量 CV 上的进程。因此对条件变量 CV 由两种主要操作：

- wait_cv: 被一个进程调用，以等待断言 Pc 被满足后该进程可恢复执行。进程挂在该条件变量上等待时，不被认为是占用了管程。
- signal_cv: 被一个进程调用，以指出断言 Pc 现在为真，从而可以唤醒等待断言 Pc 被满足的进程继续执行。
