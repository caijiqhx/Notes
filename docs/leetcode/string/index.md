# 字符串

常见的字符串处理。

## replace

替换字符串函数

```c++
// 把 [pos, pos + len) 间的子串替换为 str
string& replace (size_t pos,        size_t len,        const string& str);
// 把 [i1, i2) 间的子串替换为 str
string& replace (const_iterator i1, const_iterator i2, const string& str);
// 用 str 的 [subpos, subpos + sublen) 的子串替换 [pos, pos + len)
string& replace (size_t pos,        size_t len,        const string& str,
                 size_t subpos, size_t sublen = npos);
// C-string 替换
string& replace (size_t pos,        size_t len,        const char* s);
string& replace (const_iterator i1, const_iterator i2, const char* s);
// buffer 中前 n 个字符
string& replace (size_t pos,        size_t len,        const char* s, size_t n);
string& replace (const_iterator i1, const_iterator i2, const char* s, size_t n);
// 替换为 n 个字符 c
string& replace (size_t pos,        size_t len,        size_t n, char c);
string& replace (const_iterator i1, const_iterator i2, size_t n, char c);
// 用 [first, last) 间子串替换 [i1, i2)
template <class InputIterator>
  string& replace (const_iterator i1, const_iterator i2,
                   InputIterator first, InputIterator last);
// 使用初始化列表中的字符替换
string& replace (const_iterator i1, const_iterator i2, initializer_list<char> il);
```

