# EXER2: 完成内核级条件变量和基于内核级条件变量的哲学家就餐问题

## Q1: 给出内核级条件变量的设计描述，并说明其大致执行流程。

管程相关的数据结构：

```C
// 条件变量
typedef struct condvar{
    semaphore_t sem;    // 底层实现机制为信号量
    int count;          // 正在等待条件变量的进程数，为 0 时 signal 为空操作
    monitor_t * owner;  // 所属管程
} condvar_t;

// 管程
typedef struct monitor{
    semaphore_t mutex;  // 锁
    semaphore_t next;   // 因为发出信号而被阻塞的进程等待这个信号量
    int next_count;     // 因发出信号被阻塞的进程数
    condvar_t *cv;      // 条件变量
} monitor_t;
```

管程的 wait 和 signal 操作，wait 用于进程因无法获取所需的资源时将自己阻塞，signal 用于另一个进程释放或生成相关资源后唤醒 wait 的进程。

```C
void
cond_wait (condvar_t *cvp) {
   monitor_t *mt = cvp->owner;
   cvp->count++;
   // 自身开始等待之前现场时唤醒一个进程
   if (mt->next_count > 0) {
        up(&mt->next);  // 当前有因为发出信号而等待的进程，优先唤醒它
    } else {
        up(&mt->mutex); // 放弃自身对管程的占有权
    }
    down(&cvp->sem);    // 自身进入等待
    cvp->count--;
}

void
cond_signal (condvar_t *cvp) {
    monitor_t *mt = cvp->owner;
    if(cvp->count > 0) {
        mt->next_count++;
        up(&cvp->sem);      // 唤醒，并不是立即开始运行，而是加入就队列
        down(&mt->next);    // 阻塞自己，等待条件同步
        mt->next_count--;
    }
}
```

实现的是 Hoare 管程，进程在发出信号后，下一个在临界区内运行的必须是等待信号的进程。

条件变量实现哲学家就餐问题的过程：

```C
struct proc_struct *philosopher_proc_condvar[N];
int state_condvar[N];
monitor_t mt, *mtp=&mt;

void phi_test_condvar (i) {
    if(state_condvar[i] == HUNGRY && state_condvar[LEFT] != EATING
             && state_condvar[RIGHT] != EATING) {
        state_condvar[i] = EATING;
        cond_signal(&mtp->cv[i]); // 能获取资源则唤醒
    }
}


void phi_take_forks_condvar(int i) {
    down(&(mtp->mutex));
    state[i] = HUNGRY;
    phi_test_condvar(i);
    if(state_condvar[i] != EATING) {
        cond_wait(&mtp->cv[i]); // 如果不能拿，就阻塞自己
    }
    if(mtp->next_count>0)
        up(&(mtp->next));
    else
        up(&(mtp->mutex));
}

void phi_put_forks_condvar(int i) {
    down(&(mtp->mutex));
    state[i] = THINKING;
    phi_test_condvar(LEFT);
    phi_test_condvar(RIGHT);
    if(mtp->next_count>0)
       up(&(mtp->next));
    else
       up(&(mtp->mutex));
}

int philosopher_using_condvar(void * arg) {
    int i, iter=0;
    i=(int)arg;
    while(iter++ < TIMES) {
        do_sleep(SLEEP_TIME);       // 思考
        phi_take_forks_condvar(i);  // 获取叉子，或阻塞
        do_sleep(SLEEP_TIME);       // 吃
        phi_put_forks_condvar(i);   // 放下叉子
    }
    return 0;
}
```

## Q2: 给出给用户态进程/线程提供条件变量机制的设计方案，并比较说明给内核级提供条件变量机制的异同。

与练习 1 差不多，可以通过系统调用提供接口，内核检查在管程出入的状态设置。

## Q3: 能否不用基于信号量机制来完成条件变量？如果不能，请给出理由，如果能，请给出设计说明和具体实现。

条件变量维护进程等待队列，可以直接用等待队列和锁机制来完成条件变量。
