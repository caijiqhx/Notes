# Challenge

## Q1: 增加一用户态函数，当内核初始完毕后，可从内核态返回到用户态的函数，而用户态的函数又通过系统调用得到内核态的服务

即实现内核态到用户态，在切换会内核态的过程。

首先通过一个 trapframe 结构体保存当前被打断的程序的现场（即一些寄存器的值），以便后续恢复。

```C
// ./kern/trap/trap.h

struct trapframe {
    struct pushregs tf_regs;
    uint16_t tf_gs;
    uint16_t tf_padding0;
    uint16_t tf_fs;
    uint16_t tf_padding1;
    uint16_t tf_es;
    uint16_t tf_padding2;
    uint16_t tf_ds;
    uint16_t tf_padding3;
    uint32_t tf_trapno;
    /* below here defined by x86 hardware */
    uint32_t tf_err;
    uintptr_t tf_eip;
    uint16_t tf_cs;
    uint16_t tf_padding4;
    uint32_t tf_eflags;
    /* below here only when crossing rings, such as from user to kernel */
    uintptr_t tf_esp;
    uint16_t tf_ss;
    uint16_t tf_padding5;
} __attribute__((packed));
```

栈是从高地址到低地址生长，结构体内成员的地址递增，即结构体从后往前填充。中断发生时，如果发生特权级的转换（从内核态转换到用户态），则先将 `ss, esp` 压栈，然后再将 `eflags, cs, eip` 压栈。之后填入错误编码 `error_code`，无错误则为 0，然后填入 `trapno` 即 vector 中的下标。最后调用 trapentry.S 定义的 `__alltraps`，依次填入`ds, es, fs, gs`， pushal 依次将`eax, ecx, edx, ebx, 旧的 esp, ebp, esi, edi` 压栈。

压栈之后，esp 即指向了 trapframe 结构体的首地址，将 esp 作为 trap 函数的参数入栈。然后调用 trap_dispatch，根据 trapno 索引处理代码。trap 函数返回后，pop 出刚才入栈的地址设置为新的栈顶。然后执行 `__trapret` 按顺序恢复寄存器，iret 恢复 `cs, eflag, eip`。

1. 内核态切换到用户态

   首先需要将 `ss, esp` 入栈，然后触发中断：

   ```C
   // ./kern/init/init.c
   static void lab1_switch_to_user(void) {
       asm volatile (
            "movl %%esp,%%eax\n"    // 先保存原始的 esp
            "pushl %0\n"            // 将 ss 的值即 USER_DS 压栈
            "pushl %%eax\n"         // 将原始 esp 入栈
            "int %1\n"              // 触发中断
            :: "i"(USER_DS), "i"(T_SWITCH_TOU)
       );
   }
   ```

   在 ./kern/trap/trap.c 的 trap_dispatch 中 `case T_SWITCH_TOU` 处理中断：

   ```C
   // 设置 trapframe 各个数据成员
   case T_SWITCH_YOU:
        tf->tf_cs = USER_CS;
        tf->tf_ds = tf->tf_es = USER_DS;
        tf->tf_eflags |= FL_IOPL_MASK;  //为了正确输出还要设置权限，来自参考答案
        break;
   ```

2. 用户态切换到内核态
   首先需要需要设置一个用户态可以使用的中断：

   ```C
   // ./kern/trap/trap.c
   // idt_init
   SETGATE(idt[T_SWITCH_TOK], 1, GD_KTEXT, __vectors[T_SWITCH_TOK], DPL_USER);
   ```

   然后再用户态触发中断：

   ```C
   static void lab1_switch_to_kernel(void) {
       asm volatile (
           "int %0\n"
           "movl %%ebp, %%esp\n"
           :: "i"(T_SWITCH_TOK)
       );
   }
   ```

   在 trap_dispatch 中处理，恢复寄存器到内核态：

   ```C
   case T_SWITCH_TOK:
        tf->tf_cs = KERNEL_CS;
        tf->tf_ds = tf->tf_es = tf->tf_ss = KERNEL_DS;
        tf->tf_eflags &= ~FL_IOPL_MASK; // 恢复输出权限
        break;
   ```

由此，内核态-->用户态-->内核态的过程实现。执行 `make grade` 后正确。

## Q2: 用键盘实现用户模式内核模式切换。具体目标是：“键盘输入 3 时切换到用户模式，键盘输入 0 时切换到内核模式”。

实现了之前的问题，这个就可以用上面的函数来实现。也就是我们把 ./kern/init/init.c 中的 switch_to_user、switch_to_kernel 添加到 trap.c 中并在 trap_dispatch 中的 `case IRQ_OFFSET + IRQ_KBD` 中调用这两个函数就行了。

emmm，看起来这样就行了，但是改完代码后，运行 make qemu，按 3 确实执行了切换到用户态的函数，然后就停住了。。。应该是切换到用户态之后没有命令执行了。所以我直接让它切换回内核态了。。。

```C
 case IRQ_OFFSET + IRQ_KBD:
    c = cons_getc();
    if( c == '3' ){
        cprintf("switch to user 333\n");
        lab1_switch_to_user();
        print_trapframe(tf);
        lab1_switch_to_kernel();
    }else if( c == '0' ){
        cprintf("switch to kernel 000\n");
        lab1_switch_to_kernel();
        print_trapframe(tf);
    }
    cprintf("kbd [%03d] %c\n", c, c);
    break;
```
