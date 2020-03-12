# 基址重定位表

链接器在生成 PE 文件时，会假设执行时 PE 文件会被加载到默认的基地址处，就把代码和数据的相关地址写入 PE 文件。如果按照默认基地址装载，则不需要重定位。但是如果 PE 文件被装载到另一地址，文件中的地址失效，就需要用重定位表调整。

每个 EXE 文件都有自己独立的虚拟内存地址空间，所以总能装载到默认基地址，也就不需要重定位信息。而 EXE 导入多个 DLL 文件时，DLL 文件就要面临基地址被占用的情况，需要重定位信息。

## 基址重定位表的结构

重定位表位于 .reloc 区块，数据目录表的第 6 项指向了重定位表的 RVA。重定位数据采用按页分割的方式，每个块存放 4KB 的重定位信息，数据块大小以 DWORD 对齐。重定位块以一个 IMAGE_BASE_RELOCATION 结构体开始，其定义如下：

```c++
typedef struct _IMAGE_BASE_RELOCATION {
    DWORD VirtualAddress;
    DWORD SizeOfBlock;
    WORD TypeOffset;
} IMAGE_BASE_RELOCATION;
typedef IMAGE_BASE_RELOCATION UNALIGNED *PIMAGE_BASE_RELOCATION;
```

结构体成员：

- VirtualAddress：这组重定位数据的开始 RVA。重定位项对应的地址加上这个值得到完整的 RVA。
- SizeOfBlock：重定位块的大小。
- TypeOffset：一个数组，每项大小为 2 字节。高 4 位表示重定位类型，低 12 位是重定位地址，与 VirtualAddress 相加就是需要修改的重定位数据的 RVA。

