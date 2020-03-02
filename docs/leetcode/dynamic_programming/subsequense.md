# 动态规划子序列问题

子序列问题是常见的算法问题，难点在于所求是不连续的序列。一般就是让求最长子序列，动态规划问题，时间复杂度为 $O(N^2)$。

dp 流程：定义 dp 数组、找出状态转移关系。

## 两种思路

### 一维 dp 数组

```c++ tab="一维"
int n = nums.length();
int[] dp = new int[n];

for(int i = 0; i < n; i++) {
    for(int j = 0; j < i; j++) {
        dp[i] = max(dp[i], dp[j] + ...)
    }
}
```

例如最长递增子序列问题，dp[i] 为以 nums[i] 结尾的最长递增子序列长度。

### 二维 dp 数组

```c++ tab="二维"
int n = nums.length();
int[][] dp = new int[n][n];

for(int i = 0; i < n; i++) {
    for(int j = 0; j < i; j++) {
        if(nums[i] == nums[j]) {
            dp[i][j] = dp[i][j] + ...
        }else {
            dp[i][j] = max(...)
        }
    }
}
```

主要是两个字符串/数组的子序列，如最长公共子序列问题。dp[i][j] 为 nums1[0...i] 与 nums2[0...j] 的最长公共子序列长度。

还有只涉及一个字符串/数组，如回文子序列长度。dp[i][j] 为 nums[i...j] 间的子序列长度。