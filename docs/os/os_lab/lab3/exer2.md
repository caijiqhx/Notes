# EXER2: 补充完成基于 FIFO 的页面替换算法

完成 do_pgfault 函数后，要实现 FIFO 算法的 map_swappable 和 swap_out_victim 函数，前者用于记录页访问情况相关的属性，后者则依赖于前者挑选需要换出的页。

```C
// _fifo_map_swappable 函数是当内存新产生一个页时调用，包括 pgdir_alloc_page 和 do_pgfault，即刚申请到一个页或刚从硬盘换入一个页。
// 主要要做的就是把新的页插入到队尾，就在 head 前面插入就行了
static int
_fifo_map_swappable(struct mm_struct *mm, uintptr_t addr, struct Page *page, int swap_in)
{
    // mm 中的 sm_priv 成员指向用来链接记录访问情况的链表头，建立了 mm_struct 和 swap_manager 之间的联系
    list_entry_t *head=(list_entry_t*) mm->sm_priv;
    list_entry_t *entry=&(page->pra_page_link);

    assert(entry != NULL && head != NULL);
    //record the page access situlation
    /*LAB3 EXERCISE 2: YOUR CODE*/
    //(1)link the most recent arrival page at the back of the pra_list_head qeueue.
    list_add_before(head, entry);
    return 0;
}
```

```C
// _fifo_swap_out_victim 要挑选将被换出的页，只需要把 head 的直接后继结点摘除就行
static int
_fifo_swap_out_victim(struct mm_struct *mm, struct Page ** ptr_page, int in_tick)
{
     list_entry_t *head=(list_entry_t*) mm->sm_priv;
         assert(head != NULL);
     assert(in_tick==0);
     /* Select the victim */
     /*LAB3 EXERCISE 2: YOUR CODE*/
     //(1)  unlink the  earliest arrival page in front of pra_list_head qeueue
     struct Page *victim = le2page(head->next, pra_page_link);
     list_del(&victim->pra_page_link);
     //(2)  assign the value of *ptr_page to the addr of this page
     *ptr_page = victim;
     return 0;
}
```

## Q: 如果要在 ucore 上实现"extended clock 页替换算法"请给你的设计方案，现有的 swap_manager 框架是否足以支持在 ucore 中实现此算法?

可以支持。

扩展时钟算法需要 PTE 的修改位和访问位，我们可以用 mm->pgdir 和 addr 找到页表项，其中就包含了需要的标志位。

遍历循环链表查询其中的访问位和修改位就可以找到要换出的页。

需要被换出的页的特征是 修改位和访问位都为 0。

ucore 通过判断 PTE 中对应位来挑选页。

消极换出，当 alloc_pages 无法分配时执行换出，当发生缺页异常时若页表项最低位为 0 而 高 24 位不为 0 即执行换入。
