# N 叉树

> - [探索 N 叉树](https://leetcode-cn.com/explore/learn/card/n-ary-tree/)

看到 leetcode 探索里有字典树的，先学一下 N 叉树。

## N 叉树的遍历

N 叉树遍历就前序和后序两种，对子结点通常就从左到右访问。

```c++ tab="N 叉树"
class Node {
public:
    int val;
    vector<Node*> children;

    Node() {}

    Node(int _val) {
        val = _val;
    }

    Node(int _val, vector<Node*> _children) {
        val = _val;
        children = _children;
    }
};
```

