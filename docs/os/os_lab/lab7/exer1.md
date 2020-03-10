# EXER1: 理解内核级信号量的实现和基于内核级信号量的哲学家就餐问题

## Q1: 给出内核级信号量的设计描述，并说明其大致执行流程

内核级信号量的相关数据结构：

```C
// 等待队列
typedef struct {
    list_entry_t wait_head;
} wait_queue_t;

// 等待项
typedef struct {
    struct proc_struct *proc; // 等待的进程 proc
    uint32_t wakeup_flags;    // 进程进入等待的原因标记
    wait_queue_t *wait_queue; // 等待项所在的队列
    list_entry_t wait_link;   // 组织等待队列的连接
} wait_t;

// 信号量
typedef struct {
    int value;               // 计数值
    wait_queue_t wait_queue; // 等待队列
} semaphore_t;
```

信号量最主要的还是 PV 操作：

```C
// up 相当于信号量的 V 操作
static __noinline void __up(semaphore_t *sem, uint32_t wait_state) {
    bool intr_flag;
    local_intr_save(intr_flag); // 中断保证原子性
    {
        wait_t *wait;
        // wait_queue 为 FIFO，在信号量对应的等待队列中获取等待项
        if ((wait = wait_queue_first(&(sem->wait_queue))) == NULL) {
            sem->value ++; // 资源没人要，
        }
        else {
            // 如果有等待信号量的进程，则唤醒进程 wakeup_wait -> wakeup_proc 添加进程到就绪队列
            assert(wait->proc->wait_state == wait_state);
            wakeup_wait(&(sem->wait_queue), wait, wait_state, 1);
        }
    }
    local_intr_restore(intr_flag);
}

// down 相当于信号量的 P 操作
static __noinline uint32_t __down(semaphore_t *sem, uint32_t wait_state) {
    bool intr_flag;
    local_intr_save(intr_flag);
    // 可以提供资源
    if (sem->value > 0) {
        sem->value --;
        local_intr_restore(intr_flag);
        return 0;
    }
    // 当前进程进入等待
    wait_t __wait, *wait = &__wait;
    wait_current_set(&(sem->wait_queue), wait, wait_state);
    local_intr_restore(intr_flag);

    // 当前进程进入 PROC_SLEEPING 状态，让出 cpu 控制权
    schedule();

    // 被唤醒后需要移除等待队列
    local_intr_save(intr_flag);
    wait_current_del(&(sem->wait_queue), wait);
    local_intr_restore(intr_flag);

    //
    if (wait->wakeup_flags != wait_state) {
        return wait->wakeup_flags;
    }
    return 0;
}
```

up 操作在有等待进程时唤醒等待队列头的进程，若无，资源+1；down 操作在资源计数器=0 时阻塞并把自身加入等待队列队尾，否则资源-1。

哲学家就餐问题的流程：

```C
int state_sema[N]; // 记录每个人状态的数组
semaphore_t mutex; // 锁
semaphore_t s[N];  // 每个哲学家一个信号量

struct proc_struct *philosopher_proc_sema[N];

void phi_test_sema(i)
{
    // 想吃且两边没人吃
    if(state_sema[i] == HUNGRY && state_sema[LEFT] != EATING
        && state_sema[RIGHT] != EATING)
    {
        state_sema[i]=EATING;
        up(&s[i]); // 第 i 个信号量资源已顺备好
    }
}

void phi_take_forks_sema(int i)
{
        down(&mutex);
        state_sema[i] = HUNGRY;
        phi_test_sema(i);
        up(&mutex);
        down(&s[i]);    // 使用资源，无法使用则阻塞

void phi_put_forks_sema(int i)
{
        down(&mutex);
        state_sema[i]=THINKING;
        phi_test_sema(LEFT);    // 释放左资源
        phi_test_sema(RIGHT);   // 释放右资源
        up(&mutex);
}

int philosopher_using_semaphore(void * arg)
{
    int i, iter=0;
    i=(int)arg;
    while(iter++ < TIMES) {
        do_sleep(SLEEP_TIME);   // 思考
        phi_take_forks_sema(i); // 获取资源或阻塞
        do_sleep(SLEEP_TIME);   // 吃
        phi_put_forks_sema(i);  // 释放资源
    }
    return 0;
}
```

简单描述流程就是：哲学家需要筷子时，先上锁，在临界区检测左右状态，如果自己可以就餐就 V 一次自己的信号量，在临界区外，down 一次自己的信号量。刚才的一次可能的 V，或者其他哲学家放下叉子的 V，为这次 down 提供所需的资源。哲学家需要放下筷子时，先上锁，在临界区内检测左右状态，如果左右邻居可以就餐，则 V 对应的资源。

## Q2: 给出给用户态进程/线程提供信号量机制的设计方案，并比较说明给内核级提供信号量机制的异同。

内核态信号量封装成系统调用供用户进程使用。

futex，用户态和内核态混合的同步机制。在用户态检查，如果有竞争才执行系统调用。
