# Preview

~~前几次的代码 merge 操作都是手动完成，太笨了。这次用的是 meld tql。~~

lab2 和 lab3 完成了物理和虚拟内存管理，在此基础上我们可以创建内核线程，内核线程是一种特殊的进程，内核线程与用户进程的区别有两个：

1. 内核线程只允许在内核态；
2. 用户进程会在用户态和内核态交替运行；
3. 所有内核线程共用 ucore 内核内存空间，不需为每个内核线程维护单独的内存空间，而用户进程需要维护各自的用户内存空间。

## 实验流程概述

lab2 和 lab3 完成了对内存的虚拟化，但整个控制流还是一条线串行执行。lab4 在此基础上进行 CPU 的虚拟化，即让 ucore 实现分时共享 CPU，实现多条控制流能够并发执行。从某种程度上，我们可以把控制流看作是一个内核线程。之所以称之为线程，就是因为所有的内核线程共享内核内存空间。

为了实现内核线程，需要设计管理线程的数据结构，即进程控制块（这里也就是线程控制块）。要让内核线程运行，首先要创建内核线程对应的进程控制块，还需把这些进程控制块通过链表连在一起，便于随时进行插入、删除和查找等内核进程管理事务。然后通过调度器来让不同的内核线程在不同的时间段占用 CPU 执行，实现对 CPU 的分时共享。

首先我们还是从 ./kern/init/init.c 中的 kern_init 函数入手，在完成虚拟内存的初始化工作后，就调用了 proc_init 函数，这个函数完成了 idleproc 内核线程和 initproc 内核线程的创建或复制工作。idleproc 内核线程的工作就是不停地查询，看是否有其他内核线程可以执行，如果有就让调度器选择那个内核线程执行，所以 idleproc 就是在 ucore 系统没有其他内核线程可执行的时候才会调用。接着就是调用 kernel_thread 函数来创建 initproc 内核线程，其工作就是显示 Hello World。

调度器会在特定的调度点上执行调度，完成进程切换。lab4 中的调度点即在 cpu_idle 函数中，此函数如果发现当前进程的 need_resched 置 1（初始化 idleproc 的进程控制块就已置 1），则调用 schedule 函数，完成进程调度和进程切换。进程调度的过程其实比较简单，就是在进程控制块链表中找到一个“合适”的内核线程，所谓“合适”就是指内核线程处于 PROC_RUNNABLE 的状态。在接下来的 switch_to 函数中完成具体的进程切换过程。

## 关键数据结构

进程管理信息用结构体 proc_struct 表示，在 ./kern/process/proc.h 中：

```C
struct proc_struct {
    enum proc_state state;                      // 进程状态
    int pid;                                    // 进程 ID
    int runs;                                   // 运行时间
    uintptr_t kstack;                           // 内核栈
    volatile bool need_resched;                 // 是否需要重新调度释放CPU　
    struct proc_struct *parent;                 // 父进程控制块
    struct mm_struct *mm;                       // 进程内存描述符
    struct context context;                     // 进程切换上下文
    struct trapframe *tf;                       // 中断帧
    uintptr_t cr3;                              // 进程页目录表基地址
    uint32_t flags;                             // 反应进程状态的信息，但不是运行状态，用于内核识别进程当前的状态，以备下一步操作
    char name[PROC_NAME_LEN + 1];               // Process name
    list_entry_t list_link;                     // Process link list
    list_entry_t hash_link;                     // Process hash list
};
```

主要成员变量：

1. state 表示进程所处状态：

   ```C
   // process's state in his life cycle
   enum proc_state {
       PROC_UNINIT = 0,  // uninitialized
       PROC_SLEEPING,    // sleeping
       PROC_RUNNABLE,    // runnable(maybe running)
       PROC_ZOMBIE,      // almost dead, and wait parent proc to reclaim his resource
   };
   ```

2. kstack 表示内核栈，每个线程都有一个内核栈，并且位于内核地址空间的不同位置。对于内核线程，该栈就是运行时的程序使用的栈；而对于普通进程，该栈是发生特权级改变的时候使保存被打断的硬件信息用的栈。ucore 在创建进程时分配了 2 个连续的物理页作为内核栈的空间。这个栈很小，所以内核中的代码应该尽可能的紧凑，并且避免在栈上分配大的数据结构，以免栈溢出，导致系统崩溃。

   kstack 记录了分配给该进程/线程的内核栈的位置。

   - 首先，当内核准备从一个进程切换到另一个的时候，需要根据 kstack 的值正确的设置好 tss （可以回顾一下在实验一中讲述的 tss 在中断处理过程中的作用），以便在进程切换以后再发生中断时能够使用正确的栈。
   - 其次，内核栈位于内核地址空间，并且是不共享的（每个线程都拥有自己的内核栈），因此不受到 mm 的管理，当进程退出的时候，内核能够根据 kstack 的值快速定位栈的位置并进行回收。

3. parent 表示用户进程的父进程（创建它的进程），在所有进程中，只有内核创建的第一个内核线程 idleproc 没有父进程。内核根据这个父子关系建立一个树形结构，用于维护一些特殊的操作，例如确定某个进程是否可以对另外一个进程进行某种操作等等。
4. mm 内存管理的信息，包括内存映射列表、页表指针等。mm 在 lab3 中用于虚存管理。但在实际 OS 中，内核线程常驻内存，不需要考虑 swap page 问题，在 lab5 中涉及到了用户进程，才考虑进程用户内存空间的 swap page 问题，mm 才会发挥作用。所以在 lab4 中 mm 对于内核线程就没有用了，这样内核线程的 proc_struct 的成员变量 \*mm=0 是合理的。mm 里有个很重要的项 pgdir，记录的是该进程使用的一级页表的物理地址。由于 \*mm=NULL，所以在 proc_struct 数据结构中需要有一个代替 pgdir 项来记录页表起始地址，这就是 proc_struct 数据结构中的 cr3 成员变量。
5. context 表示进程的上下文，结构体中的成员变量就是寄存器的值，用于进程切换（参见 switch.S）。在 ucore 中，所有的进程在内核中也是相对独立的（例如独立的内核堆栈以及上下文等等）。使用 context 保存寄存器的目的就在于在内核态中能够进行上下文之间的切换。实际利用 context 进行上下文切换的函数是在 kern/process/switch.S 中定义 switch_to。
6. tf 表示中断帧的指针，在 lab1 中已经见过。tf 总是指向内核栈的某个位置，当进程从用户空间跳到内核空间时，中断帧记录了进程在被中断前的状态。当内核需要跳回用户空间时，需要调整中断帧以恢复让进程继续执行的各寄存器值。除此之外，ucore 内核允许嵌套中断。因此为了保证嵌套中断发生时 tf 总是能够指向当前的 trapframe，ucore 在内核栈上维护了 tf 的链。
7. cr3 上面已经提到， cr3 保存页表的物理地址，目的就是进程切换的时候方便直接使用 lcr3 实现页表切换，避免每次都根据 mm 来计算 cr3。mm 数据结构是用来实现用户空间的虚存管理的，但是内核线程没有用户空间，它执行的只是内核中的一小段代码（通常是一小段函数），所以它没有 mm 结构，也就是 NULL。当某个进程是一个普通用户态进程的时候，PCB 中的 cr3 就是 mm 中页表（pgdir）的物理地址；而当它是内核线程的时候，cr3 等于 boot_cr3。而 boot_cr3 指向了 uCore 启动时建立好的饿内核虚拟空间的页目录表首地址。

为了管理系统中所有的进程控制块，uCore 维护了如下全局变量（位于 kern/process/proc.c）：

1. static struct proc \*current：当前占用 CPU 且处于“运行”状态进程控制块指针。通常这个变量是只读的，只有在进程切换的时候才进行修改，并且整个切换和修改过程需要保证操作的原子性，目前至少需要屏蔽中断。可以参考 switch_to 的实现。
2. static struct proc \*initproc：本实验中，指向一个内核线程。本实验以后，此指针将指向第一个用户态进程。
3. static list_entry_t hash_list[HASH_LIST_SIZE]：所有进程控制块的哈希表，proc_struct 中的成员变量 hash_link 将基于 pid 链接入这个哈希表中。
4. list_entry_t proc_list：所有进程控制块的双向线性列表，proc_struct 中的成员变量 list_link 将链接入这个链表中。

了解了 PCB 的结构，可以完成 练习 1，实现 alloc_proc 函数。

## 创建并执行内核线程

alloc_proc 建立进程控制块后，就可以通过 pcb 来创建具体的进程/线程。

首先要考虑最简单的内核进程，通常只是内核中的一小段代码或函数，没有自己的专属空间。ucore 已经对整个内核内存空间进行了管理，通过设置页表建立了内核虚拟空间（即 boot_cr3 指向的二级页表描述的空间）。所以内核中的所有线程都不需要再建立各自的页表，只需共享这个内核虚拟空间就可以访问整个物理内存了。从这个角度看，内核线程被 uCore 内核这个大“内核进程”所管理。

### 创建第 0 个内核线程 idleproc

在 kern_init 函数调用了 proc_init 函数，启动了创建内核线程的步骤。首先，当前的执行上下文就可以看成内核中一个内核进程的上下文，ucore 通过给当前执行的上下文分配一个进程控制块并初始化，作为第 0 个内核线程 initproc。proc_init 再进一步初始化：

```C
if ((idleproc = alloc_proc()) == NULL) {
    panic("cannot alloc idleproc.\n");
}

idleproc->pid = 0;                              // 合法的 id，第 0 个内核线程
idleproc->state = PROC_RUNNABLE;                // 可运行，等待调度
idleproc->kstack = (uintptr_t)bootstack;        // 之后的内核线程的内核栈都需要通过分配获得
idleproc->need_resched = 1;                     // idleproc 执行时应该由调度器切换其他进程执行
set_proc_name(idleproc, "idle");
nr_process ++;
```

由此，第 0 个内核线程就完成了。

### 创建第 1 个内核线程 initproc

第 0 个内核线程主要工作是完成内核中各个子系统的初始化，然后就执行 cpu_idle 函数：

```C
void
cpu_idle(void) {
    while (1) {
        if (current->need_resched) {
            schedule();
        }
    }
}
```

ucore 还需创建其他进程来完成各种工作，idle_proc 调用 kernel_thread 函数创建一个内核线程 init_main，在 lab4 中，这个函数就是输出了几句话。在后续的实验中，这个内核线程的工作就是创建特定的其他内核线程或用户进程。

```C
// kernel_thread - create a kernel thread using "fn" function
// NOTE: the contents of temp trapframe tf will be copied to
//       proc->tf in do_fork-->copy_thread function
int
kernel_thread(int (*fn)(void *), void *arg, uint32_t clone_flags) {
    struct trapframe tf;
    memset(&tf, 0, sizeof(struct trapframe));
    tf.tf_cs = KERNEL_CS;
    tf.tf_ds = tf.tf_es = tf.tf_ss = KERNEL_DS;
    tf.tf_regs.reg_ebx = (uint32_t)fn;
    tf.tf_regs.reg_edx = (uint32_t)arg;
    tf.tf_eip = (uint32_t)kernel_thread_entry;
    return do_fork(clone_flags | CLONE_VM, 0, &tf);
}
```

注意，kernel_thread 函数采用了局部变量 tf 来放置保存内核线程的临时中断帧，并把中断帧的指针传递给 do_fork 函数，而 do_fork 函数会调用 copy_thread 函数来在新创建的进程内核栈上专门给进程的中断帧分配一块空间。

首先给 tf 进行清零初始化，并设置中断帧的代码段和数据段为内核空间的段，这实际上也说明了 initproc 内核线程在内核空间中执行。而 initproc 内核线程从 tf.tf_eip 指向的 kernel_thread_entry 开始执行：

```assembly
.globl kernel_thread_entry
kernel_thread_entry:        # void kernel_thread(void)

    pushl %edx              # push arg
    call *%ebx              # call fn

    pushl %eax              # save the return value of fn(arg)
    call do_exit            # call do_exit to terminate current thread
```

kernel_thread_entry 函数主要为内核现场的主体 fn 函数设置一个准备开始和结束的壳，并把 fn 函数的参数 arg （保存在 edx 寄存器中）压栈，然后调用 fn 函数，把函数返回 eax 寄存器的内容压栈，调用 do_exit 函数退出线程执行。

do_fork 是创建线程的主要函数，kernel_thread 函数通过调用 do_fork 函数最终完成了内核线程的创建工作。练习 2 就是要实现 do_fork 函数，这个函数主要做了如下的几件事：

1. alloc_proc 函数，分配并初始化进程控制块；
2. setup_stack 函数，分配并初始化内核栈；
3. copy_mm 函数，根据 clone_flag 标志复制或共享进程内存管理结果；
4. copy_thread 函数，设置进程在内核（将来也包括用户态）正常运行和调度所需的中断帧和执行上下文；
5. 把设置好的进程控制块放入到 hash_list 和 proc_list 两个全局变量中；
6. 进程已准备好，设置为就绪态；
7. 返回子进程的 pid。

如果前三步没有执行成功，则需要做相应的错误处理，把相关已经占有的内存释放。copy_thread 函数做的比较多：

```C
// copy_thread - setup the trapframe on the  process's kernel stack top and
//             - setup the kernel entry point and stack of process
static void
copy_thread(struct proc_struct *proc, uintptr_t esp, struct trapframe *tf) {
    // 在内核栈的顶部设置中断帧大小的空间，将 kernel_thread 中建立的临时中断帧复制到此
    proc->tf = (struct trapframe *)(proc->kstack + KSTACKSIZE) - 1;
    *(proc->tf) = *tf;
    proc->tf->tf_regs.reg_eax = 0;          // 子进程/线程执行完 do_fork 后的返回值
    proc->tf->tf_esp = esp;                 // 设置中断帧中的栈指针 esp
    proc->tf->tf_eflags |= FL_IF;           // 使能中断

    proc->context.eip = (uintptr_t)forkret;
    proc->context.esp = (uintptr_t)(proc->tf);
}
```

设置好中断帧后，最后就是设置 initproc 的进程上下文。只有设置好执行现场后，一旦 ucore 调度器选择了 initproc 执行，就需要根据 initproc->context 中保存的执行现场来恢复 initproc 的执行。这里设置了 initproc 的执行现场中主要的两个信息：上次停止执行时的下一条指令地址 context.eip 和上次停止执行时的堆栈地址 context.esp。其实 initproc 还没有执行过，所以这其实就是 initproc 实际执行的第一条指令地址和堆栈指针。可以看出，由于 initproc 的中断帧占用了实际给 initproc 分配的栈空间的顶部，所以 initproc 就只能把栈顶指针 context.esp 设置在 initproc 的中断帧的起始位置。根据 context.eip 的赋值，可以知道 initproc 实际开始执行的地方在 forkret 函数（主要完成 do_fork 函数返回的处理工作）处。至此，initproc 内核线程已经做好准备执行了。
