# 导入表

可执行文件使用来自其他 DLL 的代码或数据的动作称为导入。PE 文件被载入时，PE 加载器的工作之一就是定位所有要导入的函数和数据，并将 DLL 装载到可执行文件的虚拟地址空间中。

PE 文件无法确定导入函数在内存中的位置，PE 加载器在装载 DLL 时将定位导入函数需要的信息写入到导入地址表（Import Address Table，IAT）中。执行中遇到导入函数的调用时，就通过 IAT 确定导入函数在内存中的位置。

## 导入表的结构

数据目录表的第 2 项指向导入表，导入表是 IMAGE_IMPORT_DESCRIPTOR 结构体数组，其定义如下：

```c++
typedef struct _IMAGE_IMPORT_DESCRIPTOR {
    union {
        DWORD Characteristics;
        DWORD OriginalFirstThunk;
    } DUMMYUNIONNAME;
    DWORD TimeDateStamp;
    DWORD ForwarderChain;
    DWORD Name;
    DWORD FirstThunk;
} IMAGE_IMPORT_DESCRIPTOR;
```

结构体中的重要成员：

- OriginalFirstThunk：导入名称表（Import Name Table，IAT）的 RVA。
- Name：导入函数所属库文件的 RVA。
- FirstThunk：IAT 的 RVA。

OriginalFirstThunk 和 FirstThunk 相似，分别指向两个本质上相同的 IMAGE_THUNK_DATA 结构体数组，即 INT 和 IAT。IMAGE_THUNK_DATA 结构体定义如下：

```c++
typedef struct _IMAGE_THUNK_DATA32 {
    union {
        DWORD ForwarderString;
        DWORD Function;
        DWORD Ordinal;
        DWORD AddressOfData;
    } u1;
} IMAGE_THUNK_DATA32;
typedef IMAGE_THUNK_DATA32 *PIMAGE_THUNK_DATA32;
```

结构体实际上是一个联合结构，在不同时刻含义不同：

- Function：被导入的函数的内存地址。

- Ordinal：被导入的 API 的序号值。
- AddressOfData：指向 IMAGE_IMPORT_BY_NAME。

当 IMAGE_THUNK_DATA 值得最高位为 1 时，表示函数以序号方式导入，其余位表示函数序号。当最高位为 0 时，表示函数以字符串类型的函数名方式输入，此时表示 RVA，指向 IMAGE_IMPORT_BY_NAME 结构体，记录了导入函数的相关信息。定义如下：

```c++
typedef struct _IMAGE_IMPORT_BY_NAME {
    WORD Hint;
    BYTE Name[1];
} IMAGE_IMPORT_BY_NAME, *PIMAGE_IMPORT_BY_NAME;
```

- Hint：表示导入函数在 DLL 输出表中的序号，不是必须的。
- Name：导入函数的函数名，是以 `\0` 即为的可变字符串域。

### INT 与 IAT

上面提到，INT 和 IAT 保存的数据完全相同，都是 IMAGE_THUNK_DATA 结构体数组，都指向 IMAGE_IMPORT_BY_NAME 结构。实际上，OriginalFirstThunk 指向的 INT 是不可改写的，而 FirstThunk 指向的 IAT 是由 PE 装载器重写的，先迭代搜索 INT，找出每一个 IMAGE_IMPORT_BY_NAME 结构体对应的导入函数地址，填入到对应的 IAT 表项。在内存中，INT 可以找到导入函数的名称或序号，IAT 可以找到函数的实际地址。

## 绑定导入

当 PE 装载器载入 PE 文件时，会检查导入表并将相关 DLL 映射到进程地址空间，然后重写 IAT 表，这一步需要花费很长时间。绑定导入将 IAT 的重写工作提前到装载前进行，由用户或专门的绑定工具完成，然后在 PE 文件中声明绑定导入，装载器不必重复装载。

绑定导入需要做出以下两个假设：

- 当进程初始化时，需要的 DLL 实际上加载到其首选基地址中。
- 绑定操作后，DLL 导出表中引用的符号位置没有改变。

如果不满足以上假设，IAT 中的地址就是无效的。Windows 在装载目标 PE 文件相关的 DLL 时，会首先检查 IAT 地址是否正确合法，如果不符合或者 DLL 需要被重新定位，装载器就会遍历 INT 计算新的地址，并将新的地址写入到 IAT 中。