# lab3 report

## 2019-11-15:14:32

实验完成，lab3 做的还算比较顺利，page fault 的处理机制比较好理解。练习的代码可以参考注释实现。

challenge 选择的是 extended clock 页置换算法，这个算法比较简单，要考虑的是页表项的访问和修改标志位，通过 clock 指针遍历环形链表，根据标志位进行处理：

| Access/Dirty(Old) | Access/Dirty(New)       |
| ----------------- | ----------------------- |
| 0/0               | swap out, return        |
| 0/1               | 0/0, 将页写入 swap 分区 |
| 1/0               | 0/0                     |
| 1/1               | 0/1                     |

现有的 swap_manager 的框架足以实现 extended clock 算法，可以参考 FIFO 的代码修改 map_swappable 和 swap_out_victim 函数。

编写 \_exclock_check_swap 函数需要了解 swap.c 中的 check_swap 函数流程，check 样例我是按照网站上视频课程中演示的样例。最终测试可以通过。
