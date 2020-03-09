# 背包问题

> 百度百科：
> 
> 背包问题(Knapsack problem)是一种组合优化的NP完全问题。问题可以描述为：给定一组物品，每种物品都有自己的重量和价格，在限定的总重量内，我们如何选择，才能使得物品的总价格最高。问题的名称来源于如何选择最合适的物品放置于给定背包中。相似问题经常出现在商业、组合数学，计算复杂性理论、密码学和应用数学等领域中。也可以将背包问题描述为决定性问题，即在总重量不超过W的前提下，总价值是否能达到V？

利用背包思想对各种硬币找零问题求解。

## 01 背包问题

给定不同面额的硬币 coins 和总金额 amount，每个硬币最多选择一次。计算可以凑成总金额所需的最少硬币个数，无法组合则返回 -1。

### 状态表示

dp[i][j] 表示对于前 i 个硬币，总价值是 j 的情况下最小硬币数目。

### 状态转移

dp[i][j] = min(dp[i - 1][j], dp[i - 1][j - coins[i]] + 1) 分别对应了不拿和拿第 i 个硬币的情况。

因为 dp[i][j] 只与上一层的两个状态优先，因此可以优化为一维数组。dp[j] = min(dp[j], dp[j - coins[i]] + 1); 因为 j - coins[i] < j，所以需要倒序遍历，以保证上一状态不被覆盖。

### 边界情况

dp[0] = 0 表示凑出金额 0 的最小硬币个数为 0。状态初始化为 amount + 1 表示无法达到。

```c++
int knapspack(vector<int>& coins, int amount) {
    vector<int> dp(amount + 1, amount + 1);
    dp[0] = 0;
    for(auto coin : coins) {
        for(int j = amount; j >= coin; j--) {
            dp[j] = min(dp[j], dp[j - coin] + 1);
        }
    }
    return dp[amount] == amount + 1 ? -1: dp[amount];
}
```

## 完全背包问题

给定不同面额的硬币 coins 和总金额 amount。每个硬币可以选择无数次。计算可以凑成总金额所需的最少的硬币个数，无法组合则返回 -1。

### 状态表示

d[i][j] 表示对前 i 种硬币，凑出金额 j 的最少硬币数目。

### 状态转移

对第 i 种硬币，可以不拿，或拿 1...k 个，直到大于目标金额。

dp[i][j] = min(dp[i - 1][j], dp[i - 1][j - coins[i]] + 1, dp[i - 1][j - 2 * coins[i]] + 2,..., f[i - 1][j - k * coins[i]] + k)

其中也包含了很多的冗余计算，如 dp[i][j - coins[i]] = min(dp[i - 1][j - coins[i]], dp[i - 1][j - 2 * coins[i]] + 1, ...)

可以合并为 dp[i][j] = min(dp[i - 1][j], dp[i][j - coins[i]] + 1)

优化为一维数组 dp[j] = min(dp[j], dp[j - coins[i] + 1])，从小到大枚举金额，j - coins[i] 的状态在同一层计算好直接替换即可。

### 边界情况

dp[0] = 0，其余初始化为 amount + 1 表示无法达到。

```c++
int knapspacl(vector<int>& coins, int amount) {
    vector<int> dp(amount + 1, amount + 1);
    dp[0] = 0;
    for(auto coin : coins) {
        for(int j = coin; j <= amount; j++) {
            dp[j] = min(dp[j], dp[j - coin] + 1);
        }
    }
    return dp[amount] == amount + 1 ? -1 : dp[amount];
}
```

通过代码可以看到，完全背包的硬币问题与 01 背包下的问题几乎相同，就是内层循环金额**从小到大**遍历。

## 多重背包问题

给定不同面额的硬币 coins 和总金额 amount。每个硬币选择的次数有限制为 s。计算可以凑成总金额的最少硬币个数，无法组合则返回 -1。

### 状态表示

对第 i 种硬币，可以不拿，或拿 1...k 个，知道大于目标金额或达到数量限制。

dp[i][j] = min(dp[i - 1][j], dp[i - 1][j - coins[i]] + 1,..., dp[i - 1][j - k * coins[i]] + k)

本质上与 01 背包类似，加一个枚举硬币个数的循环即可。

```c++
int knapspack(vector<int>& coins, int amount, vector<int>& s) {
    vector<int> dp(amount + 1, amount + 1);
    dp[0] = 0;
    for(int i = 0; i < coins.size(); i++) {
        for(int j = amount; j >= coins[i]; j--) {
            for(int k = 1; k <= s[i]; k++){
                dp[j] = min(dp[j], dp[j - k * coins[i]] + k);
            }
        }
    }
    return dp[amount] == amount + 1 ? -1: dp[amount];
}
```