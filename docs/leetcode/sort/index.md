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

```

```c++
class Solution {
public:
    /**
     * <归并排序>
     * 时间复杂度: 最好O(n*log(n)) 最坏O(n*log(n)) 平均O(n*log(n)) 稳定
     * 空间复杂度: O(n)
     */
    vector<int> mergeSort(vector<int> &nums, int l, int r) {
        if (l > r) return {}; // 左指针大于右指针,直接返回空
        if (l == r) return {nums[l]}; // 归并到单个数直接返回,不做排序
        vector<int> res; // 临时数组,返回排序好的部分数组
        int m = l + (r - l) / 2; // 二分
        auto ln = mergeSort(nums, l, m); // 左侧归并
        auto rn = mergeSort(nums, m + 1, r); // 右侧归并
        int i = 0;
        int j = 0;
        while (i < ln.size() && j < rn.size()) { // 只要有一个数组被遍历完,则跳出循环
            if (ln[i] <= rn[j]) {
                res.push_back(ln[i++]);
            } else {
                res.push_back(rn[j++]);
            }
        }
        while (i < ln.size()) res.push_back(ln[i++]); // 若右数组被遍历完,则说明左数组剩下的所有数都大于右数组,直接放在临时数组最后
        while (j < rn.size()) res.push_back(rn[j++]); // 同理
        return res;
    }

    /**
     * <堆排序>
     * 时间复杂度: 最好O(n*log(n)) 最坏O(n*log(n)) 平均O(n*log(n)) 不稳定
     * 空间复杂度: O(1)
     */
    void heapSort(vector<int> &nums) {
        // 构建大顶堆,从第一个非叶子节点开始,向左依次进行下沉操作
        for (int i = nums.size() / 2; i >= 0; --i) {
            siftdown(nums, i, nums.size());
        }
        // 进行出堆操作,相当于pop()
        for (int i = nums.size() - 1; i > 0; --i) {
            swap(nums[0], nums[i]); // 出堆(将最大值放置数组尾,堆size - 1)
            siftdown(nums, 0, i); // 将根执行下沉操作
        }
    }

    void siftdown(vector<int> &nums, int root, int size) {
        /**
         * 构造大顶堆的下浮操作
         */
        while (2 * root + 1 < size) { // 当p存在孩子时
            int c1 = 2 * root + 1; // p节点的左孩子
            int c2 = 2 * root + 2; // p节点的右孩子
            int c = (c2 < size && nums[c2] > nums[c1]) ? c2 : c1; // c是值最大的孩子节点
            if (nums[c] > nums[root]) { // 若孩子节点大于父亲节点,交换位置
                swap(nums[c], nums[root]);
            } else {
                break; // 该点满足堆条件,又因为下方已经成堆,所以不必向下建堆
            }
            /**
             * 若此时节点不是最大值,则有可能也小于
             * <以该节点为根的下一个子堆>的孩子节点
             * 所以需要将该节点也进行一次下沉操作
             */
            root = c;
        }
    }

```
