# EXER2: 父进程复制自己的内存空间给子进程

创建子进程的函数 do_fork 在执行中将拷贝当前进程（即父进程）的用户内存地址空间中的合法内容到新进程中（子进程），完成内存资源的复制。具体是通过 copy_range 函数（位于 kern/mm/pmm.c 中）实现的，请补充 copy_range 的实现，确保能够正确执行。

???

```C
/* copy_range - copy content of memory (start, end) of one process A to another process B
 * @to:    the addr of process B's Page Directory
 * @from:  the addr of process A's Page Directory
 * @share: flags to indicate to dup OR share. We just use dup method, so it didn't be used.
 *
 * CALL GRAPH: copy_mm-->dup_mmap-->copy_range
 */
int
copy_range(pde_t *to, pde_t *from, uintptr_t start, uintptr_t end, bool share) {
    ...
        /* LAB5:EXERCISE2 YOUR CODE
         * replicate content of page to npage, build the map of phy addr of nage with the linear addr start
         *
         * MACROs or Functions:
         *    page2kva(struct Page *page): return the kernel vritual addr of memory which page managed (SEE pmm.h)
         *    page_insert: build the map of phy addr of an Page with the linear addr la
         *    memcpy: typical memory copy function
         *
         * (1) find src_kvaddr: the kernel virtual address of page
         * (2) find dst_kvaddr: the kernel virtual address of npage
         * (3) memory copy from src_kvaddr to dst_kvaddr, size is PGSIZE
         * (4) build the map of phy addr of  nage with the linear addr start
         */
        void *p_kva = page2kva(page);
        void *np_kva = page2kva(npage);
        memcpy(np_kva, p_kva, PGSIZE);
        ret = page_insert(to, npage, start, perm);
    ...
}
```

## Q: 简要说明如何设计实现 "Copy on Write" 机制

COW 机制的基本概念是指如果有多个使用者对一个资源 A(如内存块)，进行读操作，则每个使用者只需获得一个指向同一个资源 A 的指针，就可以读该资源了。若某使用者需要对这个资源 A 进行写操作，系统会对该资源 A 进行 copy 操作，从而使得该“写操作”使用者获得一个该资源 A 的“私有”拷贝——资源 B，可对资源 B 进行写操作。

该“写操作”使用者对资源 B 的改变对于其他的使用者而言是不可兼得，因为其他使用者看到的还是资源 A 。

在 copy_range 函数中不拷贝页面，而是把原始 page 的位置直接装在新的页表项中，但是把页表项的 W 位置 0。之后可以正常的读取，但写入时会引发缺页异常，page fault 处理中，如果发现错误原因是权限问题，而访问的段的断描述符权限为可写，就可判断是由于使用 COW 机制而导致的。这时将父进程的数据段、代码段等复制到子进程的内存空间，设置页表项为新的内存位置，并且将 W 位置 1，表示以后这个资源就属于它，可以自由地写了。
