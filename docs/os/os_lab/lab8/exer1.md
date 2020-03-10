# EXER1: 完成读文件操作的实现

**用户进程打开文件的流程**

`int fd1 = safe_open("sfs_filetest1", O_RDONLY);`

- 通用文件访问接口层的处理流程

  首先进入通用文件访问接口层的处理流程，即进一步调用如下用户态函数：open-->sys_open-->syscall，从而引起系统调用进入到内核态。到了内核态后，通过中断处理例程，会调用到 sys_open 内核函数，并进一步调用 sysfile_open 内核函数。到此，需要把用户空间的字符串 `sfs_filetest` 复制到内核空间中的字符传 path 中，并进入到文件系统抽象层的处理流程完成进一步的打开文件操作中。

- 文件系统抽象层的处理流程

  分配一个空闲的 file 数据结构变量在文件系统抽象层的处理中，首先调用的 file_open 函数，它要给这个即将打开的文件分配一个 file 数据结构的变量，这个变量其实是当前进程的打开文件数组 current->fs_struct->filemap[] 中的一个空闲元素（即还没用于一个打开的文件），而这个索引值就是最终要回到用户进程并赋值给变量 fd1。到了这一步还仅仅是给当前用户进程分配了一个 file 数据结构的变量，还没有找到对应的文件索引节点。

  为此需要进一步调用 vfs_open 函数来找到 path 指出的文件所对应的基于 inode 数据结构的 VFS 索引节点 node。vfs_open 函数需要完成两件事情：通过 vfs_lookup 找到 path 对应文件的 inode；调用 vop_open 函数打开文件。

  - 找到文件设备的根目录的索引节点需要注意，这里的 vfs_lookup 函数是一个针对目录的操作函数，它会调用 vop_lookup 函数来找到 SFS 文件操作系统中的根目录下的 sfs_filetest1 文件。
  - 通过调用 vop_lookup 函数来查找根目录下对应文件 sfs_filetest1 的索引节点，如果找到就返回索引节点。
  - file 和 node 建立联系。之后返回到 file_open 函数中，通过执行语句 `file->node = node` 就把当前进程的 `current->fs_struct->filemap[fd]` 的成员变量 node 指针指向了代表 sfs_filetest1 文件的索引节点 inode。返回 fd，经过重重回退，最终把 fd 赋值给 fd1，完成了打开文件操作。

- SFS 文件系统层的处理流程

  这里需要分析文件系统抽象层中的 vop_lookup。

  sfs_lookup 有三个参数：node，path，node_store。其中 node 是根目录“/”所对应的 inode 节点；path 是文件 sfs_filetest1 的绝对路径/sfs_filetest1，而 node_store 是经过查找获得的 sfs_filetest1 所对应的 inode 节点。

  sfs_lookup 函数以“/”为分割符，从左至右逐一分解 path 获得各个子目录和最终文件对应的 inode 节点。在本例中是调用 sfs_lookup_once 查找以根目录下的文件 sfs_filetest1 所对应的 inode 节点。当无法分解 path 后，就意味着找到了 sfs_filetest1 对应的 inode 节点，就可顺利返回了。

  sfs_lookup_once 将调用 sfs_dirent_search_nolock 函数来查找与路径名匹配的目录项，如果找到目录项，则根据目录项中记录的 inode 所处的数据块索引值找到路径名对应的 SFS 磁盘 inode，并读入 SFS 磁盘 inode 对的内容，创建 SFS 内存 inode。

完成读文件操作：

```C
static int
sfs_io_nolock(struct sfs_fs *sfs, struct sfs_inode *sin, void *buf, off_t offset, size_t *alenp, bool write) {
    ...
  //LAB8:EXERCISE1 YOUR CODE HINT: call sfs_bmap_load_nolock, sfs_rbuf, sfs_rblock,etc. read different kind of blocks in file
	/*
	 * (1) If offset isn't aligned with the first block, Rd/Wr some content from offset to the end of the first block
	 *       NOTICE: useful function: sfs_bmap_load_nolock, sfs_buf_op
	 *               Rd/Wr size = (nblks != 0) ? (SFS_BLKSIZE - blkoff) : (endpos - offset)
	 * (2) Rd/Wr aligned blocks
	 *       NOTICE: useful function: sfs_bmap_load_nolock, sfs_block_op
     * (3) If end position isn't aligned with the last block, Rd/Wr some content from begin to the (endpos % SFS_BLKSIZE) of the last block
	 *       NOTICE: useful function: sfs_bmap_load_nolock, sfs_buf_op
	*/
    uint32_t nblks = endpos / SFS_BLKSIZE - blkno;
    // 读第一部分
    if (blkoff = offset % SFS_BLKSIZE) {
        // 第一块的大小
        size = (nblks != 0) ? (SFS_BLKSIZE - blkoff) : (endpos - offset);
        // 内存文件索引对应的 block 号ino
        if ((ret = sfs_bmap_load_nolock(sfs, sin, blkno, &ino)) != 0)
            goto out;
        if ((ret = sfs_buf_op(sfs, buf, size, ino, blkoff)) != 0)
            goto out;
        // 实际的读写操作
        alen += size;
        buf += size;
        offset += size;
        blkno ++;
        if (nblks == 0)
            goto out;
        else
            nblks --;
    }
    // 读取中间部分的数据，nblks 即块号
    if (nblks > 0) {
        if ((ret = sfs_bmap_load_nolock(sfs, sin, blkno, &ino)) != 0)
            goto out;
        if ((ret = sfs_block_op(sfs, buf, ino, nblks)) != 0)
            goto out;
        buf += nblks * SFS_BLKSIZE;
        alen += nblks * SFS_BLKSIZE;
        blkno += nblks;
    }
    // 读取第三部分的数据
    if (size = endpos % SFS_BLKSIZE) {
        if ((ret = sfs_bmap_load_nolock(sfs, sin, blkno, &ino)) != 0)
            goto out;
        if ((ret = sfs_buf_op(sfs, buf, size, ino, 0)) != 0)
            goto out;
        alen += size;
    }
out:
    *alenp = alen;
    if (offset + alen > sin->din->size) {
        sin->din->size = offset + alen;
        sin->dirty = 1;
    }
    return ret;
}
```

## Q: 给出设计实现“UNIX 的 PIPE 机制”的概要设方案

管道本质上就是一个操作系统内核管理的环形缓冲区，所以需要一块内存作为缓冲区，然后需要记录环形缓冲区的头部和尾部。当一个进程尝试从空管道读取数据或者向满管道写入数据的时候，操作系统内核需要将进程阻塞，所以还需要一个读取等待队列和一个写入等待队列。 缓冲区大小通常设为一页的大小 4KB。

```C
struct pipe {
    size_t head; // 缓冲区头部
    size_t tail; // 缓冲区尾部
    wait_queue_t read_queue; // 管道读取等待队列
    wait_queue_t write_queue; // 管道写入等待队列
    char * buffer; // 环形缓冲区
};
```

索引节点：管道信息数据结构和管道类型号。

管道操作：

- 创建：首先创建管道的信息节点，然后两个文件描述符，负责只读和只写。
- 关闭：打开计数值为 0，则关闭，对于管道，引用计数值等于打开计数值。
- 回收：管道的全部文件描述符关闭后，回收缓冲区内存以及信息节点使用的内存。
- 读取：逐字节读，非空，则取出后唤醒写进程，然后尝试读下一个，为空则阻塞等待被唤醒。
- 写入：逐字节写，非满，写入后唤醒都进程，尝试写下一个，为满则阻塞。
