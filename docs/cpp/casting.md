# C++ 类型转换

一直不太懂 C++ 的类型转换，以前只会 (type)var 这种。

> - [如何攻克 C++ 中复杂的类型转换？](https://zhuanlan.zhihu.com/p/80609182)
> - [C++ 笔记 · C++ 类型转换](https://zhuanlan.zhihu.com/p/80609182)

## 引言

对于一个变量，必须要回答三个问题：

1. 在哪可以访问这个变量的起点？
2. 从起点向后需要读取多少内存？
3. 如何解析读取到的二进制数据？

问题 1 由内存地址回答，问题 2 和 3 由类型回答。而 void 及 void\* 显然无法回答后两个问题，因此无法取值。

两个不同类型的变量，对问题 2 和 3 的答案不同，因此不同类型的变量无法直接运算，就需要进行类型转换。由此派生出两个概念：隐式和显式。

隐式类型转换指不通过专门的类型转换操作，而是通过其他规定或代码上下文隐式发生的类型转换；而显式类型转换则通过专门的类型转换操作进行转换，显式类型转换具有强制性。

下面将从隐式类型转换入手，逐步讨论各类 C++ 的类型转换问题。

## 类型提升与算术类型转换

算术类型转换专指 C++ 提供的各种内置算术类型之间的隐式类型转换。

C++ 内置的算术类型如下：

- bool
- char, signed char, unsigned char
- (unsigned) short, int, long, long long
- float, double, long double
- size_t 等其他特殊类型

算术类型转换是一类不完全明确的，且与底层密切相关的隐式类型转换。主要遵循以下原则：

1. 对于同类算术类型，如 short 与 int、float 与 double，占用较小内存的类型将转换成另一类型，称为称为类型提升；
2. 整型转换为浮点数；
3. 仅当无符号类型占用的内存小于有符号类型时，无符号类型才发生类型提升从而转为有符号类型，否则有符号类中转为无符号类型。

```c++
int main()
{
    unsigned short a = 1;
    unsigned b = 1;
    cout << (a > -1) << " " << (b > -1) << endl;
}
// output:
// 1 0
```

以上的代码中，a 转换为 int 而与 b 比较的 -1 转换为 unsigned。

## 转换构造函数

### 定义转换构造函数

C++ 中，如果一个构造函数满足以下所有条件，则其称为一个转换构造函数：

1. 至多有一个不含默认值的形参；
2. 第一形参的类型不为类本身或其附加类型（否则此构造函数将成为拷贝或移动构造函数）。

如果一个定义了某种转换构造函数，则被定义的类型将可以通过任何类型转换方式转为当前类型。转换构造函数可用于赋值和实参传递时的隐式类型转换以及基于 static_cast 的显式类型转换。

```c++
class A
{
private:
    int a;
    int b;

public:
    A(int _a, int _b = 0) : a(_a), b(_b)
    {
        cout << a << " " << b << endl;
    }
};

void test(A) {}

int main()
{
    A a(1, 2);
    A(2);       // 显式转换
    a = 3;      // 赋值隐式转换
    test(4);    // 实参传递的隐式转换
    return 0;
}
// output:
// 1 2
// 1 0
// 3 0
```

以上的代码中，定义了从 int 到 A 的转换构造函数。

### 阻止基于转换构造函数

定义了转换构造函数，相当于建立了两个类型转换的通道。可使用 explicit 关键字禁用基于转换构造函数进行的隐式类型转换。但是不影响显式转换和构造函数正常调用。

```c++
class A
{
private:
    int a;
    int b;

public:
    explicit A(int _a, int _b = 0) : a(_a), b(_b)
    {
        cout << a << " " << b << endl;
    }
};

void test(A) {}

int main()
{
    A a(1, 2);
    A(2);
    static_cast<A>(3); // 不影响强制类型转换
    // a = 3;       禁止赋值隐式转换
    // test(4);     禁止传参时的隐式转换
    return 0;
}
```

## 类型转换运算符

转换构造函数定义了其他类型向类类型的转换方案，类型转换运算符则定义了与之相反的过程：即定义了类类型向其他类型的转换方案。当类定义了某种类型的类型转换符后，类类型将可以向被定义类型发生类型转换。

```c++
class A
{
private:
    int a;
    int b;

public:
    operator int()
    {
        cout << "A convert to int:" << a << endl;
        return a;
    }
    explicit A(int _a, int _b = 0) : a(_a), b(_b)
    {
        cout << a << " " << b << endl;
    }
};

void test(int) {}

int main()
{
    A a(1, 2);
    test(a);    // 传参隐式转换
    int b = a;  // 赋值隐式转换
    return 0;
}
// output:
// 1 2
// A convert to int: 1
// A convert to int: 1
```

与转换构造函数类似，可以通过 explicit 函数禁用类型转换符的隐式转换，同样不影响显式类型转换。另外，对于 operator bool 在条件表达式或逻辑表达式中的隐式类型转换不受 explicit 影响。

## 继承类到基类的类型转换

### 静态类型与动态类型

C++ 的继承机制决定了这样的抽象类型：继承类 = 基类部分 + 继承类部分。这意味着每一个继承类都含有其所有基类的数据各一份。也就是说，对于一个继承类对象，对其基类部分进行操作显然是可行的。主要包括：

1. 得到基类部分的数据；
2. 将类型转换为基类类型（以丢失某些信息为代价）。

我们可以将一个继承类对象直接赋值给一个基类类型的变量，这建立在隐式类型转换之上，称为继承类到基类的类型转换，或称为向上类型转换。分为以下几种情况：

```c++
struct A {};
struct B: A {};
int main()
{
    A a1 = B();    // 值向上转换
    A *a2 = new B; // 指针向上转换
    A &a3 = a1;    // 左值引用向上转换
    A &&a4 = B();  // 右值引用向上转换
}
```

以上代码中，a1 是类型 A 的非指针或引用变量，因此其内存大小就是 A 类对象的大小。a1 得到了 B 类型对象的 A 类部分。（不过这里的赋值操作调用了 A 类的赋值运算符，而非隐式类中转换。这种问题之后再看吧。）

对于变量 a2, a3, a4 其类型都是类型 A 的指针或引用，而非 A 类对象。由于指针本身并不与类型直接相关，因此理论上此类变量存放的值可以是一个非 A 类型的数据。

由此，我们引入 静态类型 与 动态类型 的概念。

C++ 中，一个变量声明的类型称为静态类型，而其实际存储的数据的类型称为动态类型。绝大多数情况下，静态类型与动态类型必须一致，如果不一致，将发生隐式类型转换或引发编译错误。当且仅当使用基类的指针或引用存储继承类对象时，变量的静态类型与动态类型将不一致。

此时虽然看上去发生了向上类型转换，但实际上并未发生，此过程称为动态绑定。

一个变量的静态类型，决定了由此变量能够访问到的成员名称。当静态类型是基类指针或引用时，即使变量存放的是继承类对象，也只能访问到基类中声明的成员名称。

即：如果发生向上类型转换的类型是类的指针或引用，将以丢失继承类部分的成员名称为代价进行向上类型转换。

但由于虚函数的存在，访问成员名称得到的实际成员函数将不一定与静态类型保持一致，这是 C++ 多态的核心。

### 阻止向上类型转换

此时提出一个问题：为什么继承类可以访问基类的成员？

其实这并不应该，因为继承类并不是复制其基类，而只有继承类本身的部分。因此原则上其本身是没有访问基类的成员的。

继承类对象之所以能够访问基类成员，是因为在访问中，继承类的 this 指针通过向上类型转换操作转换成了一个基类的指针，然后以基类指针的身份访问到了基类的成员。

如果希望阻止这种隐式的向上类型转换呢？我们需要回顾 public, protected, private 三个关键字。

- public: 用于访问说明符时，表示对类的一切用户可见；用于继承时，表示继承时不修改基类的一切访问说明符。
- protected: 用于访问说明符时，表示仅对类的继承用户可见，对类的实例用户不可见；用户继承时，表示将基类的一切 public 访问说明符在基类中修改为 protected。
- private: 用于访问说明符时，表示对一切类的用户不可见；用于继承时，表示将基类的一切 public 和 protected 访问说明符在继承类中修改位 private。

从向上类型转换的角度考虑：

- public: 不阻止任何用户进行向上类型转换。
- protected: 阻止类的实例用户进行向上类型转换。
- private: 阻止一切用户进行向上类型转换。

```c++
struct A {};
struct B: A {}; // 不阻止任何B类的用户向A进行类型转换
struct C: protected A {}; // 阻止C类的实例用户向A进行类型转换
struct D: private A {}; // 阻止D类的一切用户向A进行类型转换
struct E: B { void test() { static_cast<A *>(this); } }; // B类的继承类用户可以向A进行类型转换
struct F: C { void test() { static_cast<A *>(this); } }; // C类的继承类用户可以向A进行类型转换
struct E: D { void test() { static_cast<A *>(this); } }; // Error！D类的继承类用户不可以向A进行类型转换
int main()
{
    static_cast<A *>(new B); // B类的实例用户可以向A进行类型转换
    static_cast<A *>(new C); // Error！C类的实例用户不可以向A进行类型转换
    static_cast<A *>(new D); // Error！D类的实例用户不可以向A进行类型转换
}
```

B, C, D 以三种不同方式继承类 A，同时为类 B, C, D 各定义了一个继承类用户和一个实例用户。

### 多重继承与向上类型转换

对于多重继承，其向上类型转换对于同一个继承层的多个基类是全面进行的。

```c++
struct A { int i; };
struct B { int i; };
struct C: A, B { int i; };
struct D: A, B {};

int main()
{
    C.i; // 访问C::i
    D.i; // Error！存在二义性！
}
```

对于类 C，由于其自身定义了变量 i，访问时未发生向上类型转换。而对于类 D，自身没有定义变量 i，故访问 D 类的 i 变量时需要在其各个基类分别查找，此时存在二义性。

## 其他隐式类型转换

C++ 还定义了一些特殊的类型转换，以下为常见情况：

### 0 转换为空指针

```c++
int main() {
    int *p = 0;
}
```

### 数组退化为指针

函数传参是数组会退化为指针。

```c++
int main() {
    int a[10];
    int *p = a;
}
```

### 空指针或数字 0 转换为 false，其他指针或数字转为 true

```c++
int main() {
    if(ptr) {}
    if(2) {}
}
```

### T 转换为 void

```c++
int main() {
    void *p = new int;
}
```

### 非 const 转换为 const

```c++
int main() {
    int *a;
    const int *b = a; // 常量指针，指向常量的指针，不可通过指针修改指向的值
    int *const c = a; // 指针常量，不可修改指针指向的地址
}
```

## 显式类型转换

### 旧式风格的类型转换

```
type(expr)  // 函数形式的强制类型转换
(type)expt  // C 语言风格的强制类型转换
```

### 现代 C++ 风格的类型转换

```
cast-name<type>(expr)
```

cast-name 有四种类型转换运算符 static_cast, dynamic_cast, const_cast, reinterpret_cast，表示不同的转换方式。

### static_cast

```
static_cast<type>(expr)
```

任何编写程序时能够明确的类型转换都可以使用 static_cast（不能转换掉底层 const, volatile, \_\_unaligned 属性）。由于不提供运行时的检查，所以叫 static_cast。

主要在以下几种场合中使用：

1. 用于类层次结构中，父类和子类之间指针和引用的转换：进行向上转换，把子类对象的指针/引用转换为父类指针/引用，这种转换是安全的；进行向下转换，把父类对象的指针/引用转换成子类指针/引用，这种转换是不安全的；
2. 用于基本数据类型之间的转换；
3. 把 void 指针转换成目标类型指针（极不安全）。

static_cast 使用需要编程时确认安全性。

### dynamic_cast

```
dynamic_cast<type>(expr)
```

相比于 static_cast，dynamic_cast 会在运行时检查类型转换是否合法，具有一定的安全性。但是运行时检查会消耗一些性能。

使用场景与 static 相似，向上转换安全，向下转换会检查，比 static 安全。

**dynamic_cast 转换仅适用于指针或引用。**

在转换可能发生的前提下，dynamic_cast 会尝试转换，若指针转换失败，则返回空指针，若引用转换失败，则抛出异常 bad_cast。

#### 向下的转换

```c++
class A { virtual void f() {} };
class B : public A { };
int main () {
    A *pA = new B;
    B *pB = dynamic_cast<B*>(pA);
}
```

#### void\* 的转换

一些情况下，需要将指针转换为 void\*，然后在合适的时候重新将 void\* 转换为目标类型指针。

```c++
class A{ virtual void f() {} };
int main() {
    A *pA = new A;
    void *pv = dynamic_cast<void*>(pA);
}
```

#### 菱形继承中的向上转换

首先定义一组菱形继承的类：

```c++
class A { virtual void f() {}; };
class B :public A { void f() {}; };
class C :public A { void f() {}; };
class D :public B, public C { void f() {}; };
int main() {
    D *pD = new D;
    A *pA = dynamic_cast<A*>(pD);
}
```

此种情况下，D 对象指针能否安全的转换为 A 类型指针？

此处 B, C 都继承了 A，且都实现了虚函数，导致在进行转换时，无法选择一条转换路径。此时需要先转换为 B 或 C，再转换为 A。

### const_cast

```
const_cast<type>(expr)
```

const_cast 用于移除类型的 const, volatile, \_\_unaligned 属性。

常量指针或引用被转换成非常量指针或引用，仍然指向或引用原来的对象。

### reinterpret_cast

```
reinterpret_cast<type>(expr)
```

非常激进的指针类型转换，在编译器完成，可以转换任何类型的指针，所以极不安全。
