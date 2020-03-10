# Lab5 report

## 2019-12-24:11:42

终于考完研了。。。继续做实验。

练习 1，很简单，主要是要看懂整个调用的过程，大概过程就是：硬构造 idleproc --> initproc --> init_main 创建新进程 --> user_main --> kernel_execve --> sys_call --> do_execve --> load_icode。文档里面是按照将 initproc 直接作为用户程序 hello 的容器来解释的，上面这个过程是按照实际项目代码的流程写的。区别就是在 initproc 下又创建一个进程，其主函数为 user_main，以此作为后续调用的入口。

## 2019-12-25:19:10

练习 2、3 完成，主要就是了解系统调用的执行过程。通过 `int 0x80 --> vector[128](vector.S) --> __alltraps(trapentry.S) --> trap(trap.c) --> trap_dispatch(trap.c) --> syscall(syscall.c)` 这样的路径，然后根据 eax 中的系统调用号的不同提供不同的服务。

ucore 中的一些系统调用：

| SYSCALL    | means                                     | function                                                                       |
| ---------- | ----------------------------------------- | ------------------------------------------------------------------------------ |
| SYS_exit   | process exit                              | do_exit                                                                        |
| SYS_fork   | create child process, dup mm              | do_fork --> wakeup_proc                                                        |
| SYS_wait   | wait child process                        | do_wait                                                                        |
| SYS_exec   | after fork, process execute a new program | load a programe and refresh the mm                                             |
| SYS_yield  | process flag itself need resecheduling    | proc->nead_sched =1, then scheduler will rescheule this process                |
| SYS_kill   | kill process                              | do_kill --> proc->flags \|= PF_EXITING --> wakeup_proc --> do_wait --> do_exit |
| SYS_getpid | get the process's pid                     |                                                                                |

犯了个巨蠢的错误。。。在 trap.c 中设置系统调用的中断描述符时，写成了 `SETGATE(idt[T_SYSCALL], 1, GD_KTEXT, __vectors[i], DPL_USER);` 。。。导致 grade 的时候一顿报错，最后一点点比对才发现，视力是个好东西

challenge
