# EXER6: 完善中断初始化和处理

> 操作系统三种中断
>
> - 中断 interrupt : 由 CPU 外部设备引起的外部事件如 I/O 中断、时钟中断、控制台中断等异步产生的与 CPU 的执行无关的中断。
> - 异常 exception : 在 CPU 执行指令期间检测到不正常的或非法的条件(如除零错、地址访问越界)所引起的内部事件。
> - 软中断 trap : 在程序中使用请求系统服务的系统调用而引发的事件。

## Q1: 中断描述符表中一个表项占多少字节? 其中哪几位代表中断处理代码的入口?

中断向量表定义在 ./kern/trap/tarp.c 中：

```C
static struct gatedesc idt[256] = {{0}};
// 结构体gatedesc的定义在 ./kern/mm/mmu.h 中

/* Gate descriptors for interrupts and traps */
struct gatedesc {
    unsigned gd_off_15_0 : 16;        // low 16 bits of offset in segment
    unsigned gd_ss : 16;            // segment selector
    unsigned gd_args : 5;            // # args, 0 for interrupt/trap gates
    unsigned gd_rsv1 : 3;            // reserved(should be zero I guess)
    unsigned gd_type : 4;            // type(STS_{TG,IG32,TG32})
    unsigned gd_s : 1;                // must be 0 (system)
    unsigned gd_dpl : 2;            // descriptor(meaning new) privilege level
    unsigned gd_p : 1;                // Present
    unsigned gd_off_31_16 : 16;        // high bits of offset in segment
};
// gatedesc 的定义使用了 bits-field，指定了各个成员变量的位数。
```

可见中断描述符表的一个表项占 64 位，即 8 字节。

中断处理代码的入口的段选择子在 gd_ss 字段，即 16~31 位，偏移地址的高 16 位在描述符的末尾 16 位，低 16 位在描述符的首 16 位。

## Q2: 请编程完善 kern/trap/trap.c 中对中断向量表进行初始化的函数 idt_init。在 idt_init 函数中，依次对所有中断入口进行初始化。使用 mmu.h 中的 SETGATE 宏，填充 idt 数组内容。每个中断的入口由 tools/vectors.c 生成，使用 trap.c 中声明的 vectors 数组即可。

./kern/trap/trap.c 中的 idt_init 注释写的很详细：

1. ISR(Interrupt Service Routine) 中断处理入口地址都在 vector.S 文件中的 `__vectors[]` 中。
   ```C
   extern uintptr_t __vectors[];
   ```
2. 把这些 ISR 的入口填入 idt，可以用 SETGATE 宏设置表项。

   SETGATE 定义在 ./kern/mm/mmu.h 中：

   ```C
   /* *
    * Set up a normal interrupt/trap gate descriptor
    *   - istrap: 1 for a trap (= exception) gate, 0 for an interrupt gate
    *   - sel: Code segment selector for interrupt/trap handler
    *   - off: Offset in code segment for interrupt/trap handler
    *   - dpl: Descriptor Privilege Level - the privilege level required
    *          for software to invoke this interrupt/trap gate explicitly
    *          using an int instruction.
    * */
   // 参数依次位 中断描述符、判断是异常还是中断、段选择子、偏移地址、权限
   #define SETGATE(gate, istrap, sel, off, dpl) {            \
       (gate).gd_off_15_0 = (uint32_t)(off) & 0xffff;        \
       (gate).gd_ss = (sel);                                \
       (gate).gd_args = 0;                                    \
       (gate).gd_rsv1 = 0;                                    \
       (gate).gd_type = (istrap) ? STS_TG32 : STS_IG32;    \
       (gate).gd_s = 0;                                    \
       (gate).gd_dpl = (dpl);                                \
       (gate).gd_p = 1;                                    \
       (gate).gd_off_31_16 = (uint32_t)(off) >> 16;        \
   }
   ```

3. 类似于 GDT，用 lidt 指令加载 LDT 到寄存器 LDTR。与 GDT 的 ldgt 类似，需要传 LDT 段界限和地址。此处就是用 idt_pd :
   ```C
   static struct pseudodesc idt_pd = {
    sizeof(idt) - 1, (uintptr_t)idt
   };
   ```

> 根据参考资料：
>
> 在保护模式下，最多会存在 256 个 Interrupt/Exception Vectors。范围[0，31]内的 32 个向量被异常 Exception 和 NMI 使用，但当前并非所有这 32 个向量都已经被使用，有几个当前没有被使用的，请不要擅自使用它们，它们被保留，以备将来可能增加新的 Exception。范围[32，255]内的向量被保留给用户定义的 Interrupts。

由此，实现 idt_init 代码如下：

```C
void idt_init(void) {
    extern uintptr_t __vectors[];
    int i;
    for(i = 0; i < sizeof(idt) / sizeof(struct gatedesc); i++ ) {
        if(i <= 31){
            // 前 32 个设置为 exception/traps
            SETGATE(idt[i], 1, GD_KTEXT, __vectors[i], DPL_KERNEL);
        }else {
            // 后面的设置为 interrupt
            SETGATE(idt[i], 0, GD_KTEXT, __vectors[i], DPL_KERNEL);
        }
    }
    // 从trap.h 看到 系统调用对应是 0x80，系统调用应该对应用户态权限
    SETGATE(idt[T_SYSCALL], 0, GD_KTEXT, __vectors[i], DPL_USER);
    lidt(&idt_pd);
}
```

## Q3: 请编程完善 trap.c 中的中断处理函数 trap，在对时钟中断进行处理的部分填写 trap 函数中处理时钟中断的部分，使操作系统每遇到 100 次时钟中断后，调用 print_ticks 子程序，向屏幕上打印一行文字”100 ticks”。

要补全的位置在 trap_dispatch 函数中，很简单，根据注释写就行：

```C
// ./kern/driver/clock.c 中的 ticks
volatile size_t ticks;

ticks++;
if( ticks == TICK_NUM ) {
    ticks = 0;
    print_ticks();
}
```
