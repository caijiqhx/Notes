# 导出表

DLL 通过导出表向外界提供导出函数名称、序号以及入口地址等信息。PE 装载器重写 IAT 时就是通过 DLL 的导出表读取导入函数地址。导出表通常存在于大多数 DLL 文件中，一些 EXE 文件中同样存在。

DLL 导出函数的调用，可以通过函数名称或函数在导出表的索引进行。PE 装载器将与进程相关的 DLL 加载到虚拟地址空间后，会根据导入表中登记的与该 DLL 相关的名称或序号遍历 DLL 的虚拟地址空间并查找导出表结构，从而确定导出函数起始地址 VA，写入对应的 IAT 项。

## EAT

数据目录表的第一项保存导出表的 RVA，指向 IMAGE_EXPORT_DIRECTORY 结构体。PE 文件最多只存在 1 个此结构体。其定义如下：

```c++
typedef struct _IMAGE_EXPORT_DIRECTORY {
    DWORD Characteristics;
    DWORD TimeDateStamp;
    WORD MajorVersion;
    WORD MinorVersion;
    DWORD Name;
    DWORD Base;
    DWORD NumberOfFunctions;
    DWORD NumberOfNames;
    DWORD AddressOfFunctions;
    DWORD AddressOfNames;
    DWORD AddressOfNameOrdinals;
} IMAGE_EXPORT_DIRECTORY, *PIMAGE_EXPORT_DIRECTORY;
```

主要数据成员说明：

- Name：保存指向一个 ASCII 字符串的 RVA。即 DLL 文件的名称。
- Base：导出函数的起始序号。通过序号查询导出函数时，减去起始序号作为导出函数表（Export Address Table，EAT）的索引。
- NumberOfFunctions：导出函数的总个数。
- NumberOfNames：导出函数名称表（Export Name Table，ENT）的条目数量。有些函数没有定义名称，只能通过序号导出。
- AddressOfFunctions：EAT 的 RVA。EAT 是一个 RVA 数组，保存了 NumberOfFunctions 数量的导出函数地址。
- AddressOfNames：ENT 的 RVA。ENT 是一个指向导出函数名的 ASCII 字符串的 RVA 数组。
- AddressOfNameOrdinals：导出序号表的 RVA。此表将 ENT 中的数组索引映射到相应的 EAT 条目。

获取导出函数函数地址的过程大致如下：

- 利用 AddressOfNames 定位 ENT；
- 通过字符串比较找到指定的函数名称，找到后其索引作为 name_index；
- 利用 AddressOfNameOrdinals 定位到导出序号表；
- 通过 name_index 在导出序号表中定位对应的序号值 ordinal；
- 利用 AddressOfFunctions 定位 EAT；
- 最后通过 ordinal 作为索引在 EAT 中定位到对应的项，获取制定函数的起始地址。

对于没有命名的导出函数，利用序号减去 Base 作为 EAT 的索引值，获取导出函数地址。