# EXER1: 使用 Round Robin 调度算法

## Q1: 请理解并分析 sched_class 中各个函数指针的用法，并结合 Round Robin 调度算法描 ucore 的调度执行过程

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

1. init: 初始化运行队列；
   ```C
   static void
   RR_init(struct run_queue *rq) {
       list_init(&(rq->run_list));
       rq->proc_num = 0;
   }
   ```
2. enqueue: 把一个 runnable 的进程放入队列，调用点有两个：

   - wakeup_proc 中，把刚刚产生的或从睡眠中被唤醒的进程加入就绪队列；
   - schedule 中，如果当前进程是 runnable 且不在队列中，即 running，则加入就绪队列。

   ```C
   static void
   RR_enqueue(struct run_queue *rq, struct proc_struct *proc) {
       assert(list_empty(&(proc->run_link)));
       // 将新进程添加到队尾
       list_add_before(&(rq->run_list), &(proc->run_link));
       // 如果时间片用完或者大于设定的最大时间片，则重置时间片
       // 如果时间片未用完那么就维持剩余的时间片数
       if (proc->time_slice == 0 || proc->time_slice > rq->max_time_slice) {
           proc->time_slice = rq->max_time_slice;
       }
       proc->rq = rq;
       rq->proc_num ++;
   }
   ```

3. dequeue: 把一个不再 runnable 的进程移除就绪队列，调用点有一处，就是在 schedule 中选出队列中适合现在运行的 runnable 程序移除就绪队列，调度执行。

   ```C
   static void
   RR_dequeue(struct run_queue *rq, struct proc_struct *proc) {
       assert(!list_empty(&(proc->run_link)) && proc->rq == rq);
       // 就是简单地从表中删除
       list_del_init(&(proc->run_link));
       rq->proc_num --;
   }
   ```

4. pick_next: 从就绪队列中选择适合现在运行的 runnable 进程，调用点就是上面提到的 schedule 的选择过程。

   ```C
   static struct proc_struct *
   RR_pick_next(struct run_queue *rq) {
       // 就是简单地选择第一个进程，如果没有进程可选则返回 NULL
       list_entry_t *le = list_next(&(rq->run_list));
       if (le != &(rq->run_list)) {
           return le2proc(le, run_link);
       }
       return NULL;
   }
   ```

5. proc_tick: 给调度算法提供信息，指示刚刚过去了一个时间片，在 trap_dispatch 时钟中断处调用。时间片消耗完就将 need_resched 置 1。

   ```C
   static void
   RR_proc_tick(struct run_queue *rq, struct proc_struct *proc) {
       if (proc->time_slice > 0) {
           proc->time_slice --;
       }
       if (proc->time_slice == 0) {
           proc->need_resched = 1;
       }
   }
   ```

Round Robin 算法下的 ucore 进程调度过程：

进程创建并初始化后调用 wakeup_proc 唤醒，加入就绪队列。以时间片控制进程执行，每次时钟中断，剩余时间片数减 1，时间片为 0 时将 need_resched 置 1，进入 schedule 将当前进程加入就绪队列，并选择队列首进程执行进程切换，如果无进程可选则执行 idleproc。

## Q2: 简要说明如何设计实现“多级反馈队列调度算法"

1. N 个优先级，run_queue 中维护 list_entry_t run_list[N]
2. proc_struct 中增加进程的优先级，即队列号。
3. 初始的时间片设置为 MAX_TIME_SLICE\<\<priority，proc_tick 中发现时间片用完，则降低优先级（+1），下次入队就进入下一级队列。
4. pick_next 根据优先级高低来选择进程。
