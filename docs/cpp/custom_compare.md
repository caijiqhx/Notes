# C++ 中自定义比较函数

记录一下 C++ 中自定义比较函数的几种用法。

## priority_queue 优先队列

优先队列也就是堆，这里记录一下如何自定义优先队列的比较函数。

默认是 `<`，对应大顶堆，通常我们都用小顶堆，所以定义的时候应该写 `priority_queue<int, vector<int>, greater<int>> pq`，指定使用 `>` 比较。

或者我们重载 `<` 运算符：

```c++
// 这里 函数参数列表后加 const 的用法仅用于类的成员函数，表示函数不能修改类成员
bool operator<(const Type&a, const Type& b) const {
    ...
}
```

或者定义一个比较类，重载它的 `()` 运算符：

```c++
struct cmp {
    bool operator()(const Type&a, const Type& b) {
        ...
    }
};
priority_queue<Type, vector<Type>, cmp> pq;
```

## sort, priority_queue, map, set 比较

默认都是小于号，都是升序，优先队列默认是大顶堆因为出堆都是末尾元素出堆。

sort 自定义可以用一个 `bool cmp(const Type& a, const Type& b) {}` 函数，传入 `cmp`。或者像上面一样定义一个类，传入 `cmp()`。

map 和 set 都是定义类传入 `cmp()`。
