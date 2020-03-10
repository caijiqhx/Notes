# EXER1: 分配并初始化一个进程控制块

实现 alloc_proc 函数，负责分配并返回一个新的 struct proc_struct 结构，用于存储新建立的内核线程的管理信息。

```C
// alloc_proc - alloc a proc_struct and init all fields of proc_struct
static struct proc_struct *
alloc_proc(void) {
    struct proc_struct *proc = kmalloc(sizeof(struct proc_struct));
    if (proc != NULL) {
    //LAB4:EXERCISE1 YOUR CODE
    /*
     * below fields in proc_struct need to be initialized
     *       enum proc_state state;                      // Process state
     *       int pid;                                    // Process ID
     *       int runs;                                   // the running times of Proces
     *       uintptr_t kstack;                           // Process kernel stack
     *       volatile bool need_resched;                 // bool value: need to be rescheduled to release CPU?
     *       struct proc_struct *parent;                 // the parent process
     *       struct mm_struct *mm;                       // Process's memory management field
     *       struct context context;                     // Switch here to run process
     *       struct trapframe *tf;                       // Trap frame for current interrupt
     *       uintptr_t cr3;                              // CR3 register: the base addr of Page Directroy Table(PDT)
     *       uint32_t flags;                             // Process flag
     *       char name[PROC_NAME_LEN + 1];               // Process name
     */
        memset(proc, 0, sizeof(struct proc_struct));     // 结构体中的大多数成员变量在初始化时置 0 即可
        proc->state = PROC_UNINIT;                       // 进程状态设置为 PROC_UNINIT，其实这个值本来就是 0，这句不写也行
        proc->pid = -1;                                  // pid 赋值为 -1，表示进程尚不存在
        proc->cr3 = boot_cr3;                            // 内核态进程的公用页目录表
    }
    return proc;
}
```

## Q: 请说明 proc_struct 中 struct context context 和 struct trapframe \*tf 成员变量含义和在本实验中的作用是啥？

context 即进程上下文，保存了进程切换前的寄存器

```C
struct context {
    uint32_t eip;
    uint32_t esp;
    uint32_t ebx;
    uint32_t ecx;
    uint32_t edx;
    uint32_t esi;
    uint32_t edi;
    uint32_t ebp;
};
```

./kern/process/switch.S 中的 switch_to 函数就是将八个寄存器保存到 from->context，从 to->context 中读取寄存器的值。然后通过 `push 0(%eax)` 将 to->context.eip 放到栈顶，ret 即 `pop eip` 让 eip 指向了 to 上次被打断的地方执行。

还有就是 copy_thread 函数，有 `proc->context.eip = (uintptr_t)forkret; proc->context.esp = (uintptr_t)(proc->tf);` 即设置从 forkret 开始执行，对应的栈为 proc->tf。

trapframe 结构体在 lab1 中已经见过了，保存了中断发生时进程的状态，用于恢复中断前的现场。

tf 指向中断帧的位置，在此处被传给了 forkret

```C
static void
forkret(void) {
    forkrets(current->tf);
}
```

forkret 定义在 trapentry.S 中，将 tf 指向的地址设置为新栈的地址，并跳转到了 \_\_trapret:

```assembly
.globl forkrets
forkrets:
    # set stack to this new process's trapframe
    movl 4(%esp), %esp
    jmp __trapret
```

\_\_trapret 利用 tf 指向的中断帧的值恢复了中断前的现场，（这里其实并不是因为中断发生的进程切换）：

```assembly
.globl __trapret
__trapret:
    # restore registers from stack
    popal

    # restore %ds, %es, %fs and %gs
    popl %gs
    popl %fs
    popl %es
    popl %ds

    # get rid of the trap number and error code
    addl $0x8, %esp
    iret
```

在 kernel_thread 中设置了 tf->tf_eip 为 kernel_thread_entry，接下来执行的是：

```assembly
.globl kernel_thread_entry
kernel_thread_entry:        # void kernel_thread(void)

    pushl %edx              # push arg
    call *%ebx              # call fn

    pushl %eax              # save the return value of fn(arg)
    call do_exit            # call do_exit to terminate current thread
```

即开始执行了指定的函数 fn。
