# 二分查找

> 参考：
> 
> - [二分查找详解](https://labuladong.gitbook.io/algo/suan-fa-si-wei-xi-lie/er-fen-cha-zhao-xiang-jie)

Knuth 大佬说过：

`Although the basic idea of binary search is comparatively straightforward, the details can be surprisingly tricky...`

思路很简单，细节是魔鬼。

计算 mid 防溢出：`mid = left + (right - left)/2`

- 查找一个数：

```c++
int search(vector<int>& nums, int target) {
    int l = 0, r = nums.size() - 1;
    int mid = 0;
    while(l <= r) {
        mid = l + (r - l)/2;
        if(nums[mid] == target){
            return mid;
        }else if(nums[mid] < target) {
            l = mid + 1;
        }else if(nums[mid] > target) {
            r = mid - 1;
        }
    }
    return -1;
}
```

while 的条件是 `l <= r`，因为我们的检索区间是 `[l, r]`。返回的 l 是插入的位置。

- 查找左侧边界，如果 mid 处的值大于等于 target，在左侧搜索；否则在右侧搜索。

```c++
int left_bound(vector<int>& nums, int target) {
    int l = 0, r = nums.size();
    int mid = 0;
    while(l < r) {
        mid = l + (r - l)/2;
        if(nums[mid] == target) {
            r = mid;
        }else if(nums[mid] < target) {
            l = mid + 1;
        }else if(nums[mid] > target) {
            r = mid;
        }
    }
    if(l == nums.size()) {
        return -1;
    }
    return nums[l] == target ? l : -1;
}
```

- 查找右侧边界，mid 小于等于 target，在右侧搜索；否则在左侧。

```c++
int right_bound(vector<int>& nums, int target) {
    int l = 0, r = nums.size();
    int mid = 0;
    while(l < r) {
        mid = l + (r - l)/2;
        if(nums[mid] == target) {
            l = mid + 1;
        }else if(nums[mid] < target) {
            l = mid + 1;
        }else if(nums[mid] > target) {
            r = mid;
        }
    }
    if(l == 0) {
        return -1;
    }
    return nums[l - 1] == target ? l - 1 : -1;
}
```