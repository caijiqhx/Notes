# C++ 实现 STL 标准库和算法

> [实验楼：C++ 实现标准库和算法](#https://www.shiyanlou.com/courses/1166)

## template 编程

本节内容主要讲述 C++11 模板的用法，同时简单讲解迭代器的相关知识，为后面的容器和算法的内容作铺垫。

### 基本语法

模板编程是 STL 的基石，也是 C++11 的核心特性之一。模板的基本语法如下：

```c++
template <typename/class T>
```

`T` 叫做模板形参，一旦模板被实例化，`T` 也会变成具体的类型。

### 模板函数

```c++
template <typename T>
T  add(const T lva ,const T rva) 
{
     T a ;
     a = lva + rva;
    return a;    
 }
```

以上是一个模板函数的简单示例，`template` 关键字告知编译器模板和参数必要信息。函数模板支持默认参数，顺序任意。在此例中需要两个参数的类型一致。可以添加模板类型参数实现不同类型相加。

### 类模板和成员模板

#### 类模板

C++11 不仅支持对函数的模板化，也支持对类的模板：

```c++
 template <class T>
 class Myclass
 {
     T a;
     public:
         T add(const T lva ,const T rva);
 };

 template <class T>
 T Myclass<T>::add(const T lva, const T rva)
 {
     a = lva + rva;
     return a;
 }
```

实例化类时需要指定类型模板参数，类模板也支持默认参数。但必须严格从右往左默认化。

#### 成员模板

class, struct, template class 的成员也可以使用模板。

```c++
template <class T>
class Myclass
{
    public:
        T a;
        template <typename type_1 , typename type_2>
        type_1 add(const type_1 lva ,const type_2 rva);
};

template <class T>
template <typename type_1,typename type_2>
type_1 Myclass<T>::add(const type_1 lva, const type_2 rva)
{
    a = lva + rva;
    return a;
}
```

类的声明中使用了一个嵌套的模板声明，且通过作用域运算符 `::` 指出 `add()` 是类的成员，需要注意的一点，有些编译器不支持模板成员，有些编译器不支持在类外定义。甚至允许在模板类中再建立模板类：

```c++
 template <class T>
 class Myclass
 {
     public:
        T a;
        template <typename type_1 , typename type_2>
         type_1 add(const type_1 lva ,const type_2 rva);

         template <class type_3>
         class Myclass_2;         // 声明放在这里，具体定义放在类外进行。
         Myclass_2<T> C;          // 定义一个Myclass_2 类 A。使用 T 进行实例化
 };

 template <class T>
     template <typename type_1,typename type_2>
 type_1 Myclass<T>::add(const type_1 lva, const type_2 rva)
 {
     a = lva + rva;
     return a;
 }

 template <class T>
     template <class type_3>
     class Myclass<T>::Myclass_2
     {
         public:
             type_3 value;
             type_3 sub(const type_3 a , const type_3 b) {vlaue = a - b;} 
     };
```

### 模板里中的静态成员

类的静态成员是存储在静态区的，被所有类对象共享，模板类中的静态成员也不会被复制多份，而是被同类实例化的类对象共享，比如所有 int 和所有 double 的类对象，享有相互独立的静态变量。

### typename 和 class

模板中常用的两个关键词，在模板定义的时候没有什么区别。

```c++
class Myclass{
    public:
        Myclass();
        typedef int test;  //定义类型别名
}
template <class T>
class Myclass2{
    public:
        Myclass2();
        T::test *a  // 声明一个指向T::test类型的指针。
        //   typename T::test * a
}
```

C++ 中允许在类中定义类型别名，且使用时和类访问类成员的方法一样。编译器在编译时产生二义性，它根本不知道这是一个类型还是别名，就需要加上 `typename` 显式说明。

## 迭代器

本节主要介绍 5 种常见的迭代器：输入、输出迭代器，前向逆向迭代器，双向迭代器和随机迭代器。主要内容包括各自的构造方法和操作方法。

### 迭代器详述

迭代器 iterator 是一种对象，它能够用来遍历标准模板库容器中的部分或全部元素，每个迭代器对象代表容器中的确定的地址。迭代器修改了常规指针的接口，所谓迭代器是一种概念上的抽象：行为上像迭代器的东西都可以叫做迭代器。然而迭代器有很多不同的能力，它可以把抽象容器和通用算法有机地统一起来。

简单概括：迭代器是一种检查容器内元素并遍历元素的可带泛型数据类型。

#### 输入迭代器

通过对输入迭代器解除引用，它将引用对象，而对象可能位于集合中。通常用于传递地址。

```c++
template<class T, class Distance>
struct input_iterator {
    typedef input_iterator_tag iterator_category;//返回类型
    typedef T                  value_type;//所指对象类型
    typedef Distance           difference_type;//迭代器间距离类型
    typedef T*                 pointer;//操作结果类型
    typedef T&                 reference;//解引用操作结果类型
};
```

#### 输出迭代器

与输入迭代器相似，也只能单步向前迭代元素，不同的是该类迭代器对元素只有写的权限。通常用于返回地址。

```c++
struct output_iterator{
    typedef output_iterator_tag iterator_category;
    typedef void                value_type;
    typedef void                difference_type;
    typedef void                pointer;
    typedef void                reference;
};
```

#### 前向迭代器

前向迭代器可以在一个正确的区间中进行读写操作，它拥有输入迭代器的所有特性，和输出迭代器的部分特性，以及单步向前迭代元素的能力。通常用于遍历。

```c++
template <class T, class Distance> struct forward_iterator{
    typedef forward_iterator_tag    iterator_category;
    typedef T                        value_type;
    typedef Distance                difference_type;
    typedef T*                        pointer;
    typedef T&                        reference;
};
```

#### 双向迭代器

在前向迭代器的基础上提供了单步向后迭代的能力。

```c++
template <class T, class Distance> struct bidirectional_iterator{
    typedef bidirectional_iterator_tag    iterator_category;
    typedef T                        value_type;
    typedef Distance                difference_type;
    typedef T*                        pointer;
    typedef T&                        reference;
};
```

#### 随机迭代器

该类迭代器能完成上面所有迭代器的工作，它自己独有的特性就是可以像指针那样进行算术计算，而不是仅仅只有单步向前或向后迭代。

```c++
template <class T, class Distance> struct random_access_iterator{
    typedef random_access_iterator_tag    iterator_category;
    typedef T                        value_type;
    typedef Distance                difference_type;
    typedef T*                        pointer;
    typedef T&                        reference;
};
```

#### 迭代器辅助函数

- `advance`：用于迭代器前移，增加迭代的位置。可用于定向访问到迭代器的某个变量