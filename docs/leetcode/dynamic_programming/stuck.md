# LeetCode 股票买卖问题

## 题目描述

给定一个数组，它的第  i 个元素是一支给定股票第 i 天的价格。

设计一个算法来计算你所能获取的最大利润。你最多可以完成 k 笔交易。

注意：你不能同时参与多笔交易（你必须在再次购买前出售掉之前的股票）。

以上是几个题目共同的条件，区别就是添加了限制，第一题是 k = 1，第二题是 k = +infinity，第三题是 k = 2，其余两道加入了交易冷冻期和手续费的条件。

我们准备用一个思路解决这些问题，下面开始分析。

### 状态表示

利用状态进行穷举，分析每一天有几种状态，每种状态对应的选择，根据选择更新状态。

此问题中，每天有三种选择：买入、卖出、不动。同时还有一些限定，先买入再卖出再买入，不动还分持有和不持有，还有交易次数 k 的限制。

dp[i][k][1/0] 表示第 i 天，交易次数限制为 k，是/否持有股票的状态下的利益。一共就 n _ k _ 2 种状态。

我们要求的是 dp[n -1][k][0]，即最后一天，最多允许 k 次交易，最多获得的利润。

### 状态转移方程

dp[i][k][0] = max(dp[i - 1][k][0], dp[i - 1][k][1] + prices[i])

第 i 天不持有股票，可以是前一天就没有股票，今天不动，还是没有；或者是前一天有股票，今天卖出。

dp[i][k][1] = max(dp[i - 1][k][1], dp[i - 1][k - 1][0] - prices[i])

第 i 天持有股票，前一天有，今天不动；或者前一天没有，今天买入。

今天的选择就是二者较大值。

### 初始状态

dp[-1][k][0] = 0，未开始的利润为 0；dp[-1][k][1] = INT_MIN，未开始不可能有股票；dp[i][0][0] = 0，不允许交易利润为 0；dp[i][0][1]，不允许交易不可能持有股票。

因此总结状态转移方程：

```c++
dp[-1][k][0] = dp[i][0][0] = 0;
dp[-1][k][1] = dp[i][0][1] = INT_MIN;

dp[i][k][0] = max(dp[i - 1][k][0], dp[i -1][k][1] + prices[i]);
dp[i][k][1] = max(dp[i - 1][k][1], dp[i - 1][k - 1][0] - prices[i]);
```

基本的框架形成，下面开始完善细节问题。

## k = 1

对状态转移方程化简：

```c++
dp[i][1][0] = max(dp[i - 1][1][0], dp[i - 1][1][1] + prices[i]);
dp[i][1][1] = max(dp[i - 1][1][1], dp[i - 1][0][0] - prices[i]);
            = max(dp[i - 1][1][1], -prices[i]);

// 去掉 k：
dp[i][0] = max(dp[i - 1][0], dp[i - 1][1] + prices[i]);
dp[i][1] = max(dp[i - 1][1], -prices[i]);
```

写出对应的代码：

```c++ tab="dp"
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int n = prices.size();
        if(n <= 1) {
            return 0;
        }
        vector<vector<int>> dp(n, vector<int>(2, 0));
        dp[0][0] = 0, dp[0][1] = -1 * prices[0];
        for(int i = 1; i < n; i++) {
            dp[i][0] = max(dp[i - 1][0], dp[i - 1][1] + prices[i]);
            dp[i][1] = max(dp[i - 1][1], -1 * prices[i]);
        }
        return dp[n - 1][0];
    }
};
```

```c++ tab="O(1)"
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int n = prices.size();
        if(n <= 1) {
            return 0;
        }
        int dp_i_0 = 0, dp_i_1 = INT_MIN;
        for(int i = 0; i < n; i++) {
            dp_i_0 = max(dp_i_0, dp_i_1 + prices[i]);
            dp_i_1 = max(dp_i_1, -1 * prices[i]);
        }
        return dp_i_0;
    }
};
```

## k = +infinity

k 为正无穷，那我们就不需要记录这个状态，状态转移方程变为：

```
dp[i][0] = max(dp[i - 1][0], dp[i - 1][1] + prices[i]);
dp[i][1] = max(dp[i - 1][1], dp[i - 1][0] - prices[i]);
```

直接写空间复杂度 O(1) 的代码：

```c++
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int n = prices.size();
        if(n <= 1) {
            return 0;
        }
        int dp_i_0 = 0, dp_i_1 = INT_MIN;
        for(int i = 0; i < n; i++) {
            int tmp = dp_i_0;
            dp_i_0 = max(dp_i_0, dp_i_1 + prices[i]);
            dp_i_1 = max(dp_i_1, tmp - prices[i]);
        }
        return dp_i_0;
    }
};
```

## k = 2

上两个都和 k 关系不大，这个就需要处理 k 。状态转移方程无法化简。

```c++
dp[i][k][0] = max(dp[i - 1][k][0], dp[i -1][k][1] + prices[i]);
dp[i][k][1] = max(dp[i - 1][k][1], dp[i - 1][k - 1][0] - prices[i]);

dp[0][k][0] = max(dp[-1][k][0], dp[-1][k][1] + prices[i]) = 0;
dp[0][k][1] = max(dp[-1][k][1], dp[-1][k - 1][0] - prices[i]) = - prices[i];

dp[i][2][0] = max(dp[i - 1][2][0], dp[i - 1][2][1] + prices[i]);
dp[i][2][1] = max(dp[i - 1][2][1], dp[i - 1][1][0] - prices[i]);
dp[i][1][0] = max(dp[i - 1][1][0], dp[i - 1][1][1] + prices[i]);
dp[i][1][1] = max(dp[i - 1][1][1], - prices[i]);
```

我们不仅需要对 i 遍历，还需要遍历 k，要注意初始状态。当然 k 比较小，我们还可以直接列出来。

```c++ tab="三维 dp"
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int n = prices.size();
        if(n <= 1) {
            return 0;
        }
        int dp[n][3][2] = { 0 };
        for(int i = 0; i < n; i++) {
            for(int k = 2; k >= 1; k--) {
                if(i == 0) {
                    dp[i][k][0] = 0;
                    dp[i][k][1] = -1 * prices[i];
                    continue;
                }
                dp[i][k][0] = max(dp[i - 1][k][0], dp[i - 1][k][1] + prices[i]);
                dp[i][k][1] = max(dp[i - 1][k][1], dp[i - 1][k - 1][0] - prices[i]);
            }
        }
        return dp[n - 1][2][0];
    }
};
```

```c++ tab="优化"
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int dp_i10 = 0, dp_i11 = INT_MIN;
        int dp_i20 = 0, dp_i21 = INT_MIN;
        for(auto price : prices) {
            dp_i20 = max(dp_i20, dp_i21 + price);
            dp_i21 = max(dp_i21, dp_i10 - price);
            dp_i10 = max(dp_i10, dp_i11 + price);
            dp_i11 = max(dp_i11, -1 * price);
        }
        return dp_i20;
    }
};
```

## 任意给定的 k

一次交易买入卖出至少需要两天，所以当 k > n / 2 时，就等价于不限制次数了。对于有效限制的部分就按照上面 k = 2 时穷举即可。

```c++
class Solution {
public:
    int maxProfitWithoutK(vector<int>& prices) {
        int dp_i_0 = 0, dp_i_1 = INT_MIN;
        for(int i = 0; i < prices.size(); i++) {
            dp_i_0 = max(dp_i_0, dp_i_1 + prices[i]);
            dp_i_1 = max(dp_i_1, dp_i_0 - prices[i]);
        }
        return dp_i_0;
    }
    int maxProfit(int k, vector<int>& prices) {
        int n = prices.size();
        if(n <= 1) {
            return 0;
        }
        if(k > n / 2) {
            return maxProfitWithoutK(prices);
        }
        int dp[n][k + 1][2] = { 0 };
        for(int i = 0; i < n; i++) {
            for(int j = k; j >= 1; j--) {
                if(i == 0) {
                    dp[i][j][0] = 0;
                    dp[i][j][1] = -1 * prices[i];
                    continue;
                }
                dp[i][j][0] = max(dp[i - 1][j][0], dp[i - 1][j][1] + prices[i]);
                dp[i][j][1] = max(dp[i - 1][j][1], dp[i - 1][j - 1][0] - prices[i]);
            }
        }
        return dp[n - 1][k][0];
    }
};
```

## k = +infinity 含冷冻期

卖出股票后，第二天不能买入股票。稍微修改一下前面 k = +infinity 的状态方程。

```c++ hl_line="2"
dp[i][0] = max(dp[i - 1][0], dp[i - 1][1] + prices[i]);
dp[i][1] = max(dp[i - 1][1], dp[i - 2][0] - prices[i]);
```

添加一个变量记录前天的即可。

```c++
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        int n = prices.size();
        if(n <= 1) {
            return 0;
        }
        int dp_i_0 = 0, dp_i_1 = INT_MIN;
        int dp_i2_0 = 0; // 记录前天的
        for(int i = 0; i < n; i++) {
            int tmp = dp_i_0;
            dp_i_0 = max(dp_i_0, dp_i_1 + prices[i]);
            dp_i_1 = max(dp_i_1, dp_i2_0 - prices[i]);
            dp_i2_0 = tmp;
        }
        return dp_i_0;
    }
};
```

## k = +infinity 含手续费

每次交易要付手续费，也比较简单，只要再买入的时候减去手续费即可。

```c++
dp[i][0] = max(dp[i - 1][0], dp[i - 1][1] + prices[i]);
dp[i][1] = max(dp[i - 1][1], dp[i - 1][0] - prices[i] - fee);
```

```c++
class Solution {
public:
    int maxProfit(vector<int>& prices, int fee) {
        int n = prices.size();
        if(n <= 1) {
            return 0;
        }
        int dp_i_0 = 0, dp_i_1 = INT_MIN;
        for(int i = 0; i < n; i++) {
            int tmp = dp_i_0;
            dp_i_0 = max(dp_i_0, dp_i_1 + prices[i]);
            dp_i_1 = max(dp_i_1, tmp - prices[i] - fee);
        }
        return dp_i_0;
    }
};
```
