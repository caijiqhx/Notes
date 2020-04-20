# 二叉树的遍历

二叉树的遍历，就前中后和层序遍历。

递归形式很容易想，迭代要用栈，写的时候要想一下是怎么入栈的，而且感觉后序遍历的迭代也比较难理解。

在 leetcode 的题解里看到了一位带哥写的迭代遍历的 “颜色遍历” 方法，通过添加标志位让迭代与递归形式统一，方便理解，拿过来就写。

栈里存 `pair<bool, TreeNode*>`，以中序遍历为例，如果当前节点对应的标记为 true 表示未遍历过，那么就按照中序顺序倒序插入，false 则访问当前结点。

```c++ tab="颜色遍历框架"
class Solution {
public:
    vector<int> postorderTraversal(TreeNode* root) {
        if(root == nullptr) {
            return {};
        }
        vector<int> res;
        stack<pair<bool, TreeNode*>> st;
        st.push({true, root});
        while(!st.empty()) {
            auto flag = st.top().first;
            auto cur = st.top().second;
            st.pop();
            if(flag) {
                // 不同的遍历，修改此处的入栈顺序
                if(cur->right != nullptr) {
                    st.push({true, cur->right});
                }
                st.push({false, cur});
                if(cur->left != nullptr) {
                    st.push({true, cur->left});
                }
            }else {
                res.push_back(cur->val);
            }
        }
        return res;
    }
};
```