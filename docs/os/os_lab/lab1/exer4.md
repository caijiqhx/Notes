# EXER4: 分析 bootloader 加载 ELF 格式的 OS 的过程

bootasm.S 和 bootmain.c 构成了一个 bootloader，练习 3 已经分析了 bootasm.S 部分是如何让 CPU 进入保护模式的，在其最后调用 bootmain 指令，进入 bootmain.c 中编写的程序，读入 ELF 格式的内核文件。

> 两种定址方式：
>
> - LBA (Logical Block Address) : 简单的定址方式，从 0 开始编号区块。
> - CHS (Cylinder-head-sector) : 即以柱面-磁头-扇区的定址方式。
>
> 两种方式的换算 #lba = (#c \* H + #h) \* S + #s - 1
>
> c、h、s 分别是柱面、磁头、扇区的编号，#lba 为逻辑区块编号，H 为每个磁柱的磁头数，S 为每磁道的扇区数。
>
> 两种数据传输方式：
>
> - PIO (Programmed input/output) : 所有的 IO 操作是通过 CPU 访问硬盘的 IO 地址寄存器完成。
> - DMA (Directory Memory Access) : 数据不经过 CPU 在磁盘和内存间传输。

LBA 与 CHS 在 PIO 模式下的磁盘读取：

第一个 IDE 通道通过访问 IO 地址 0x1f0-0x1f7 来实现，第二个 IDE 通道通过访问 0x170-0x17f 实现。

| registers    | address | features                                                                                         |
| ------------ | ------- | ------------------------------------------------------------------------------------------------ |
| data         | 0x1F0   | 读数据，当 0x1F7 不忙时可以读                                                                    |
| feature      | 0x1F1   | 读取时的错误信息，写入时的额外参数                                                               |
| sector count | 0x1F2   | 指定读写的扇区数                                                                                 |
| LBA low      | 0x1F3   | LBA 地址的 0~7 位                                                                                |
| LBA mid      | 0x1F4   | LBA 地址的 8~15 位                                                                               |
| LBA high     | 0x1F5   | LBA 地址的 16~23 位                                                                              |
| device       | 0x1F6   | LBA 地址的 24~27 位作为低 4 位，第 4 位为 0/1(主/从盘)<br>第 5、7 位为 1，第 6 位为 0/1(CHS/LBA) |
| command      | 0x1F7   | 读写命令，读取时，它第三位为 1 时表示硬盘做好数据交换准备，最高位为 1 时表示忙                   |

## Q1: bootloader 如何读取硬盘扇区的?

分析 bootmain.c 中函数：

```C
/* waitdisk - wait for disk ready */
static void
waitdisk(void) {
    while ((inb(0x1F7) & 0xC0) != 0x40)
        /* do nothing */;
}
```

waitdisk 函数检查 0x1F7 寄存器的最高位，当为最高位为 0 时即磁盘就绪。函数调用了 inb 函数，包括之后用到的 outb、insl 等函数，都定义在 ./libs/x86.h 中，都是在内联汇编中调用相应的汇编指令实现，以 inb 为例：

```C
static inline uint8_t
inb(uint16_t port) {
    uint8_t data;
    asm volatile ("inb %1, %0" : "=a" (data) : "d" (port));
    return data;
}
```

内联汇编 `inb %1,%0`，%0、%1 表示操作数，以出现顺序算，`=` 表示只写，a、d 为指定寄存器 eax、edx，从 edx 中的端口读一字节到 eax 中。

```C
/* readsect - read a single sector at @secno into @dst */
static void
readsect(void *dst, uint32_t secno) {
    // wait for disk to be ready
    waitdisk();

    outb(0x1F2, 1);                         // count = 1
    outb(0x1F3, secno & 0xFF);
    outb(0x1F4, (secno >> 8) & 0xFF);
    outb(0x1F5, (secno >> 16) & 0xFF);
    outb(0x1F6, ((secno >> 24) & 0xF) | 0xE0);
    outb(0x1F7, 0x20);                      // cmd 0x20 - read sectors

    // wait for disk to be ready
    waitdisk();

    // read a sector
    insl(0x1F0, dst, SECTSIZE / 4);
}
```

dst 为目标地址，secno 为按照 LBA 寻址方式的扇区编号。

1. waitdisk，等待磁盘就绪
2. outb 函数，设置 IO 地址寄存器，发出读取扇区的命令
3. waitdisk，等待磁盘就绪
4. insl 把磁盘扇区数据读到指定内存，内部实现用 repne 实现循环读取，一次读 4 个字节。

readsect 为读取一个扇区，读取任意长度的函数如下：

```C
/* *
 * readseg - read @count bytes at @offset from kernel into virtual address @va,
 * might copy more than asked.
 * */
static void
readseg(uintptr_t va, uint32_t count, uint32_t offset) {
    uintptr_t end_va = va + count;

    // round down to sector boundary
    // 向下舍入到扇区边界
    // 因为readsect函数读的是整个扇区，那么为了确保读的数据准确地在对应地址，舍入到扇区边界。不过实际运行中应该并没用到。
    va -= offset % SECTSIZE;

    // translate from bytes to sectors; kernel starts at sector 1
    uint32_t secno = (offset / SECTSIZE) + 1;

    // If this is too slow, we could read lots of sectors at a time.
    // We'd write more to memory than asked, but it doesn't matter --
    // we load in increasing order.
    for (; va < end_va; va += SECTSIZE, secno ++) {
        readsect((void *)va, secno);
    }
}
```

把要读的字节偏移转换为扇区编号，这里 +1 是因为 kernel 是从第 2 个扇区开始的，再调用 readsect 函数读数据。

## Q2: bootloader 是如何加载 ELF 格式的 OS?

bootmain 函数即为加载 kernel 文件的主体函数：

```C
#define ELFHDR          ((struct elfhdr *)0x10000)      // scratch space
/* bootmain - the entry of bootloader */
void
bootmain(void) {
    // 读elf文件的前八个扇区到暂存空间，用以校验文件头
    readseg((uintptr_t)ELFHDR, SECTSIZE * 8, 0);

    // 判断文件头
    if (ELFHDR->e_magic != ELF_MAGIC) {
        goto bad;
    }

    // 通过偏移获取 program header
    struct proghdr *ph, *eph;
    ph = (struct proghdr *)((uintptr_t)ELFHDR + ELFHDR->e_phoff);
    eph = ph + ELFHDR->e_phnum;

    //按照描述表中的信息读入elf文件
    for (; ph < eph; ph ++) {
        readseg(ph->p_va & 0xFFFFFF, ph->p_memsz, ph->p_offset);
    }

    // call the entry point from the ELF header
    // note: does not return
    // 跳转到内核入口函数，cpu交给内核
    ((void (*)(void))(ELFHDR->e_entry & 0xFFFFFF))();

bad:
    outw(0x8A00, 0x8A00);
    outw(0x8A00, 0x8E00);

    /* do nothing */
    while (1);
}
```

program header 描述与程序执行直接相关的目标文件结构信息，用来在文件中定位各个段的映像，同时包含其他一些用来为程序创建进程映像所必需的信息。可执行文件的程序头部是一个 program header 结构的数组， 每个结构描述了一个段或者系统准备程序执行所必需的其它信息。目标文件的 “段” 包含一个或者多个 “节区”（section） ，也就是“段内容（Segment Contents）” 。程序头部仅对于可执行文件和共享目标文件有意义。可执行目标文件在 ELF 头部的 e_phentsize 和 e_phnum 成员中给出其自身程序头部的大小。程序头部的数据结构如下表所示：

```C
struct proghdr {
  uint type;   // 段类型
  uint offset;  // 段相对文件头的偏移值
  uint va;     // 段的第一个字节将被放到内存中的虚拟地址
  uint pa;
  uint filesz;
  uint memsz;  // 段在内存映像中占用的字节数
  uint flags;
  uint align;
};
```

本练习看代码还是比较简单的，懒得用 gdb debug 了。
