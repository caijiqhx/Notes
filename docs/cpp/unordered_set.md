# unordered_set

使用 `unordered_set<pair<>>` 时报错，标准库并未给 std::pair 提供哈希函数。

下面学一下自定义哈希函数，首先看 unorder_set 的定义：

```c++
template < class Key,                        // unordered_set::key_type/value_type
           class Hash = hash<Key>,           // unordered_set::hasher
           class Pred = equal_to<Key>,       // unordered_set::key_equal
           class Alloc = allocator<Key>      // unordered_set::allocator_type
           > class unordered_set;
```


