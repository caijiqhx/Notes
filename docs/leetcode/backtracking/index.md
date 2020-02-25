# 回溯算法

> 参考：
>
> - [回溯算法详解](https://labuladong.gitbook.io/algo/suan-fa-si-wei-xi-lie/hui-su-suan-fa-xiang-jie-xiu-ding-ban)

解决回溯问题，实际就是一个决策树的遍历问题。主要就是三个问题：

- 路径：做出的选择
- 选择列表：可以做的选择
- 结束条件：到达决策树底层，无法再做选择的条件

回溯算法的框架：

```
result = []
def backtrack(路径, 选择列表):
    if 满足结束条件:
        result.add(路径)
        return

    for 选择 in 选择列表:
        做选择
        backtrack(路径, 选择列表)
        撤销选择
```

核心就是 for 循环里的递归，在递归调用前做选择，递归调用之后撤销选择。