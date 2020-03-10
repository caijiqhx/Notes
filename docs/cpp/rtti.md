# C++ 运行时类型识别

> - C++ Primer Chapter 19.2

C++ 运行时类型识别（run-time type identification, RTTI) 的功能通过两个运算符实现：

- typeid 运算符，用于返回表达式的类型。
- dynamic_cast 运算符，用于将基类的指针或引用安全地转换成派生类的指针或引用。

当我们将这两个运算符用于某种类型的指针或引用，并且该类型含有虚函数时，运算符将使用指针或引用所绑定对象的动态类型。

这两个运算符特别适用于以下情况：**我们想使用基类对象的指针或引用执行某个派生类操作并且该操作不是虚函数。**一般来说，只要有可能我们应该尽量使用虚函数。当操作被定义成虚函数时，编译器将根据对象的动态类型自动地选择正确的函数版本。

然而，并非任何时候都能定义一个虚函数。如果我们无法使用虚函数，则可以使用一个 RTTI 运算符。另一方面，与虚成员函数相比，使用 RTTI 运算符风险更高：程序员必须清楚地知道转换的目的类型并且检查类型转换是否被成功执行。

## dynamic_cast 运算符

dynamic_cast 的使用形式如下：

```c++
dynamic_cast<type*>(expr)   // expr 必须是一个有效的指针
dynamic_cast<type&>(expr)   // expr 必须是一个左值
dynamic_cast<type&&>(expr)  // expr 不能是左值
```

type 必须是一个类类型，并且通常情况下该类型应该含有虚函数。expr 的类型必须符合以下三个条件种的任意一个：目标 type 的公有派生类、目标 type 的公有基类或者目标 type 的类型。如果符合，则类型转换可以成功。否则，转换失败。如果指针类型转换失败，结果为 0（空指针）。引用类型转换失败，则抛出一个 bad_cast 异常。

### 指针类型的 dynamic_cast

```c++
class Base { virtual void f() {} };
class Derived : public Base { };

if(Derived *dp = dynamic_cast<Derived*>(bp)) {
    // use dp
}else {
    // use bp
}
```

如果 bp 指向 Derived 对象，则以上的类型转换初始化 dp 并令其指向 bp 所指的 Derived 对象。if 内部使用 Derived 操作的代码时安全的。否则，类型转换的结果为 0，意味着转换失败，else 语句执行相应的 Base 操作。

> 我们可以对一个空指针执行 dynamic_cast，结果是所需类型的空指针。
>
> 在条件部分执行 dynamic_cast 操作可以确保类型转换和结果检查在同一条件表达式种完成。

### 引用类型的 dynamic_cast

引用类型的 dynamic_cast 与 指针类型的 dynamic_cast 在表示错误发生的方式上略有不同。因为不存在所谓的空引用，所以对引用的类型转换失败时，程序抛出了一个名为 std::bad_cast 的异常，定义于 typeinfo 标准库头文件中。

```c++
void f(const Base &b) {
    try {
        const Derived &d = dynamic_cast<const Derived &>(b);
    }catch (bad_cast) {
        // cast fail
    }
}
```

## typeid 运算符

为 RTTI 提供的第二个运算符是 typeid 运算符，它允许程序向表达式提问：你的对象是什么类型？
