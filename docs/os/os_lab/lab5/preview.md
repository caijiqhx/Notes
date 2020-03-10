# Preview

lab 4 完成了内核线程，但到目前为止，所有的运行都在内核态执行。lab 5 将创建用户进程，让用户进程在用户态执行，且在需要 ucore 支持时，可通过系统调用来让 ucore 提供服务。为此需要构造出第一个用户进程，并通过系统调用 sys_fork/sys_exec/sys_exit/sys_wait 来支持运行不同的应用程序，完成对用户进程的执行过程的基本管理。

在代码 merge 的时候看到了很多需要改进前四个实验代码的地方。

1. ./kern/trap/trap.c 中要加入系统调用的中断设置，且在时钟中断的时候要在时间片结束后调度

   ```C
   // 从trap.h 看到 系统调用对应是 0x80，系统调用应该对应用户态的软件权限
    SETGATE(idt[T_SYSCALL], 1, GD_KTEXT, __vectors[T_SYSCALL], DPL_USER);

    // 时间片结束设置当前进程可调度
    ticks ++;
    if(ticks % TICK_NUM == 0) {
        assert(current != NULL);
        current->need_resched = 1;
    }
   ```

2. ./kern/process/proc.c 中 alloc_proc 添加 wait_state、cptr、yptr 和 optr 的初始化，之前我初始化的时候就是把整个 proc_struct 结构体都置 0 了，wait_state 初值为 0，后面指针的初值为 NULL，就不用再单独赋值了。
3. ./kern/process/proc.c 中 do_fork 中添加设置当前进程为父进程后，确保当前进程的 wait_state 为 0，同时调用 set_links 函数完成相关链接的设置：

   ```C
   proc->parent = current; // 设置父进程
   assert(current->wait_state == 0);

   // set_links - set the relation links of process
   static void
   set_links(struct proc_struct *proc) {
        list_add(&proc_list, &(proc->list_link));
        proc->yptr = NULL;
        if ((proc->optr = proc->parent->cptr) != NULL) {
            proc->optr->yptr = proc;
        }
        proc->parent->cptr = proc;
        nr_process ++;
   }
   ```

## 实验流程概述

分析本实验的执行过程，以及用户进程的生命周期来阐述用户进程管理的设计与实现。

进程的执行空间扩展到了用户态空间，且出现了创建子进程执行应用程序等与 lab4 有较大不同的地方，所以具体实现的不同主要集中在进程管理和内存管理部分。首先，在 总控函数 kern_init 并未有变化。实际上其调用的物理内存初始化，进程管理初始化有一定的变化。

在内存管理部分，与 lab4 最大的区别就是增加用户态虚拟内存的管理。为了管理用户态的虚拟内存，需要对页表的内容进行扩展，能够把部分物理内存映射为用户态虚拟内存。如果某进程执行过程中，CPU 在用户态下执行（在 CS 段寄存器最低两位包含有一个 2 位的优先级域，如果为 0，表示 CPU 运行在特权态；如果为 3，表示 CPU 运行在用户态），则可以访问本进程页表描述的用户态虚拟内存，但由于权限不够，不能访问内核态虚拟内存。另一方面，不同的进程有各自的页表，所以即使不同进程的用户态虚拟地址相同，但由于页表把虚拟页映射到了不同的物理页帧，所以不同进程的虚拟内存空间是被隔离开的，相互之间无法直接访问。在用户态内存空间和内核态内核空间之间需要拷贝数据，让 CPU 处在内核态才能完成对用户空间的读或写，为此需要设计专门的拷贝函数（copy_from_user 和 copy_to_user）完成。但反之则会导致违反 CPU 的权限管理，导致内存访问异常。

在进程管理方面，主要涉及到的是进程控制块中与内存管理相关的部分，包括建立进程的页表和维护进程可访问空间（可能还没有建立虚实映射关系）的信息；加载一个 ELF 格式的程序到进程控制块管理的内存中的方法；在进程复制（fork）过程中，把父进程的内存空间拷贝到子进程内存空间的技术。另外一部分与用户态进程生命周期管理相关，包括让进程放弃 CPU 而睡眠等待某事件；让父进程等待子进程结束；一个进程杀死另一个进程；给进程发消息；建立进程的血缘关系链表。

当实现了上述内存管理和进程管理的需求后，接下来 ucore 的用户进程管理工作就比较简单了。首先，“硬”构造出第一个进程（idle_proc，lab4 已经提到），它是后续所有进程的祖先；然后，在 proc_init 函数中，通过 alloc 把当前 ucore 的执行环境转变成 idle 内核线程的执行现场；然后调用 kernel_thread 来创建第二个内核线程 init_main，而 init_main 内核线程有创建了 user_main 内核线程。到此，内核线程创建完毕，应该开始用户进程的创建过程，这第一步实际上是通过 user_main 函数调用 kernel_tread 创建子进程，通过 kernel_execve 调用来把某一具体程序的执行内容放入内存。具体的放置方式是根据 ld 在此文件上的地址分配为基本原则，把程序的不同部分放到某进程的用户空间中，从而通过此进程来完成程序描述的任务。一旦执行了这一程序对应的进程，就会从内核态切换到用户态继续执行。以此类推，CPU 在用户空间执行的用户进程，其地址空间不会被其他用户的进程影响，但由于系统调用（用户进程直接获得操作系统服务的唯一通道）、外设中断和异常中断的会随时产生，从而间接推动了用户进程实现用户态到到内核态的切换工作。ucore 对 CPU 内核态与用户态的切换过程需要比较仔细地分析（应该和 lab1 challenge 差不多）。当进程执行结束后，需回收进程占用和没消耗完毕的设备整个过程，且为新的创建进程请求提供服务。在本实验中，当系统中存在多个进程或内核线程时，ucore 采用了一种 FIFO 的很简单的调度方法来管理每个进程占用 CPU 的时间和频度等。在 ucore 运行过程中，由于调度、时间中断、系统调用等原因，使得进程会进行切换、创建、睡眠、等待、发消息等各种不同的操作，周而复始，生生不息。

## 创建用户进程

./user 文件夹中为用户程序和库。

### 应用程序的组成和编译

来看第一个应用程序，在 ./user/hello.c 中：

```C
#include <stdio.h>
#include <ulib.h>

int
main(void) {
    cprintf("Hello world!!.\n");
    cprintf("I am process %d.\n", getpid());
    cprintf("hello pass.\n");
    return 0;
}
```

输出了一些字符串，然后通过系统调用 sys_getpid 调用输出该进程的 pid。

执行 make 指令可以找到对 hello.c 编译的过程：

```shell
+ cc user/hello.c
gcc -Iuser/ -march=i686 -fno-builtin -fno-PIC -Wall -ggdb -m32 -gstabs -nostdinc  -fno-stack-protector -Ilibs/ -Iuser/include/ -Iuser/libs/ -c user/hello.c -o obj/user/hello.o

ld -m    elf_i386 -nostdlib -T tools/user.ld -o obj/__user_hello.out  obj/user/libs/panic.o obj/user/libs/syscall.o obj/user/libs/ulib.o obj/user/libs/initcode.o obj/user/libs/stdio.o obj/user/libs/umain.o  obj/libs/string.o obj/libs/printfmt.o obj/libs/hash.o obj/libs/rand.o obj/user/hello.o

ld -m    elf_i386 -nostdlib -T tools/kernel.ld -o bin/kernel  obj/kern/init/entry.o obj/kern/init/init.o ... -b binary obj/__user_hello.out ...

```

可以看到 hello.c 编译依赖的是 ./user/lib 以及 ./lib 中的库，在 make 的最后一步执行了一个 ld 命令，把 hello 应用程序的执行码 `./obj/__user_hello.out` 连接在了 ucore kernel 的末尾。且 ld 命令会在 kernel 中会把 `__user_hello.out` 的位置和大小记录在全局变量`_binary_obj__user_hello_out_start` 和 `_binary_obj__user_hello_out_size` 中，这样这个 hello 用户程序就能够和 ucore 内核一起被 bootloader 加载到内存里中，并且通过这两个全局变量定位 hello 用户程序执行码的起始位置和大小。

### 用户进程的虚拟地址空间

在 ./tools/user.ld 描述了用户空间虚拟地址的执行入口虚拟地址：

```
SECTIONS {
    /* Load programs at this address: "." means the current address */
    . = 0x800020;
```

在 ./tools/kernel.ld 描述了内核虚拟空间的起始地址：

```
SECTIONS {
    /* Load the kernel at this address: "." means the current address */
    . = 0xC0100000;
```

这样 ucore 把用户进程的虚拟地址空间分了两块，一块与内核线程一样，是所有用户进程都共享的内核虚拟地址空间，映射到同样的物理内存空间中，这样在物理内存中只需放置一份内核代码，使得用户进程从用户态进入核心态时，内核代码可以统一应对不同的内核程序；另外一块是用户虚拟地址空间，虽然虚拟地址范围一样，但映射到不同且没有交集的物理内存空间中。这样当 ucore 把用户进程的执行代码（即应用程序的执行代码）和数据（即应用程序的全局变量等）放到用户虚拟地址空间中时，确保了各个进程不会“非法”访问到其他进程的物理内存空间。ucore 给一个用户进程的虚拟内存空间如下：

```
/* *
 * Virtual memory map:                                          Permissions
 *                                                              kernel/user
 *
 *     4G ------------------> +---------------------------------+
 *                            |                                 |
 *                            |         Empty Memory (*)        |
 *                            |                                 |
 *                            +---------------------------------+ 0xFB000000
 *                            |   Cur. Page Table (Kern, RW)    | RW/-- PTSIZE
 *     VPT -----------------> +---------------------------------+ 0xFAC00000
 *                            |        Invalid Memory (*)       | --/--
 *     KERNTOP -------------> +---------------------------------+ 0xF8000000
 *                            |                                 |
 *                            |    Remapped Physical Memory     | RW/-- KMEMSIZE
 *                            |                                 |
 *     KERNBASE ------------> +---------------------------------+ 0xC0000000
 *                            |        Invalid Memory (*)       | --/--
 *     USERTOP -------------> +---------------------------------+ 0xB0000000
 *                            |           User stack            |
 *                            +---------------------------------+
 *                            |                                 |
 *                            :                                 :
 *                            |         ~~~~~~~~~~~~~~~~        |
 *                            :                                 :
 *                            |                                 |
 *                            ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 *                            |       User Program & Heap       |
 *     UTEXT ---------------> +---------------------------------+ 0x00800000
 *                            |        Invalid Memory (*)       | --/--
 *                            |  - - - - - - - - - - - - - - -  |
 *                            |    User STAB Data (optional)    |
 *     USERBASE, USTAB------> +---------------------------------+ 0x00200000
 *                            |        Invalid Memory (*)       | --/--
 *     0 -------------------> +---------------------------------+ 0x00000000
 * (*) Note: The kernel ensures that "Invalid Memory" is *never* mapped.
 *     "Empty Memory" is normally unmapped, but user programs may map pages
 *     there if desired.
 *
 * */
```

### 创建并执行用户进程

确定了用户进程的执行代码和数据，以及用户进程的虚拟地址空间后，就可以创建用户进程了。~~本实验的第一个用户进程是第二个内核线程 initproc 通过把 hello 应用程序执行代码覆盖到 initproc 的用户虚拟空间来创建的。~~这里写的好像不太对，给出的示例是直接在 init_main 中执行 KERNEL_EXECVE 宏，但是现在的 ucore 代码中是在 init_main 中又创建了一个进程 user_main，在其中调用各种宏。

initproc 的执行主体就是 init_main 函数，在其中创建了一个以 user_main 为主函数的进程，之后再 user_main 中执行 KERNEL_EXECVE 宏：

```C
// kernel_execve - do SYS_exec syscall to exec a user program called by user_main kernel_thread
static int
kernel_execve(const char *name, unsigned char *binary, size_t size) {
    int ret, len = strlen(name);
    asm volatile (
        "int %1;"
        : "=a" (ret) // 输出值为 eax 的值
        : "i" (T_SYSCALL), "0" (SYS_exec), "d" (name), "c" (len), "b" (binary), "D" (size)
        //  依次为 系统调用的中断号、把 %0 初始化位 SYS_exec、%eax=name、%ecx=len、%ebx=binary、%edi=size
        : "memory"); // 表示修改了内存，之前缓存在寄存器中的值需要重新读取
    return ret;
}

#define __KERNEL_EXECVE(name, binary, size) ({                          \
            cprintf("kernel_execve: pid = %d, name = \"%s\".\n",        \
                    current->pid, name);                                \
            kernel_execve(name, binary, (size_t)(size));                \
        })

#define KERNEL_EXECVE(x) ({                                             \
            extern unsigned char _binary_obj___user_##x##_out_start[],  \
            // 这里的 ##x## 就是连起来构成变量名，比如 _binary_obj__user_hello_out_start，得到用户程序的位置和大小
                _binary_obj___user_##x##_out_size[];                    \
            __KERNEL_EXECVE(#x, _binary_obj___user_##x##_out_start,     \
                            _binary_obj___user_##x##_out_size);         \
        })

#define __KERNEL_EXECVE2(x, xstart, xsize) ({                           \
            extern unsigned char xstart[], xsize[];                     \
            __KERNEL_EXECVE(#x, xstart, (size_t)xsize);                 \
        })

#define KERNEL_EXECVE2(x, xstart, xsize)        __KERNEL_EXECVE2(x, xstart, xsize)

// user_main - kernel thread used to exec a user program
static int
user_main(void *arg) {
#ifdef TEST
    KERNEL_EXECVE2(TEST, TESTSTART, TESTSIZE);
#else
    KERNEL_EXECVE(hello);
#endif
    panic("user_main execve failed.\n");
}
```

缺省条件下就是执行宏 KERNEL_EXECVE，最后执行 SYS_exec 系统调用，将 `_binary_obj__user_hello_out_start`、`_binary_obj__user_hello_out_size` 两个全局变量作为参数，ucore 创建用户进程。

整体的过程为：`int 0x80 --(vector.S中对应中断号为128)--> __alltraps(trapentry.S) --> trap(trap.c) --> trap_dispatch(trap.c) --> syscall(syscall.c) --> sys_exec(syscall.c) --> do_execve(proc.c)`

最后通过 do_execve 函数完成用户进程的创建过程，首先为加载新的执行码做好用户态内存空间清空准备。由于此处的 initproc 是内核线程，所以 mm 为 NULL，整个处理都不会做，整个处理的操作与 do_exit 函数中开始的部分相同。接下来的一步是加载应用程序执行码到当前进程的新创建的用户态虚拟空间中。这里涉及到读 ELF 格式的文件，申请内存空间，建立用户态虚存空间，加载应用程序执行码等。load_icode 函数完成了整个复杂的工作。

```C
// do_execve - call exit_mmap(mm)&put_pgdir(mm) to reclaim memory space of current process
//           - call load_icode to setup new memory space accroding binary prog.
int
do_execve(const char *name, size_t len, unsigned char *binary, size_t size) {
    struct mm_struct *mm = current->mm;
    if (!user_mem_check(mm, (uintptr_t)name, len, 0)) {
        return -E_INVAL;
    }
    if (len > PROC_NAME_LEN) {
        len = PROC_NAME_LEN;
    }

    char local_name[PROC_NAME_LEN + 1];
    memset(local_name, 0, sizeof(local_name));
    memcpy(local_name, name, len);

    if (mm != NULL) {
        lcr3(boot_cr3);
        if (mm_count_dec(mm) == 0) {
            exit_mmap(mm);
            put_pgdir(mm);
            mm_destroy(mm);
        }
        current->mm = NULL;
    }
    int ret;
    if ((ret = load_icode(binary, size)) != 0) {
        goto execve_exit;
    }
    set_proc_name(current, local_name);
    return 0;

execve_exit:
    do_exit(ret);
    panic("already exit: %e.\n", ret);
}
```

load_icode 函数的相关工作在练习 1 中，需要的工作就是简单的设置一下 trapframe。

## 进程退出和等待

当进程执行完它的工作后，就需要执行退出操作，释放进程占用的资源。ucore 分了两步来完成这个工作，首先由进程本身完成大部分资源的占用内存回收工作，然后由此进程的父进程完成剩余资源占用内存的回收工作。为何不让进程本身完成所有的资源回收工作呢？这是因为进程要执行回收操作，就表明此进程还存在，还在执行指令，这就需要内核栈的空间不能释放，且表示进程存在的进程控制块不能释放。所以需要父进程来帮忙释放子进程无法完成的这两个资源回收工作。

为此在用户态的函数中提供了 exit 函数：

```C
// ./user/libs/ulib.c
void
exit(int error_code) {
    sys_exit(error_code);
    cprintf("BUG: exit failed.\n");
    while (1);
}

// ./kern/syscall/syscall.c
static int
sys_exit(uint32_t arg[]) {
    int error_code = (int)arg[0];
    return do_exit(error_code);
}
```

exit 函数传递 error_code 作为参数，通过 sys_exit 系统调用接口让操作系统帮助当前进程执行退出过程中的部分资源回收。sys_exit 最终调用 do_exit 函数完成对当前进程的退出处理，主要工作简单来说就是回收当前进程所占的大部分内存资源，并通知父进程完成最后的回收工作，具体流程如下：

```C
// ./process/proc.c
// do_exit - called by sys_exit
//   1. call exit_mmap & put_pgdir & mm_destroy to free the almost all memory space of process
//   2. set process' state as PROC_ZOMBIE, then call wakeup_proc(parent) to ask parent reclaim itself.
//   3. call scheduler to switch to other process
int
do_exit(int error_code) {
    if (current == idleproc) {
        panic("idleproc exit.\n");
    }
    if (current == initproc) {
        panic("initproc exit.\n");
    }

    struct mm_struct *mm = current->mm;
    // 在 lab4 的 preview 里已经知道，内核线程并不需要 mm_struct 结构体，所以是 NULL。
    // 此处表示是用户进程，则开始回收此用户进程所占用的用户虚拟内存空间
    if (mm != NULL) {
        lcr3(boot_cr3); // 切换到内核的页表，这样用户进程目前只能在内核虚拟地址空间执行，这是为了确保后续释放用户态内存和进程页表的工作能够正常执行
        // 如果 mm_struct 结构体的成员变量 mm_count 减 1 后为 0，表明这个 mm 没有再被其他进程共享，可以彻底释放进程所占的用户虚拟空间，则开始开始回收用户的内存资源
        if (mm_count_dec(mm) == 0) {
            // 调用 exit_mmap 函数释放 current->mm->vma链表中每个 vma 描述的进程合法空间中实际分配的内存，然后把对应的页表项清空，最后还把页表所占用的空间释放并把对应的页目录表项清空
            exit_mmap(mm);
            // 调用 put_pgdir 函数释放当前进程的页目录表项所占的内存
            put_pgdir(mm);
            // 调用 mm_destroy 函数释放 mm 中 vma 所占内存，最后释放 mm 所占内存
            mm_destroy(mm);
        }
        // 此时再将 current->mm 设置为 NULL，表示与当前进程相关的用户虚拟内存空间和对应的内存管理成员变量所占的内核虚拟内存空间已经回收完毕。
        current->mm = NULL;
    }
    // 设置当前进程的执行状态为 PROC_ZOMBIE，退出码为 error_code，表示进程已不能被调度了，需要此进程的父进程来做最后的回收工作，即回收描述此进程的内核栈和进程控制块。
    current->state = PROC_ZOMBIE;
    current->exit_code = error_code;

    bool intr_flag;
    struct proc_struct *proc;
    local_intr_save(intr_flag);
    {
        proc = current->parent;
        // 如果当前进程的父进程处于等待子进程的状态，则唤醒父进程，让父进程帮助自己完成最后的资源回收
        if (proc->wait_state == WT_CHILD) {
            wakeup_proc(proc);
        }
        // cpter: child, optr: older sibling, yptr: younger sibling
        // 如果当前进程还有子进程，则将子进程的父进程指针设置为 initproc 线程，并把子进程插入到 initproc 的子进程链表中，如果某个子进程的执行状态为 PROC_ZOMBIE，则需要唤醒 initproc 来完成对此子进程的最后回收工作。
        while (current->cptr != NULL) {
            proc = current->cptr;
            current->cptr = proc->optr;

            proc->yptr = NULL;
            if ((proc->optr = initproc->cptr) != NULL) {
                initproc->cptr->yptr = proc;
            }
            proc->parent = initproc;
            initproc->cptr = proc;
            if (proc->state == PROC_ZOMBIE) {
                if (initproc->wait_state == WT_CHILD) {
                    wakeup_proc(initproc);
                }
            }
        }
    }
    local_intr_restore(intr_flag);

    // 选择新的进程执行
    schedule();
    panic("do_exit will not return!! %d.\n", current->pid);
}
```

以上就是当前进程完成对自身大部分资源的回收过程，而父进程对子进程的回收工作要执行 wait 或 wait_pid 用户函数，最终访问 sys_wait 系统调用，执行 do_wait 函数，完成最后的回收操作：

```C
// do_wait - wait one OR any children with PROC_ZOMBIE state, and free memory space of kernel stack
//         - proc struct of this child.
// NOTE: only after do_wait function, all resources of the child proces are free.
int
do_wait(int pid, int *code_store) {
    struct mm_struct *mm = current->mm;
    if (code_store != NULL) {
        if (!user_mem_check(mm, (uintptr_t)code_store, sizeof(int), 1)) {
            return -E_INVAL;
        }
    }

    struct proc_struct *proc;
    bool intr_flag, haskid;
repeat:
    haskid = 0;
    // 如果 pid 非 0，表示只找 pid 对应的处于退出状态的子进程，否则找任意一个处于退出状态的子进程
    if (pid != 0) {
        proc = find_proc(pid);
        if (proc != NULL && proc->parent == current) {
            haskid = 1;
            if (proc->state == PROC_ZOMBIE) {
                goto found;
            }
        }
    }
    else {
        proc = current->cptr;
        for (; proc != NULL; proc = proc->optr) {
            haskid = 1;
            if (proc->state == PROC_ZOMBIE) {
                goto found;
            }
        }
    }
    // 如果找到了对应的子进程但是进程状态并不是 PROC_ZOMBIE，表明子进程未退出，则当前进程只好设置自己的执行状态为 PROC_SLEEPING，原因为 等待子进程退出，调度新的进程自行，如果被唤醒，则回到 repeat 的标记，重新找符合条件的子进程。
    if (haskid) {
        current->state = PROC_SLEEPING;
        current->wait_state = WT_CHILD;
        schedule();
        if (current->flags & PF_EXITING) {
            do_exit(-E_KILLED);
        }
        goto repeat;
    }
    return -E_BAD_PROC;

found:
    // 如果找到处于退出状态的子进程，需要当前进程完成对子进程的最终回收哦工作，即首先把子进程控制块从两个进程队列 proc_list 和 hash_list 删除，并释放子进程的内核堆栈和进程控制块。自此子进程彻底结束了它的执行过程，释放了它占用的所有资源。
    if (proc == idleproc || proc == initproc) {
        panic("wait idleproc or initproc.\n");
    }
    if (code_store != NULL) {
        *code_store = proc->exit_code;
    }
    local_intr_save(intr_flag);
    {
        unhash_proc(proc);
        remove_links(proc);
    }
    local_intr_restore(intr_flag);
    put_kstack(proc);
    kfree(proc);
    return 0;
}
```

## 系统调用实现

系统调用的存在在于运行在用户态的进程希望使用执行一些需要特权指令的任务，而要确保用户态程序无法执行特权指令，则通过系统调用的方式请求操作系统帮忙执行特权指令。

### 初始化系统调用对应的中断描述符

ucore 的初始化函数 kern_init 调用了 idt_init 来初始化中断描述符表，并设置一个特殊中断号的中断门，专门用户用户进程访问系统调用，也就是在实验最开始对 lab1 的代码进行补充的地方：

```C
SETGATE(idt[T_SYSCALL], 1, GD_KTEXT, __vectors[i], DPL_USER)
```

所有的系统调用通用一个中断号 0x80，一旦用户执行 `int 0x80`，CPU 就会从用户态切换到内核态，保存相关寄存器，并跳转到中断向量表 vector[T_SYSCALL] 处开始执行，有以下的执行路径：`int 0x80 --> vector[128](vector.S) --> __alltraps(trapentry.S) --> trap(trap.c) --> trap_dispatch(trap.c) --> syscall(syscall.c)`。最后，在 syscall 中根据系统调用号完成不同的系统调用服务。

### 建立系统调用的用户库准备

在操作系统中初始化好系统调用相关的中断描述符、中断处理起始地址等后，还需在用户态的应用程序中初始化好相关工作，简化应用程序访问系统调用的复杂性。为此在用户态建立了一个中间层，即简化的 libc 实现，在./user/libs/ulib.c 和 ./user/libs/syscall.c 中完成了对访问系统调用的封装。用户态最终的访问系统调用函数是 syscall，实现如下：

```C
static inline int
syscall(int num, ...) {
    va_list ap;
    va_start(ap, num);
    uint32_t a[MAX_ARGS];
    int i, ret;
    for (i = 0; i < MAX_ARGS; i ++) {
        a[i] = va_arg(ap, uint32_t);
    }
    va_end(ap);

    asm volatile (
        "int %1;"
        : "=a" (ret)
        : "i" (T_SYSCALL),
          "a" (num),
          "d" (a[0]),
          "c" (a[1]),
          "b" (a[2]),
          "D" (a[3]),
          "S" (a[4])
        : "cc", "memory");
    return ret;
}
```

可以看出，应用程序调用的 exit/fork/wait/getpid 等库函数最终都会调用 syscall 函数，实际上就是将系统调用好放到 eax，其他 5 个参数 a[0~4] 分别保存到 edx/ecx/ebx/edi/esi 寄存器中，即最多用 6 个寄存器来传递系统调用的参数，且系统调用的返回结果是 eax。

### 与用户进程相关的系统调用

本实验中，与进程相关的各个系统调用属性如下所示：

| SYSCALL    | means                                     | function                                                                       |
| ---------- | ----------------------------------------- | ------------------------------------------------------------------------------ |
| SYS_exit   | process exit                              | do_exit                                                                        |
| SYS_fork   | create child process, dup mm              | do_fork --> wakeup_proc                                                        |
| SYS_wait   | wait child process                        | do_wait                                                                        |
| SYS_exec   | after fork, process execute a new program | load a programe and refresh the mm                                             |
| SYS_yield  | process flag itself need resecheduling    | proc->nead_sched =1, then scheduler will rescheule this process                |
| SYS_kill   | kill process                              | do_kill --> proc->flags \|= PF_EXITING --> wakeup_proc --> do_wait --> do_exit |
| SYS_getpid | get the process's pid                     |                                                                                |

通过这些系统调用，可方便地完成从进程/线程创建到退出的整个运行过程。

### 系统调用的执行过程

与用户态的函数库调用执行过程相比，系统调用执行过程有以下几点主要的不同：

1. 不是通过 CALL 指令而是通过 INT 指令发起调用；
2. 不是通过 RET 指令而是通过 IRET 指令完成调用返回；
3. 当到达内核态后，操作系统需要严格检查系统调用传递的参数，确保不破坏整个系统的安全性；
4. 执行系统调用可导致进程等待某事件发生，从而可引起进程切换。

在练习 3 中将详细地分析 fork/exec/wait/exit 等系统调用的执行过程。
