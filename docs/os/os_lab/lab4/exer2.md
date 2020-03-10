# EXER2: 为新创建的内核线程分配资源

创建一个内核线程需要分配和设置好很多资源。kernel_thread 函数通过调用 do_fork 函数完成具体内核线程的创建工作。do_fork 的作用是，创建当前内核线程的一个副本，它们的执行上下文、代码、数据都一样，但是存储位置不同。在这个过程中，需要给新内核线程分配资源，并且复制原进程的状态。在 preview 中已经了解了 do_fork 流程如下：

1. alloc_proc 函数，分配并初始化进程控制块；
2. setup_stack 函数，分配并初始化内核栈；
3. copy_mm 函数，根据 clone_flag 标志复制或共享进程内存管理结果；
4. copy_thread 函数，设置进程在内核（将来也包括用户态）正常运行和调度所需的中断帧和执行上下文；
5. 把设置好的进程控制块放入到 hash_list 和 proc_list 两个全局变量中；
6. 进程已准备好，设置为就绪态；
7. 返回子进程的 pid。

参考注释实现的代码如下：

```C
/* do_fork -     parent process for a new child process
 * @clone_flags: used to guide how to clone the child process
 * @stack:       the parent's user stack pointer. if stack==0, It means to fork a kernel thread.
 * @tf:          the trapframe info, which will be copied to child process's proc->tf
 */
int
do_fork(uint32_t clone_flags, uintptr_t stack, struct trapframe *tf) {
    int ret = -E_NO_FREE_PROC;
    struct proc_struct *proc;
    if (nr_process >= MAX_PROCESS) {
        goto fork_out;
    }
    ret = -E_NO_MEM;
    //LAB4:EXERCISE2 YOUR CODE
    /*
     * Some Useful MACROs, Functions and DEFINEs, you can use them in below implementation.
     * MACROs or Functions:
     *   alloc_proc:   练习 1 实现的创建并初始化一个进程控制块
     *   setup_kstack: 分配并初始化内核栈
     *   copy_mm:      根据 clone_flag 标志复制或共享进程内存管理结果
     *                 if clone_flags & CLONE_VM, then "share" ; else "duplicate"
     *   copy_thread:  设置进程在内核（将来也包括用户态）正常运行和调度所需的中断帧和执行上下文
     *   hash_proc:    基于 pid 将进程插入哈希表
     *   get_pid:      分配一个唯一的 pid （命名为 generate_pid 不是更好吗。。。
     *   wakeup_proc:  set proc->state = PROC_RUNNABLE
     * VARIABLES:
     *   proc_list:    the process set's list
     *   nr_process:   the number of process set
     */

    //    1. call alloc_proc to allocate a proc_struct
    if((proc = alloc_proc()) == NULL) {
        goto fork_out;
    }
    proc->parent = current; // 设置父进程
    //    2. call setup_kstack to allocate a kernel stack for child process
    if(setup_kstack(proc) != 0) {
        goto bad_fork_cleanup_proc;
    }
    //    3. call copy_mm to dup OR share mm according clone_flag
    if(copy_mm(clone_flags, proc) != 0) {
        goto bad_fork_cleanup_kstack;
    }
    //    4. call copy_thread to setup tf & context in proc_struct
    copy_thread(proc, stack, tf);
    //    5. insert proc_struct into hash_list && proc_list
    proc->pid = get_pid();
    hash_proc(proc);
    list_add(&proc_list, &(proc->list_link));
    nr_process ++;
    //    6. call wakeup_proc to make the new child process RUNNABLE
    wakeup_proc(proc);
    //    7. set ret vaule using child proc's pid
    ret = proc->pid;

fork_out:
    return ret;

bad_fork_cleanup_kstack:
    put_kstack(proc);
bad_fork_cleanup_proc:
    kfree(proc);
    goto fork_out;
}
```

需要注意的点就是在 preview 里也提到过了，如果前三步没有执行成功则需要做错误处理，把相关已经占有的内存释放。还有就是进程分配之后设置父进程为当前进程。

比较有趣的点就是在给出的参考代码中用到了如下的结构：

```C
bool intr_flag;
local_intr_save(intr_flag);
{
    proc->pid = get_pid();
    hash_proc(proc);
    list_add(&proc_list, &(proc->list_link));
    nr_process ++;
}
local_intr_restore(intr_flag);
```

这里似乎是关闭了中断确保这一段操作的原子性，不会发生竞争。

## Q: 请说明 ucore 是否做到给每个新 fork 的线程一个唯一的 id？请说明你的分析和理由。

可以做到，首先分析以下 get_pid 的代码（已经无数次吐槽这个函数名了。。。）：

```C
// get_pid - alloc a unique pid for process
static int
get_pid(void) {
    static_assert(MAX_PID > MAX_PROCESS);
    struct proc_struct *proc;
    list_entry_t *list = &proc_list, *le;
    static int next_safe = MAX_PID, last_pid = MAX_PID;
    if (++ last_pid >= MAX_PID) { // 循环分配，超出了上限就到 1，0 应该是 idleproc
        last_pid = 1;
        goto inside; // 归 1 后就无法保证 last_pid 到 next_safe 区间内的 pid 未被占用，直接跳过 if 进入内部
    }
    if (last_pid >= next_safe) { // 为了保证 pid 的唯一性，下面要逐个检查
    inside:
        next_safe = MAX_PID;
    repeat:
        le = list;
        while ((le = list_next(le)) != list) {
            proc = le2proc(le, list_link);
            if (proc->pid == last_pid) { // 如果 pid 冲突就 last_pid++ 再找一遍
                if (++ last_pid >= next_safe) {
                    if (last_pid >= MAX_PID) {
                        last_pid = 1;
                    }
                    next_safe = MAX_PID;
                    goto repeat;
                }
            }
            else if (proc->pid > last_pid && next_safe > proc->pid) { // 没有冲突
                next_safe = proc->pid; // 更新缩小安全区间
            }
        }
    }
    return last_pid;
}
```

通过 next_safe 划定一个不会发生冲突的区间，可以提高一点效率。反正就是用一段很长的代码保证了分配一个唯一的 pid。同时结合前面提到的，调用 get_pid 时关闭了中断保证原子性，不会发生竞争，进一步保证了 pid 的唯一性。
