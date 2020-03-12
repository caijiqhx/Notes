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

typeid 表达式的形式为 typeid(expr)，其中 expr 可以是任意表达式或类型的名字。typeid 操作的结果是一个常量对象的引用，该对象的类型是标准库类型 type_info 或 type_info 的公有派生类型。type_info 类定义在 typeinfo 头文件中。

typeid 运算符可以作用于任意类型的表达式，顶层 const 被忽略，如果表达式是一个引用，则 typeid 返回该引用所引对象的类型。不过当 typeid 作用于数组或函数时，并不会执行向指针的标准类型转换。也就是说对数组 a 执行 typeid(a)，得到的结果是数组类型而非指针类型。

当运算对象不属于类类型或者是一个不包含任何虚函数的类时，typeid 运算符指示的是运算对象的静态类型。而当运算对象是定义了至少一个虚函数类的左值时，typeid 的结果知道运行才会求得。

```c++
Derived *dp = new Derived;
Base *bp = dp;
if(typeid(dp) == typeid(bp)) {
    // bp and dp point to the same type
}
if(typeid(*bp) == typeid(Derived)) {
    // bp point to Derived
}
```

要注意的是，typeid 应该作用于对象，如果判断代码为 `typeid(bp) == typeid(Derived)`，则一直不会满足。typeid 作用于指针时返回的结果是该指针的静态类型。

typeid 是否需要运行时检查决定了表达式表达式是否会被求值。只有当类型含有虚函数时，编译器才会对表达式求值。如果类型不含有虚函数，则 typeid 返回表达式的静态类型；编译器无须对表达式求值也能知道表达式的静态类型。

如果表达式的动态类型可能与静态类型不同，则必须在运行时对表达式求值以确定返回的类型。即 typeid(\*p) 的情况，如果指针 p 所指的类型不含有虚函数，则 p 不必非得是一个有效的指针。否则，\*p 将在运行时求值，此时 p 必须是一个有效的指针。如果 p 是一个空指针，则 type(\*p) 将抛出一个 bad_typeid 异常。

## 使用 RTTI

某些条件下 RTTI 非常有用，比如当我们想为具有继承关系的类实现相等运算符时。两个对象类型相同且对应数据成员取值相同，则说这个两个对象相等。在类的继承体系中，每个派生类负责添加自己的数据成员，因此派生类的相等运算符必须把派生类的新成员考虑进来。

一种容易想到的解决方案是定义一套虚函数，令其在继承体系的各个层次上分别执行相等性判断。此时我们可以为基类的引用定义一个相等运算符，该运算符将它的工作委托给虚函数 equal，由 equal 负责实际的操作。

然而，上述方案很难奏效。虚函数的基类版本和派生类版本必须具有相同的形参类型（否则就变成重载）。如果我们想定义一个虚函数 equal，则该函数的形参必须是基类的引用，equal 函数只能使用基类的成员，而不能比较派生类独有的成员。

首先要明确，类型不同则结果为 false，试图比较一个基类对象和一个派生类对象，则应返回 false。因此可以用 RTTI 解决问题。我们定义相等运算符的形参是基类的引用，然后用 typeid 检查两个对象的类型是否一致。类型一致才调用 equal 函数。每个类的 equal 函数负责比较类型自己的成员。运算符接收 Base& 形参，在比较操作前把对象转换成运算符所属的类类型。

```c++
class Base {
    friend bool operator==(const Base&, const Base&);
public:
protected:
    virual bool equal(const Base&) const;
};
class Derived : public Base {
public:
protected:
    bool equal(const Base&) const;
}
```

定义整体的相等运算符，先判断类型是否相同，相同再调用虚函数 equal：

```c++
bool operator==(const Base& lhs, const Base& rhs) {
    return typeid(lhs) == typeid(rhs) && lhs.equal(rhs);
}
```

虚函数 equal，每个类都必须定义自己的 equal 函数，派生类函数要做的第一件事就是类型转换：

```c++
bool Derived::equal(const Base &rhs) const {
    // 调用之前已经检查过 lhs 与 rhs 的类型相同，因此可以成功转换
    auto r = dynamic_cast<const Derived&>(rhs);
    // 比较两个 Derived 对象的操作
}
bool Base::equal(const Base &rhs) const {
    // 比较两个 Base 对象的操作
}
```

## type_info 类

type_info 类的精确定义随编译器不同略有差异，不过 C++ 标准规定 type_info 类必须定义在 typeinfo 头文件中，且至少提供了以下的操作：

| type_info 的操作   |                                                                                 |
| ------------------ | ------------------------------------------------------------------------------- |
| t1 == t2, t1 != t2 | 判断 type_info 对象 t1 和 t2 是否表示同一类型                                   |
| t.name()           | 返回一个 C 风格字符串，表示类型名字的可打印形式。类型名字的生成方式因系统而异。 |
| t1.before(t2)      | 返回一个 bool 值，表示 t1 是否位于 t2 之前。顺序依赖于编译器                    |

type_info 类一般是作为一个基类出现，所以它还应该提供一个公有的虚析构函数。当编译器希望提供额外的类型信息时，通常在其派生类中完成。

type_info 没有默认构造函数，它的拷贝和移动构造函数以及赋值构造运算符都定义为 delete。创建 type_info 对象的唯一途径是使用 typeid 运算符。

```c++
class A {
public:
    virtual ~A() {}
};
class B : public A { };
class C : public B { };

int main() {
    A *pa = new C;
    cout << typeid(pa).name() << endl;
    C cobj;
    A &ra = cobj;
    cout << typeid(&ra).name() << endl;
    B *px = new B;
    A &ra2 = *px;
    cout << typeid(ra2).name() << endl;
}
// output:
// P1A
// P1A
// 1B
```
