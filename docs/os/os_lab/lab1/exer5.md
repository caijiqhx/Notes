# EXER5: 实现函数调用堆栈跟踪函数

在 ./kern/debug/kdebug.c 中实现 print_stackframe 函数。

注释写的很清楚：

```C
void print_stackframe(void) {
    uint32_t ebp = read_ebp(), eip = read_eip();
    int i, j;
    for (i = 0; i < STACKFRAME_DEPTH && ebp; ++i)
    {
        uint32_t *ptr = (uint32_t *)ebp;
        cprintf("ebp:0x%08x eip:0x%08x ", ebp, eip);
        cprintf("args:");
        for (j = 0; j < 4; ++j) {
            cprintf("0x%08x ", ptr[j + 2]);
        }
        cprintf("\n");
        print_debuginfo(eip - 1);
        eip = ptr[1];
        ebp = ptr[0];
    }
}
```

最后一行输出的调试信息：

```
ebp:0x00007bf8 eip:0x00007d72 args:0xc031fcfa 0xc08ed88e 0x64e4d08e 0xfa7502a8
    <unknow>: -- 0x00007d71 --
```

最底层应该就是 bootmain 函数，bootasm.S 中设置 ebp、esp 后直接调用，并没有传参。此时 ebp 为 0x7bf8。
