# Lab4 report

## 2019-11-20:04:09

练习 1 完成，很简单，就是初始化 proc_struct 结构体，只要看懂结构体各个成员变量的即可。

## 2019-11-26:20:09

练习 2、3 完成，一如既往地翻译注释就行了。。。get_pid 这个函数名感觉很别扭。。。

在给出的参考代码中，有以下的一系列操作：

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

为了弄清楚这是在干啥，首先分析一下使用的几个宏：

```C
/* intr_disable - disable irq interrupt */
void
intr_disable(void) {
    cli();
}

/* intr_enable - enable irq interrupt */
void
intr_enable(void) {
    sti();
}

static inline bool
__intr_save(void) {
    if (read_eflags() & FL_IF) {
        intr_disable();
        return 1;
    }
    return 0;
}

static inline void
__intr_restore(bool flag) {
    if (flag) {
        intr_enable();
    }
}

#define local_intr_save(x)      do { x = __intr_save(); } while (0)
#define local_intr_restore(x)   __intr_restore(x);
```

看到这就明白了，就是要先关中断然后再执行想要执行的代码，就不会被打断，保证操作的原子性。操作完成后再打开中断。
