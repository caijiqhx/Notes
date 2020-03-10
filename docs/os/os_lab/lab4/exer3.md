# EXER3: 阅读代码，理解 proc_run 函数和它调用的函数如何完成进程切换的

```C
// proc_run - make process "proc" running on cpu
// NOTE: before call switch_to, should load  base addr of "proc"'s new PDT
void
proc_run(struct proc_struct *proc) {
    if (proc != current) { // 如果 proc 就是当前进程，则不需要调度
        bool intr_flag;
        struct proc_struct *prev = current, *next = proc;
        local_intr_save(intr_flag); // 前面也见过这个，禁止中断，上锁
        {
            current = proc; // 更新当前进程
            load_esp0(next->kstack + KSTACKSIZE); // 更新 tss 中 ring 0 的 esp 为 proc 对应的内核栈的栈顶
            lcr3(next->cr3); // 加载 proc 的页目录表到 cr3
            switch_to(&(prev->context), &(next->context)); // 切换进程，switch.S 中的 switch_to 函数，就是设置 context 中的寄存器
        }
        local_intr_restore(intr_flag); // 恢复中断，解锁
    }
}
```

## Q1: 在本实验的执行过程中，创建且运行了几个内核线程？

两个，第 0 个进程 idleproc，它的工作就是不断查询能够执行的进程后让调度器调度执行。第 1 个进程 initproc 在本次实验中它就是输出了一句 hello word。

## Q2: 语句 local_intr_save(intr_flag);....local_intr_restore(intr_flag);在这里有何作用?请说明理由

这个在前面练习 2 的时候已经遇到了，就是先禁止中断，等执行完需要的操作后再恢复中断，用以保证操作的原子性。
