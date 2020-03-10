# EXER2: 实现 Stride Scheduling 调度算法

Stride Scheduling 基本思想：

1. 每个 runnable 的进程设置一个当前状态 stride，表示该进程当前的调度权。另外定义其对应的 pass 值，表示对应进程在调度后，stride 需要进行的累加值。
2. 每次需要调度时，从当前 runnable 态的进程中选择 stride 最小的进程调度。
3. 对于获得调度的进程 P，将对应的 stride 加上其对应的步长 pass（只与进程的优先权有关系）。
4. 在一段固定的时间之后，回到 2.步骤，重新调度当前 stride 最小的进程。
5. 可以证明，如果令 P.pass =BigStride / P.priority 其中 P.priority 表示进程的优先权（大于 1），而 BigStride 表示一个预先定义的大常数，则该调度方案为每个进程分配的时间将与其优先级成正比

ucore 提供了斜堆实现优先队列。

还是按照 sched_class 的结构来实现算法：

```C
// max stride - min stride <= max pass <= BIGSTRIDE 则要差不溢出就定义 32 位全 1 就行
#define BIG_STRIDE  0x7FFFFFFF

/* The compare function for two skew_heap_node_t's and the
 * corresponding procs*/
// 比较斜堆节点的函数
static int
proc_stride_comp_f(void *a, void *b)
{
    struct proc_struct *p = le2proc(a, lab6_run_pool);
    struct proc_struct *q = le2proc(b, lab6_run_pool);
    int32_t c = p->lab6_stride - q->lab6_stride;
    if (c > 0) return 1;
    else if (c == 0) return 0;
    else return -1;
}

static void
stride_init(struct run_queue *rq) {
    list_init(&(rq->run_list));
    rq->lab6_run_pool = NULL;
    rq->proc_num = 0;
}

static void
stride_enqueue(struct run_queue *rq, struct proc_struct *proc) {
    // 合并堆
    rq->lab6_run_pool = skew_heap_insert(rq->lab6_run_pool, &proc->lab6_run_pool, proc_stride_comp_f);
    // 设置时间片
    if (proc->time_slice == 0 || proc->time_slice > rq->max_time_slice) {
       proc->time_slice = rq->max_time_slice;
    }
    proc->rq = rq;
    rq->proc_num++;
}

static void
stride_dequeue(struct run_queue *rq, struct proc_struct *proc) {
    // 从堆中删除
    rq->lab6_run_pool = skew_heap_remove(rq->lab6_run_pool, &proc->lab6_run_pool, proc_stride_comp_f);
    rq->proc_num--;
}

static struct proc_struct *
stride_pick_next(struct run_queue *rq) {
    // 选择根节点
    if (rq->lab6_run_pool == NULL) {
        return NULL;
    } else {
        struct proc_struct *proc = le2proc(rq->lab6_run_pool, lab6_run_pool);
        proc->lab6_stride += BIG_STRIDE / proc->lab6_priority;
        return proc;
    }
}

// 与RR一样
static void stride_proc_tick(struct run_queue *rq, struct proc_struct *proc)
```
