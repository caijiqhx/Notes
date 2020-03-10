# EXER1: 给未被映射的地址映射上物理页

完成 do_pgfault（mm/vmm.c）函数，给未被映射的地址映射上物理页。设置访问权限 的时候需要参考页面所在 VMA 的权限，同时需要注意映射物理页时需要操作内存控制 结构所指定的页表，而不是内核的页表。

```C
/* do_pgfault - interrupt handler to process the page fault execption
 * @mm         : the control struct for a set of vma using the same PDT 缺页异常的进程对应的 mm
 * @error_code : the error code recorded in trapframe->tf_err which is setted by x86 hardware
 * @addr       : the addr which causes a memory access exception, (the contents of the CR2 register)
 *
 * CALL GRAPH: trap--> trap_dispatch-->pgfault_handler-->do_pgfault
 */
int
do_pgfault(struct mm_struct *mm, uint32_t error_code, uintptr_t addr) {
    int ret = -E_INVAL;
    // 根据 addr 参数找到对应的 vma 结构
    struct vma_struct *vma = find_vma(mm, addr);

    pgfault_num++;
    // 未找到有效的 vma
    if (vma == NULL || vma->vm_start > addr) {
        cprintf("not valid addr %x, and  can not find it in vma\n", addr);
        goto failed;
    }
    // 根据 error_code 判断错误类型
    switch (error_code & 3) {
    default:
            /* error code flag : default is 3 ( W/R=1, P=1): write, present */
    case 2: /* error code flag : (W/R=1, P=0): write, not present */
        if (!(vma->vm_flags & VM_WRITE)) {
            cprintf("do_pgfault failed: error code flag = write AND not present, but the addr's vma cannot write\n");
            goto failed;
        }
        break;
    case 1: /* error code flag : (W/R=0, P=1): read, present */
        cprintf("do_pgfault failed: error code flag = read AND present\n");
        goto failed;
    case 0: /* error code flag : (W/R=0, P=0): read, not present */
        if (!(vma->vm_flags & (VM_READ | VM_EXEC))) {
            cprintf("do_pgfault failed: error code flag = read AND not present, but the addr's vma cannot read or exec\n");
            goto failed;
        }
    }
    /* IF (write an existed addr ) OR
     *    (write an non_existed addr && addr is writable) OR
     *    (read  an non_existed addr && addr is readable)
     * THEN
     *    continue process
     */
    uint32_t perm = PTE_U;
    // 读写属性
    if (vma->vm_flags & VM_WRITE) {
        perm |= PTE_W;
    }
    addr = ROUNDDOWN(addr, PGSIZE); // 页对齐

    ret = -E_NO_MEM; // 如果再出错，则是内存不足

    pte_t *ptep=NULL;
    /*LAB3 EXERCISE 1: YOUR CODE
    *
    * MACROs or Functions:
    *   get_pte : lab2 中实现的函数，通过 la 获取页表项，若不存在则创建一个
    *   pgdir_alloc_page : 调用 alloc_page 和 page_insert 函数分配页，建立 pa 和 la 的映射添加到页表
    *
    * DEFINES:
    *   VM_WRITE  : If vma->vm_flags & VM_WRITE == 1/0, then the vma is writable/non writable
    *   PTE_W           0x002                   // page table/directory entry flags bit : Writeable
    *   PTE_U           0x004                   // page table/directory entry flags bit : User can access
    * VARIABLES:
    *   mm->pgdir : the PDT of these vma
    *
    */
#if 0
    /*LAB3 EXERCISE 1: YOUR CODE*/
    ptep = ???              //(1) try to find a pte, if pte's PT(Page Table) isn't existed, then create a PT.
    if (*ptep == 0) {
                            //(2) if the phy addr isn't exist, then alloc a page & map the phy addr with logical addr

    }
    else {
    /*LAB3 EXERCISE 2: YOUR CODE
    * 当页存在于 swap 分区时，要根据 PTE 将页换入
    *
    *  MACROs or Functions:
    *    swap_in(mm, addr, &page) : alloc a memory page, then according to the swap entry in PTE for addr,
    *                               find the addr of disk page, read the content of disk page into this memroy page
    *    page_insert ： build the map of phy addr of an Page with the linear addr la
    *    swap_map_swappable ： set the page swappable
    */
        if(swap_init_ok) {
            struct Page *page=NULL;
                                    //(1）According to the mm AND addr, try to load the content of right disk page
                                    //    into the memory which page managed.
                                    //(2) According to the mm, addr AND page, setup the map of phy addr <---> logical addr
                                    //(3) make the page swappable.
        }
        else {
            cprintf("no swap_init_ok but ptep is %x, failed\n",*ptep);
            goto failed;
        }
   }
#endif
    if((ptep = get_pte(mm->pgdir, addr, 1)) == NULL) {
        cprintf("get_pte in do_pgfault failed\n");
        goto failed;
    }
    // 页表项为 0 表示没有与物理页面建立映射关系，pgdir_alloc_page 函数分配了一个页帧
    if(*ptep == 0) {
        if (pgdir_alloc_page(mm->pgdir, addr, perm) == NULL) {
            cprintf("pgdir_alloc_page in do_pgfault failed\n");
            goto failed;
        }
    }
    // 要处理的另一种情况，就是页存在于 swap 分区
    else {
        if(swap_init_ok) {
            struct Page *page = NULL;
            // 换入操作
            if ((ret = swap_in(mm, addr, &page)) != 0) {
                cprintf("swap_in in do_pgfault failed\n");
                goto failed;
            }
            page_insert(mm->pgdir, page, addr, perm); // 设置页表项
            swap_map_swappable(mm, addr, page, 1);    // 设置页可交换
            page->pra_vaddr = addr;                   // 设置页对应的虚拟地址
        }
        else {
            cprintf("no swap_init_ok but ptep is %x, failed\n",*ptep);
            goto failed;
        }
    }
    ret = 0;
failed:
    return ret;
}
```

这里涉及到的 pgdir_alloc_page 函数：

```C
// pgdir_alloc_page
// 分配一个页并且设置 la 与 pa 的映射关系
struct Page *
pgdir_alloc_page(pde_t *pgdir, uintptr_t la, uint32_t perm) {
    struct Page *page = alloc_page(); // 分配一个页
    if (page != NULL) {
        // page_insert 通过 la 找到 ptep 地址并设置值
        if (page_insert(pgdir, page, la, perm) != 0) {
            free_page(page);
            return NULL;
        }
        if (swap_init_ok){
            // 实现页换入换出
            swap_map_swappable(check_mm_struct, la, page, 0);
            page->pra_vaddr=la;
            assert(page_ref(page) == 1);
        }

    }

    return page;
}
```

## Q1: 请描述页目录项（Page Directory Entry）和页表项（Page Table Entry）中组成部分对 ucore 实现页替换算法的潜在用处

在 lab2 中已经回答了关于 PDE 和 PTE 的组成部分的问题，PDE 和 PTE 高 20 位为物理地址，低 12 位为标志位。

对于页替换算法有用的位：

| 位  | 名称 | 含义                                            | 用法                                       |
| --- | ---- | ----------------------------------------------- | ------------------------------------------ |
| 0   | P    | 页面是否在内存中，若此位为 0 则其他位可随意使用 | 存放交换分区信息，可用于页替换算法实现     |
| 5   | A    | 在上次清零之后，该页是否被访问（读或写）过      | 可用于时钟替换算法和拓展时钟替换算法的实现 |
| 6   | D    | 在上次清零之后，该页是否被写过                  | 可用于拓展时钟替换算法实现                 |

## Q2: 如果 ucore 的缺页服务例程在执行过程中访问内存，出现了页访问异常，请问硬件要做哪些事情?

缺页服务例程执行过程中访问内存出现的页访问异常与其他程序出现页访问异常没什么区别。硬件都是将发生异常的线性地址放入 CR2 寄存器，在栈中依次 压入 `eflags、cs、eip、error_code`。然后中断号为 14，将对应的中断服务例程的地址加载到 cs、eip 中，开始执行中断服务例程。
