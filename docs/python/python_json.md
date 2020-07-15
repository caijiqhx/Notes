# Python 处理 json

> - [菜鸟学院 python3 json](https://www.runoob.com/python3/python3-json.html)

想搞个热榜聚合这种，看到有带哥的轮子 [今日热榜](https://github.com/tophubs/TopList) ，还给了接口，正好学一下 python 处理 json 数据。

JSON (JavaScript Object Notation) 是一种轻量型的数据交换格式。Python 使用 json 模块处理数据，包含两个函数：

- json.dumps() 编码 python -> json
- json.loads() 解码 json -> python

python 原始类型与 json 对应：

python 编码为 json 的转换表：

| Python                               | JSON            |
| ------------------------------------ | --------------- |
| dict                                 | object          |
| list, tuple                          | array           |
| str                                  | string          |
| int, float, int-&float-derived Enums | number          |
| True/False/None                      | true/false/null |

json 解码为 python 的对照表：

| JSON             | Python          |
| ---------------- | --------------- |
| object           | dict            |
| array            | list            |
| string           | str             |
| number(int/real) | int/float       |
| true/false/null  | True/False/None |
