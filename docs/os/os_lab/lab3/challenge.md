# Challenge: Extended Clock

在 preview 里已经了解了 Extended Clock 页置换算法

主要是维护 clock 指针，对 map_swappable 和 swap_out_victim 两个函数修改，具体过程：

1. 在初始化时，调用 map_swappable 函数将物理页面装入环形链表；
2. 当所有物理内存分配完毕，就不需要再对链表进行插入删除操作，直接修改值即可。

算法在遍历时同时查询访问位和修改位，根据两位的不同，有以下结果：

| Access/Dirty(Old) | Access/Dirty(New)       |
| ----------------- | ----------------------- |
| 0/0               | swap out, return        |
| 0/1               | 0/0, 将页写入 swap 分区 |
| 1/0               | 0/0                     |
| 1/1               | 0/1                     |

参考 FIFO 算法的实现容易修改主要函数，主要在于实现 check 函数。

首先要熟悉 ./kern/mm/swap.c 中的 check_swap 函数流程：

1. 调用 mm_create 建立 mm 变量，并调用 vma_create 创建 vma 变量，设置合法的访问范围为 4KB~24KB；
2. 调用 free_page 等操作，模拟形成一个只有 4 个空闲 physical page；并设置了从 4KB~24KB 的连续 5 个虚拟页的访问操作；
3. 设置记录缺页次数的变量 pgfault_num=0，执行 check_content_set 函数，使得起始地址分别对起始地址为 0x1000, 0x2000, 0x3000, 0x4000 的虚拟页按时间顺序先后写操作访问，由于之前没有建立页表，所以会产生 page fault 异常，这些从 4KB~20KB 的 4 虚拟页会与 ucore 保存的 4 个物理页帧建立映射关系；
4. 然后对虚页对应的新产生的页表项进行合法性检查；
5. 然后进入测试页替换算法的主体，执行函数 check_content_access，并进一步调用到 swap_manager 中的 check_swap 函数。如果通过了所有的 assert，则进一步表示页替换算法基本正确实现；
6. 最后恢复 ucore 环境。

check 程序按照视频课程中演示的样例

内存中的页面初始状态, page(A/D):
a(0/0), b(0/0), c(0/0), d(0/0) <==> ^a00, b00, c00, d00

要注意的是 clock 指针的位置，用 ^ 表示

下面开始一系列访问请求：

- read c: ^a00, b00, c10, d00
- write a: ^a11, b00, c10, d00
- read d: ^a11, b00, c10, d10
- write b: ^a11, b11, c10, d10
- read e: page fault -> exclock -> a00, b00, e10, ^d00
- read b: a00, b10, e10, ^d00
- write a: a11, b10, e10, ^d00
- read b: a11, b10, e10, ^d00
- read c: page fault -> exclock -> ^a11, b10, e10, c10
- read d: page fault -> exclock -> a00, d10, ^e00, c00
