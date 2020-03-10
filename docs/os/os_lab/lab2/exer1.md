# EXER1: 实现 first-fit 连续物理内存分配算法

通过 preview 中的学习，已经初步了解实现 first-fit 算法的先导知识。利用双向链表管理不连续的空闲内存块，完善 init_memmap、alloc_pages、free_pages 函数。

pmm_manager 中定义了一系列函数指针用于管理物理内存空间。

```C
struct pmm_manager {
    const char *name;                                 // XXX_pmm_manager's name
    void (*init)(void);                               // initialize internal description&management data structure
                                                      // (free block list, number of free block) of XXX_pmm_manager
    void (*init_memmap)(struct Page *base, size_t n); // setup description&management data structcure according to
                                                      // the initial free physical memory space
    struct Page *(*alloc_pages)(size_t n);            // allocate >=n pages, depend on the allocation algorithm
    void (*free_pages)(struct Page *base, size_t n);  // free >=n pages with "base" addr of Page descriptor structures(memlayout.h)
    size_t (*nr_free_pages)(void);                    // return the number of free pages
    void (*check)(void);                              // check the correctness of XXX_pmm_manager
};
```

对于默认的 pmm_manager 其中函数的具体实现在 ./kern/mm/default_pmm.c 中，现在需要在原代码的基础上修改。

```C
static void
default_init_memmap(struct Page *base, size_t n) { // 参数为内存块 head page 的地址和页的个数
    assert(n > 0);
    struct Page *p = base;
    for (; p != base + n; p ++) {
        assert(PageReserved(p)); // 在 ./kern/mm/pmm.c 中的 page_init 中开始是将所有的页都标记为 reserved
        p->flags = p->property = 0; // 清空 Page 结构的 flags 和 property
        set_page_ref(p, 0); // 将 Page 结构中的 ref 设置为 0，即引用为 0
    }
    base->property = n; // base 指向的页即内存块的 head page 的 property 值应为内存块页数
    SetPageProperty(base); // 将 flags 的 PG_property 置位，表示 property 值有效
    nr_free += n; // 空闲页数
    // list_add(&free_list, &(base->page_link));
    // 将内存块的 head page 插入到管理空闲内存的双向链表中
    // list_add 将 base 按照地址递增的顺序头插法插入了链表，导致从头结点向后访问的 page 地址是递减的
    // 改为 list_add_before 每次在头结点前插入，这样使得头结点向后访问的 page 地址是递增的。符合 first-fit 的要求。
    list_add_before(&free_list, &(base->page_link));
}
```

这里其实不用修改，因为初始化只有一大块空闲物理内存空间，不影响。后面涉及到的则必须要修改。

```C
static struct Page *
default_alloc_pages(size_t n) { // 参数为请求页的个数
    assert(n > 0);
    if (n > nr_free) {
        return NULL;
    }
    struct Page *page = NULL;
    list_entry_t *le = &free_list;
    while ((le = list_next(le)) != &free_list) {
        struct Page *p = le2page(le, page_link); // le2page 将链表结构转为 Page
        if (p->property >= n) {
            page = p;
            break;
        }
    }
    if (page != NULL) {
        list_del(&(page->page_link)); // 从链表中删除要分配的这个内存块
        if (page->property > n) {
            struct Page *p = page + n;
            SetPageProperty(p); // 将分配后的 head page 的 PG_property 置位
            p->property = page->property - n; // 拆分
            // list_add(&free_list, &(p->page_link));
            // 这里应该是在找到的 page 后插入，而此时 page 已经从列表中删除，不能直接在 page->page_link 之后添加
            // 或者可以把 list_del 放到后面，还是用 list_add
            list_add_before(page->page_link.next, &(p->page_link));
        }
        nr_free -= n;
        ClearPageProperty(page);
    }
    return page;
}
```

```C
static void
default_free_pages(struct Page *base, size_t n) {
    assert(n > 0);
    struct Page *p = base;
    for (; p != base + n; p ++) {
        assert(!PageReserved(p) && !PageProperty(p)); // 页不是保留的
        p->flags = 0; // flags 清零
        set_page_ref(p, 0); // 将引用清零
    }
    base->property = n;
    SetPageProperty(base);
    list_entry_t *le = list_next(&free_list);
    while (le != &free_list) {
        p = le2page(le, page_link);
        le = list_next(le);
        if (base + base->property == p) { // 向后合并
            base->property += p->property;
            ClearPageProperty(p);
            list_del(&(p->page_link));
        }
        else if (p + p->property == base) { // 向前合并
            p->property += base->property;
            ClearPageProperty(base);
            base = p;
            list_del(&(p->page_link));
        }
    }
    nr_free += n;
    // list_add(&free_list, &(base->page_link));
    // 不能直接将 base 插入到 free_list 后，应该按照地址找到适当的位置
    if( base > le2page(list_prev(&free_list), page_link)) { // base 的地址最大就直接添加到链表尾
        list_add_before(&free_list, &(base->page_link));
    } else { // 否则就从后往前比较地址，找到首个地址比 base 大的块，插入到前面
        le = &free_list;
        while ( (le = list_next(le)) != &free_list ) {
            p = le2page(le, page_link);
            if( base + base->property <= p ) {
                assert(base + base->property != p); // 检查合并是否正确
                break;
            }
        }
        list_add_before(le, &(base->page_link));
    }
}
```

## Q: 你的 first fit 算法是否有进一步的改进空间

用以空间为关键字的平衡树和以地址为关键字的平衡树可以加快内存空间的申请和释放
