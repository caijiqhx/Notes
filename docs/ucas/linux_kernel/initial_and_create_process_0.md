# 设备环境初始化及激活进程 0

从现在开始执行 main 函数！

系统达到怠速状态前所做的一切准备工作的核心目的就是让用户程序能够以进程的方式正常运行。本章讲解的内容就是为了实现这个目标，对设备环境进行初始化，并将激活第一个进程——进程 0。

Linux 0.11 是一个支持多进程的现代操作系统。这就意味着，各个用户进程在运行过程中，彼此不能相互干扰，这样才能保证进程在主机中正常地运算。然后，进程需要系统人为地给它设计一套边界来对其进行保护。这套边界就是系统为进程提供的进程管理信息数据结构，包括：task_struct、task[64] 和 GDT 等。

- task_struct 是每个进程所独有的结构，标识了进程的各项属性值，包括剩余时间片、进程执行状态、局部数据描述符表 LDT 和任务状态描述符表 TSS 等。
- task[64] 和 GDT 是为管理多进程提供的数据结构。task[64] 中存储所有进程的 task_struct 指针。如果操作系统需要对多个进程加以比较并选择，就可以遍历 task[64] 结构来实现。
- GDT 存储着一套对所有进程的索引结构。通过索引项，操作系统可以间接地与每个进程中的 LDT 和 TSS 建立关系。

本章还将讲解操作系统是如何对内存、CPU、串行口、显示器、键盘、硬盘、软盘等硬件进行设置，并将这些硬件所对应的中断服务程序与 IDT 相挂接，为进程 0 及其直接、间接创建的后续进程与外设沟通构建环境。

## 设置根设备、硬盘

首先初始化根设备和硬盘，用 bootsect 中写入机器系统数据 `0x901FC` 的根设备为软盘的信息，设置软盘为根设备，并用起始自 `0x90080` 的 32 字节的机器系统数据的硬盘参数信息设置内核中硬盘信息 drive\_info。

```c
#define DRIVE_INFO (*(struct drive_info *)0x90080)	// 硬盘参数表
#define ORIG_ROOT_DEV (*(unsigned short *)0x901FC)	// 根设备号
struct drive_info { char dummy[32]; } drive_info;  // 用于存放硬盘参数表信息
void main(void) {
    ROOT_DEV = ORIG_ROOT_DEV;		// ROOT_DEV 在 fs.h 中声明为 extern int
 	drive_info = DRIVE_INFO;
    ...
}
```

## 规划物理内存格局，设置缓冲区、虚拟盘、主内存

具体规划为：除内核代码和数据所占的内核空间之外，其余物理内存主要分三部分：

- 主内存区，进程代码运行的空间，也包括内核管理进程的数据结构；
- 缓冲区，主要作为主机与外设进行数据交互的中转站；
- 虚拟盘区，可选，可将外设上的数据先复制进虚拟盘区。

先根据内存大小对缓冲区和主内存区的位置和大小进行设置，代码如下：

```c
#define EXT_MEM_K (*(unsigned short *)0x90002)
...
static long memory_end = 0;                     // 机器具有的物理内存容量（字节数）
static long buffer_memory_end = 0;              // 高速缓冲区末端地址
static long main_memory_start = 0;              // 主内存（将用于分页）开始的位置
...
void main(void) {
    ...
	memory_end = (1<<20) + (EXT_MEM_K<<10);     // 内存大小=1Mb + 扩展内存(k)*1024 byte
	memory_end &= 0xfffff000;                   // 忽略不到4kb(1页)的内存数
	if (memory_end > 16*1024*1024)              // 内存超过16Mb，则按16Mb计
		memory_end = 16*1024*1024;
	if (memory_end > 12*1024*1024)              // 如果内存>12Mb,则设置缓冲区末端=4Mb 
		buffer_memory_end = 4*1024*1024;
	else if (memory_end > 6*1024*1024)          // 否则若内存>6Mb,则设置缓冲区末端=2Mb
		buffer_memory_end = 2*1024*1024;
	else
		buffer_memory_end = 1*1024*1024;        // 否则设置缓冲区末端=1Mb
	main_memory_start = buffer_memory_end;
}
```

1MB 以上都是扩展内存，扩展内存数存在之前 setup 保存的机器系统数据 0x90002 处。对于不同物理内存容量，缓冲区末端设置了不同的值，缓冲区的起始位置会在后面介绍。

## 设置虚拟盘空间并虚拟化

如果在 Makefile 中定义了 RAMDISK，则初始化虚拟盘，主内存将减少。代码如下：

```c
#ifdef RAMDISK
	main_memory_start += rd_init(main_memory_start, RAMDISK*1024);
#endif
...
// 块设备结构
struct blk_dev_struct {	
	void (*request_fn)(void);			// 请求操作的函数指针
	struct request * current_request;	// 当前正在处理的请求信息结构
};
// 块设备数组
struct blk_dev_struct blk_dev[NR_BLK_DEV] = {
	{ NULL, NULL },		/* no_dev */
	{ NULL, NULL },		/* dev mem */	// 内存
	{ NULL, NULL },		/* dev fd */	// 软驱
	{ NULL, NULL },		/* dev hd */	// 硬盘
	{ NULL, NULL },		/* dev ttyx */
	{ NULL, NULL },		/* dev tty */
	{ NULL, NULL }		/* dev lp */	// 打印机设备
};
#define MAJOR_NR 1
#define DEVICE_REQUEST do_rd_request
// 返回内存虚拟盘所需的内存量
long rd_init(long mem_start, int length)
{
	int	i;
	char	*cp;
	// 设置虚拟盘设备的请求项处理函数指针指向 do_rd_request
	blk_dev[MAJOR_NR].request_fn = DEVICE_REQUEST; 
	rd_start = (char *) mem_start;
	rd_length = length;
	cp = rd_start;
	for (i=0; i < length; i++)						// 虚拟盘区清零
		*cp++ = '\0';
	return(length);
}
```

rd_init 为虚拟盘区分配了 RAMDISK KB的数据，并置零。

## 内存管理结构 mem_map 初始化

确定了主内存区的起始位置，开始设置主内存区的管理结构。代码如下：

```c
	mem_init(main_memory_start,memory_end); // 主内存区初始化。mm/memory.c
...
// mm/memory.c
#define LOW_MEM 0x100000    
#define PAGING_MEMORY (15*1024*1024)
#define PAGING_PAGES (PAGING_MEMORY>>12)    
#define MAP_NR(addr) (((addr)-LOW_MEM)>>12)    
// 物理内存映射字节图（1字节代表1页内存）。每个页面对应的字节用于标志页面当前引
// 用（占用）次数。它最大可以映射15MB的内存空间。在初始化函数mem_init()中，对于
// 不能用做主内存页面的位置均都预先被设置成USED（100）.
static unsigned char mem_map [ PAGING_PAGES ] = {0,};   
// 物理内存管理初始化    
void mem_init(long start_mem, long end_mem)
{
	int i;

    // 首先将1MB到16MB范围内所有内存页面对应的内存映射字节数组项置为已占用状态 USED = 100
	HIGH_MEMORY = end_mem;                  // 设置内存最高端(16MB)
	for (i=0 ; i<PAGING_PAGES ; i++)
		mem_map[i] = USED;
    
	i = MAP_NR(start_mem);      // 主内存区其实位置处页面号
	end_mem -= start_mem;
	end_mem >>= 12;             // 主内存区中的总页面数
	while (end_mem-->0)
		mem_map[i++]=0;         // 主内存区页面对应字节值清零
}
```

调用 mem_init，使用内存映射数组 mem_map[] 管理 1MB 以上的页面，每个页面对应的字节表示页面引用次数，不能做主内存的页面数组值会设置为 USED。内存最多 15MB，页面数 3840 个。最后主内存区页面对应的 mem_map 值都置零。

![image-20201121123239787](image-20201121123239787.png)

操作系统对内核和用户进程采用两套不同的分页管理方法。内核的线性地址和物理地址完全一样，而用户进程线性地址和物理地址相差很大。主内存区采用专门管理用户进程的分页管理方法。

## 异常处理类中断服务程序挂接

用户进程和系统内核都要经常使用中断或遇到异常情况需要处理，下面将通过 trap_init 函数将中断、异常处理的服务程序与 IDT 进行挂接，逐步重建中断服务体系。代码如下：

```c
#define set_trap_gate(n,addr) \
	_set_gate(&idt[n],15,0,addr)

#define set_system_gate(n,addr) \
	_set_gate(&idt[n],15,3,addr)
// 异常(陷阱)中断程序初始化子程序。设置他们的中断调用门(中断向量)
void trap_init(void) {
	int i;

	set_trap_gate(0,&divide_error);		// 除零错误
	set_trap_gate(1,&debug);			// 单步调试
	set_trap_gate(2,&nmi);				// 不可屏蔽中断
	set_system_gate(3,&int3);	/* int3-5 can be called from all */
	set_system_gate(4,&overflow);		// 溢出
	set_system_gate(5,&bounds);			// 越界
	set_trap_gate(6,&invalid_op);		// 无效指令
	set_trap_gate(7,&device_not_available);			
	set_trap_gate(8,&double_fault);					
	set_trap_gate(9,&coprocessor_segment_overrun);
	set_trap_gate(10,&invalid_TSS);
	set_trap_gate(11,&segment_not_present);
	set_trap_gate(12,&stack_segment);
	set_trap_gate(13,&general_protection);
	set_trap_gate(14,&page_fault);
	set_trap_gate(15,&reserved);
	set_trap_gate(16,&coprocessor_error);
    // 下面把int17-47的陷阱门先均设置为reserved,以后各硬件初始化时会重新设置自己的陷阱门。
	for (i=17;i<48;i++)
		set_trap_gate(i,&reserved);
    // 设置协处理器中断0x2d(45)陷阱门描述符，并允许其产生中断请求。设置并行口中断描述符。
	set_trap_gate(45,&irq13);
	outb_p(inb_p(0x21)&0xfb,0x21);  // 允许8259A主芯片的IRQ2中断请求。
	outb(inb_p(0xA1)&0xdf,0xA1);    // 允许8259A从芯片的IRQ3中断请求。
	set_trap_gate(39,&parallel_interrupt); // 设置并行口1的中断0x27陷阱门的描述符。
}

```

set_trap_gate 与 set_system_gate 都使用了 IDT 中的 Trap Gate，主要区别在于前者设置的特权级为0，后者是3。因此断点陷阱中断 int3 、溢出中断 overflow 和边界出错中断 bounds 可以由任何程序产生。

\_set\_gate 宏通过拼接重组填充中断描述符，跟之前在 head 程序中填充 IDT 差不多。

```c
// 设置门描述符 
// 根据中断或异常处理程序偏移地址 addr、门描述符类型 type 和特权级信息 dpl
// 设置位于 gate_addr 处的门描述符
// %0 由 dpl, type 组成的标识字
// %1 描述符低 4 bytes 地址
// %2 描述符高 4 bytes 地址
// edx 偏移地址 addr
// eax 高字含有段选择符 0x8
// 最后要使 eax : 0008, low(addr); edx : high(addr), 1<<15 + dpl<<13 + type<<8
#define _set_gate(gate_addr,type,dpl,addr) \
__asm__ ("movw %%dx,%%ax\n\t" \
	"movw %0,%%dx\n\t" \
	"movl %%eax,%1\n\t" \
	"movl %%edx,%2" \
	: \
	: "i" ((short) (0x8000+(dpl<<13)+(type<<8))), \
	"o" (*((char *) (gate_addr))), \
	"o" (*(4+(char *) (gate_addr))), \
	"d" ((char *) (addr)),"a" (0x00080000))
```

32 位中断服务体系是为适应被动响应中断信号机制为建立的。硬件产生信号传达给 8259A，对信号进行初步处理并视 CPU 执行情况传递中断信号给 CPU；CPU 如果收到信号，就打断正在执行的程序并通过 IDT 找到具体的中断服务程序，执行完后返回刚才打断的程序点继续执行。

## 初始化块设备请求项结构

Linux 0.11 将外设分为块设备和字符设备。

- 块设备将存储空间分为若干同样大小的存储空间，每个块有块号，可以独立、随机读写。
- 字符设备以字符为单位进行 I/O 通信，如键盘、黑屏命令行显示器。

