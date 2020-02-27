# 动态规划

> 参考：
> 
> - [动态规划详解](https://labuladong.gitbook.io/algo/dong-tai-gui-hua-xi-lie/dong-tai-gui-hua-xiang-jie-jin-jie)

动态规划的一般形式就是求最值。核心问题是穷举，主要是存在重叠子问题，通过记录避免重复计算。

最难的是写出状态转移方程，主要的框架为：

明确状态 -> 定义 dp 数组/函数 -> 明确选择 -> 明确初态

下面将通过两个问题理解动态规划思想。

### 斐波那契

最简单的斐波那契就是用递归，但是单纯的递归会重复计算子问题。我们可以通过添加备忘录来剪枝，减少子问题个数。

递归是自顶而下，而动态规划使用自底向上，因此往往通过循环迭代实现。

由此得到基于 dp 数组的斐波那契：

```c++
int fib(int n) {
    vector<int> dp(n + 1, 0);
    dp[1] = dp[2] = 1;
    for(int i = 3; i <= n; i++) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }
    return dp[n];
}
```

此问题的状态转移方程为：

$$
f(x)=\left\{
\begin{aligned}
1 & , & n=1,2 \\
f(n-1)+f(n-2) & , & n>2
\end{aligned}
\right.
$$

当然，常用的还是用两个变量代替 dp 数组，空间复杂度 O(1)。

### 凑零钱

给 k 种面值的硬币，每种数量无限，要求用最少的金币数凑出金额 amount。

首先这个问题是动态规划问题，因为具有最优子结构，子问题相互独立。

那么如何列出正确的状态转移方程？按照之前提出的框架，先确定状态，硬币数量无限，则唯一的状态就是目标金额 amount。然后确定 dp 含义，目标金额为 n，至少需要 dp(n) 个硬币凑出金额。然后确定选择而择优，就是对每个状态，可以做出什么选择改变当前状态。具体到此问题，就是选择一个硬币，目标金额就减少。最后明确初始态，目标金额为 0，所需硬币数量为 0。

$$
dp(n) = \left\{
\begin{aligned}
0 & , & n = 0 \\
-1 & , & n < 0 \\
\min\{dp{n - coin} + 1\ | coin \in coins\} & , & n > 0
\end{aligned}
\right.
$$

```c++ tab="暴力递归"
vector<int>& coins;
int amount;

int dp(int n) {
    // base case
    if(n == 0) {
        return 0;
    }else if(n < 0) {
        return -1;
    }else {
        for()
    }
    int res = -1;
    for(auto coin : coins) {
        int subProblem = dp(n - coin);
        if(subProblem == -1) {
            continue;
        }
        res = min(res, 1 + subProblem);
    }
    return res;
}
```

```c++ tab="dp 数组"
int coinChang(vector<int>& coins, int amount) {
    // 取最小值，所以可以把初值设大一点，最多就是 amount + 1
    vector<int> dp(amount + 1, amount + 1);
    // base case:
    dp[0] = 0;
    for(int i = 1; i <= amount; i++) {
        // 内层循环求所有子问题 + 1 的最小值
        for(int coin : coins) {
            if(i - coin < 0) {
                continue;
            }
            dp[i] = min(dp[i], 1 + dp[i - coin]);
        }
    }
    return (dp[amount] == amount + 1) ? -1 : dp[amount];
}
```

