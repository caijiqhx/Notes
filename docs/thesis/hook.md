# Hook 技术学习

> 《加密与解密》第 13 章 Hook 技术

Hook 的关键就是通过一定手段埋下 “钩子”，钩住我们关心的重要流程，然后根据需要对执行过程进行干预。

通过在执行真正的目标函数之前执行事先插入的代码，获得程序执行过程的决定权——“插入特定代码以干预程序的执行流程” 就是 Hook 的奥义。

## Hook 的分类

程序是数据和指令的集合，Hook 就是对数据或指令的修改。对应的，Hook 大体分为两种 `Address Hook` 和 `Inline Hook`。

### `Address Hook`

`Address Hook`，通过修改数据进行 Hook。一般是一些函数的地址或偏移量。通常存放在各类表或结构中，或者某个指定的地址外，亦或特殊的寄存器中。共同点就是某个时刻会称为程序执行的 `eip`。我们要做的就是把这些值替换成 `Detour` 函数地址

- 各类表中的地址
  - PE 的 IAT，导入地址表，存的是函数地址。作用范围只针对被 Hook 的模块；
  - PE 的 EAT，导出地址表，存的是函数偏移；
  - `user32.dll` 回调函数表，存访各种用于 GUI 的回调函数，通常与内核中的 `KeUserModeCallback` 配合使用；
  - IDT 中断描述符表，存访中断处理例程 ISR 的地址；
  - SSDT 系统服务描述符表；
  - C++ 类虚函数表 VFT；
  - COM 接口的功能函数表。
- 处理例程地址，常见于内核中。
- 特殊寄存器中的地址，Windows 使用 MSR 寄存器组中 `IA32_SYSENTER_EIP` 的值作为内核调用的入口，当在 `ntdll` 中调用汇编指令 `sysenter` 进入内核时，CPU 会首先执行到这里。
- 特定的函数指针，与地址表类似，只不过不存在表中。

### `Inline Hook`

直接修改指令，一般使用 `jmp/call/retn` 之类的转移指令，主要 5 种模式：

1. `jmp xxxxxxxx`，5 字节，直接跳转到某地址；

2. `push xxxxxxxx; retn`，6 字节，通过压栈返回实现跳转；

3. `mov eax, xxxxxxxx; jmp eax`，7 字节，先将转移地址放入寄存器，再实现跳转。用 `eax` 寄存器来临时保存转移地址是因为 `eax` 常用于保存函数的返回值，在函数入口处修改它不会影响函数的执行结果；

4. call Hook，更换指令或输入表；

5. HotPatch Hook，一个短跳加一个长跳，出现这种形式与函数开头的指令有关。

   ```assembly
   ; 7 字节，可以正好用 jmp 覆盖前三条
   7C809AF1	8BFF		mov edi, edi
   7C809AF3	55			push ebp
   7C809AF4	8BEC		mov ebp, esp
   7C809AF6	...
   ; 使用 SEH，7 字节，可以用 mov eax, xxxxxxxx; jmp eax
   ; 实现 HotPatch 的方式，每个函数的第 1 条指令一定为 2 字节
   ; 一般函数位置向上有 5 个 nop 或 INT 3，就是为了这种 hook 准备的
   7C809B12	6A 10		push 10
   7C809B14	68 609B807C	push kernel32.7C809B60
   7C809B19	E8 B889FFFF	push kernel32.7C8024D6
   7C809B1E	...
   ```

### 基于异常处理的 Hook

在要 Hook 的位置写一条会引发异常的指令，或通过改变被 Hook 位置的内存属性引起访问异常，亦或中断指令等。程序执行触发异常，就会跳转到事先安装的异常处理过程中。

###  不是 Hook 的 Hook

一些病毒或操作系统程序的行为理念与 Hook 类似，都是在某些时候取得程序的控制权。

- 病毒修改 EntryPoint；
- 系统回调机制和分层模型。

## Hook 位置挑选

在程序执行流中，Hook 位置越往上，就越早得到控制权，从而优先处理，但拦截范围优先，也容易被绕过；Hook 位置越往下，得到控制权就越晚，但是在该调用真正实施之前，安装 Hook 的程序有最终的决定权，而且不容易被绕过，同时底层的 Hook 调用频繁影响系统性能。

- 程序中的 call Hook，影响最小；
- 系统内核中的 Hook，影响最大。

在满足拦截范围的情况下，离调用点不要太远，从而使拦截范围尽可能小。同时还要考虑参数处理的难易程度。

## Hook 的典型过程

首先都需要一个自定义的 Hook 函数替代被 Hook 的函数，称为 `Detour` 函数，其原型、调用约定、返回值都与原函数相同。如果 `Detour` 函数中需要调用原函数来实现功能，就需要通过某种方式调用原始函数，`Address Hook` 和 `Inline Hook` 的处理方式有所不同。

### `Address Hook` 的实施过程

除了定义 `Detour` 函数，还需要定义一个与被 Hook 函数原型一致的函数指针，指向原始函数。之后的操作就是查表替换原地址写入 `Detour` 函数的地址了。

IAT Hook、虚函数 Hook、SSDT Hook

### `Inline Hook` 的实施过程

- `TargetFun`：要被 Hook 的目标函数；
- `DetourFun`：用于代替 `TargetFun` 的自定义函数；
- `TrampolineFun`：不是完整的函数，而是调用原函数的入口。在该函数中要执行 `TargetFun` 中被替换的前几条指令，与 `TargetFun` 中被 Hook 位置之后的部分构成完整的函数。

原来的调用流程就是原函数调用 `TargetFun` 后返回。

Hook 后的调用流程是原函数调用 `DetourFun`，接着调用 `TrampolineFun`，接着调用 `TargetFun`。其中 `TrampolineFun` 不会返回结果，仅用作跳板。

实现 `Inline Hook` 需要解决两个问题：

1. 确定 Hook 方式，确定要写入何种机器码完成流程转移；
2. 准备好 `TrampolineFun`，使其正确跳转到 `TargetFun` 中被 Hook 指令之后的部分，以顺利完成原始功能调用。将 `TrampolineFun` 定义为裸函数 `__declspec(naked)`，保证编译器不会为该函数添加额外的指令。同时可以将函数原型定义为与 `TargetFun` 完全一样，以便调用。

以 `MessageBoxA` 的 Hook 为例，使用 `jmp` 指令覆盖前 3 个指令，有 `offset = targetAddress - instAddress - instLength`。

### 二次 Hook

对 `Address Hook` 的二次 Hook，只需替代地址。

对 `Inline Hook` 的二次 Hook，可以直接替换原 Hook 指令、另选位置替换或者 Hook 上一个 Hook 的 `DetourFun`。

## `DetourFun` 的典型用法

最简单的 `DetourFun` 是 pass-through，不干预任何行为，直接调用原始函数。

一般会涉及到以下几种操作：

1. 检查参数，对 in 类型参数和重过程型函数，调用前要检查参数。
2. 检查结果，对 out 类型参数和重结果的函数，需要在调用后获取结果检查；
3. 拦截调用或下发，比如实现控制流平展。