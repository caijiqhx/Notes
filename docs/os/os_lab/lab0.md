# Lab 0

### ucore 通用数据结构

#### 双向循环链表

常规的 data, prev, next 节点因为每种特定数据类型不一致会导致代码冗余。

ucore 中定义为：

```c++
struct list_entry {
    struct list_entry *prev, *next;
};
```

链表节点​不再包含传统的 data 数据域，以空闲内存块列表为例：

```c++
typedef struct {
    list_entry_t free_list;  // 链表头
    unsigned int nr_free;
} free_area_t;

// struct Page 页结构体
struct Page {
    atomic_t ref;
    ...
    list_entry_t page_link;  // 空闲链表节点
}
```

通过链表节点成员变量访问到它的所有者，即某特定数据结构的变量，使用 `le2xxx(le, member)` 的宏。要遍历空闲内存块链表中所有节点所在的 Page 变量：

```c++
free_area_t free_area;
list_entry_t *le = &free_area.free_list;
// 遍历循环链表
while((le=list_next(le)) != &free_area.free_list) {
    struct Page *p = le2page(le, page_link); // 传入 page_link 成员变量的地址
}

// 使用的宏
// 获取 type 结构体 member 成员的偏移地址
#define offsetof(type, member) ((size_t)(&((type *)0)->member))
// member 成员地址减去其结构体偏移地址就得到了 type 结构体遍历地址
#define to_struct(ptr, type, member) ((type *)((char *)(ptr) - offsetof(type, member)))
#define le2page(le, member) to_struct((le), struct Page, member)
```
