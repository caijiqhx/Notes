# 排序

最重要的问题就是 [Kth Element](https://cyc2018.github.io/CS-Notes/#/notes/Leetcode%20%E9%A2%98%E8%A7%A3%20-%20%E6%8E%92%E5%BA%8F?id=%e5%bf%ab%e9%80%9f%e9%80%89%e6%8b%a9)。

需要日常复习快排。

复习排序算法，以 leetcode 912 排序数组为例复习各种排序算法

> 排序的本质就是消除逆序数，可以证明对于随机数组，逆序数是 O(n^2)的，而如果采用“交换相邻元素”的办法来消除逆序，每次正好只消除一个，因此必须执行 O(n^2)的交换次数，这就是为什么冒泡、插入等算法只能到平方级别的原因，反过来，基于交换元素的排序要想突破这个下界，必须执行一些比较，交换相隔比较远的元素，使得一次交换能消除多个逆序，希尔、快排、堆排等等算法都是交换比较远的元素，只不过规则各不同罢了.

| 排序算法     | 平均时间复杂度 | 最坏时间复杂度 | 空间复杂度       | 稳定性 |
| ------------ | -------------- | -------------- | ---------------- | ------ |
| 冒泡排序     | $O(N^2)$       | $O(N^2)$       | $O(1)$           | 稳定   |
| 选择排序     | $O(N^2)$       | $O(N^2)$       | $O(1)$           | 不稳定 |
| 插入排序     | $O(N^2)$       | $O(N^2)$       | $O(1)$           | 稳定   |
| 快速排序     | $O(N\log(N))$  | $O(N^2)$       | $O(\log(N))$     | 不稳定 |
| 三路快速排序 | $O(N\log(N))$  | $O(N^2)$       | $O(\log(N))$     | 不稳定 |
| 希尔排序     | $O(N^{1.3})$   |                | $O(1)$           | 不稳定 |
| 桶排序       | $O(N)$         | $O(N)$         | $O(\max - \min)$ | 稳定   |
| 堆排序       | $O(N\log(N))$  | $O(N\log(N))$  | $O(1)$           | 不稳定 |
| 归并排序     | $O(N\log(N))$  | $O(N\log(N))$  | $O(N)$           | 稳定   |

```c++ tab="冒泡排序"
void bubbleSort(vector<int>& nums) {
    for(int i = 0; i < nums.size(); i++) {
        for(int j = 0 ; j < i; j++) {
            if(nums[j] > nums[i]) {
                swap(nums[i], nums[j]);
            }
        }
    }
}
```

```c++ tab="选择排序"
// 每次选最小的与第一个元素交换，不稳定。
void selectSort(vector<int>& nums) {
        for(int i = 0; i < nums.size(); i++) {
            int minIndex = i;
            for(int j = i + 1; j < nums.size(); j++) {
                if(nums[j] < nums[minIndex]) {
                    minIndex = j;
                }
            }
            swap(nums[i], nums[minIndex]);
        }
    }
```

```c++ tab="插入排序"
// 将 i 插入到左侧的有序序列中，局部其实类似冒泡
// 最好 O(N)，即数组有序
void insertSort(vector<int>& nums) {
    for(int i = 0; i < nums.size(); i++) {
        for(int j = i; j > 0 && nums[j] < nums[j - 1]; j--) {
            swap(nums[j - 1], nums[j]);
        }
    }
}
```

```c++ tab="快速排序"
void quickSort(vector<int>& nums, int l, int r) {
    if(l >= r) {
        return;
    }
    swap(nums[l], nums[l + rand() % (r - l + 1)]);
    int finalPos = l + 1;
    // 找到 nums[l] 的值在数组中的最终位置
    // 找到小于基准值的就交换
    for(int i = l + 1; i <= r; i++) {
        if(nums[i] < nums[l]) {
            swap(nums[finalPos++], nums[i]);
        }
    }
    // 需要减 1 是因为要把 finalPos 位置的值交换到 l 位置，要用小于基准值的值交换
    swap(nums[l], nums[--finalPos]);
    quickSort(nums, l, finalPos - 1);
    quickSort(nums, finalPos + 1, r);
}
```

```c++ tab="快排 非递归"
// 快排的非递归就是用栈存子区间的边界
void quickSort(vector<int>& nums) {
    stack<pair<int, int>> st;
    st.push({0, nums.size() - 1});
    while(!st.empty()) {
        int l = st.top().first;
        int r = st.top().second;
        st.pop();
        swap(nums[l], nums[l + rand() % (r - l + 1)]);
        int finalPos = l + 1;
        for(int i = l + 1; i <= r; i++) {
            if(nums[i] < nums[l]) {
                swap(nums[i], nums[finalPos++]);
            }
        }
        swap(nums[l], nums[--finalPos]);
        if(l < finalPos - 1) {
            st.push({l, finalPos - 1});
        }
        if(r > finalPos + 1) {
            st.push({finalPos + 1, r});
        }
    }
}
```

```c++ tab="三路快排"
// 适用于数据中含大量重复元素
void quickSort(vector<int>& nums, int l, int r) {
    if(l >= r) {
        return;
    }
    int pivot = nums[l + rand() % (r - l + 1)];
    int left = l, right = r;
    // 普通快排的每次找到的是第一个大于基准的位置
    // 三路快排的左指针找到的是第一个等于基准的位置
    for(int i = left; i <= right;) {
        if(nums[i] == pivot) {
            i++;
        }else if(nums[i] < pivot) {
            swap(nums[i++], nums[left++]);
        }else {
            // 当前值大于基准值，与右侧交换，此时右侧还未访问到，所以 i 不递增
            swap(nums[i],nums[right--]);
        }
    }
    // [left, right] 间的值等于基准值
    quickSort(nums, l, left - 1);
    quickSort(nums, right + 1, r);
}
```

```c++ tab="希尔排序"
// 缩小增量的插入排序
// 时间复杂度与选取的增量序列有关
void shellSort(vector<int>& nums) {
    int n = nums.size();
    int step = 1;
    while(step < n / 3) {
        step = step * 3 + 1;
    }
    while(step >= 1) {
        for(int i = step; i < n; i++) {
            for(int j = i; j >= step && nums[j - step] > nums[j]; j -= step) {
                swap(nums[j - step], nums[j]);
            }
        }
        step /= 3;
    }
}
```

```c++ tab="桶排序"
// 桶排只适用于最大值与最小值差距不大，且值为整数的数据排序。
vector<int> bucketSort(vector<int>& nums) {
    if(nums.size() == 0) {
        return {};
    }
    int low = *min_element(nums.begin(), nums.end());
    int high = *max_element(nums.begin(), nums.end());
    // 桶的大小
    int bucketSize = high - low + 1;
    vector<int> bucket(bucketSize);
    for(auto num : nums) {
        bucket[num - low]++;
    }
    vector<int> res;
    for(int i = 0; i < bucketSize; i++) {
        for(int j = 0; j < bucket[i]; j++) {
            res.push_back(i + low);
        }
    }
    return res;
}
```

```c++ tab="堆排序"
// 堆是完全二叉树，所以方便用数组表示
// 建堆的时间复杂度为 O(n)
void adjust(vector<int> &nums, int rootPos, int size) {
    while(rootPos + 1 < size - rootPos) {
        int left = 2 * rootPos + 1;
        int right = 2 * rootPos + 2;
        int maxIndex = (right < size && nums[right] > nums[left] ? right : left);
        if(nums[maxIndex] > nums[rootPos]) {
            swap(nums[maxIndex], nums[rootPos]);
        }else {
            // 满足条件则不需要再调整
            break;
        }
        // 当前节点下沉
        rootPos = maxIndex;
    }
}
void headSort(vector<int> &nums) {
    int n = nums.size();
    for(int i = n / 2; i >= 0; i--) {
        adjust(nums, i, n);
    }
    // 出堆操作，把最大值放到最后，size--
    for(int i = n - 1; i > 0; i--) {
        swap(nums[0], nums[i]);
        adjust(nums, 0, i);
    }
}
```

```c++ tab="归并排序"
// 先把左右排序 然后合并
vector<int> mergeSort(vector<int>& nums, int l, int r) {
    if(l > r) {
        return {};
    }
    if(l == r) {
        return {nums[l]};
    }
    vector<int> res(r - l + 1);
    int mid = l + (r - l) / 2;
    auto left = mergeSort(nums, l, mid);
    auto right = mergeSort(nums, mid + 1, r);
    int i = 0, j = 0;
    int cnt = 0;
    while(i < (mid - l + 1) && j < (r - mid)) {
        if(left[i] < right[j]) {
            res[cnt++] = left[i++];
        }else {
            res[cnt++] = right[j++];
        }
    }
    while(i < mid - l + 1) {
        res[cnt++] = left[i++];
    }
    while(j < r - mid) {
        res[cnt++] = right[j++];
    }
    return res;
}
```
