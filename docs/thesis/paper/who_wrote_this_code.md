# 二进制程序作者识别

> [Who Wrote This Code? Identifying the Author of Program Binaries](http://pages.cs.wisc.edu/~jerryzhu/pub/Rosenblum11Authorship.pdf)

## 文章概要

文章较早地提出了使用机器学习方法自动检测二进制代码的特征，用于识别二进制程序作者以及探测未知作者程序之间的相似性。

### 引言

程序作者身份归属早已被用于剽窃检测和数字取证等领域。其核心思想是作者在创作过程中赋予作品以个人风格。虽然归因研究历来用于文学文献领域，但计算机程序同样是创造性过程的产物，其中必然包含作者的编程风格。以往的程序作者身份归属研究仅限于对源代码层面，依赖程序源代码的文本性质。然而在商业软件或恶意代码的分析中，通常无法得到源代码，而仅能获得二进制文件。源代码的文本特性在编译过程中都被剔除。将程序作者身份识别应用到二进制领域，以识别恶意代码作者或检测商业软件剽窃等需要新的方法识别作者的个人风格。

采用机器学习方法，先定义大量简单的候选特征，使用训练数据自动提取可反映程序员风格的特征。应用这一技术主要解决两个问题：从一组候选人中识别程序作者，通过二进制的文本相似性对程序进行分类，即分类和聚类问题。研究表明，二进制代码可以反映程序员风格，这为之后的研究奠定了基础。

作者身份归属技术基于以下假设：程序员风格在整个编译过程中得以保留。

定义大量的源于程序指令和控制流图的简单特性，让数据确定最能反映作者身份的特性。

使用支持向量机分类，使用 k-means 聚类算法。通过监督学习中获取的知识优化非监督学习。

### 二进制表示

- 使用 **Idioms** 特征模板捕获程序指令序列的细节。把真实指令序列抽象，去掉操作数和内存地址等细节。旨在捕获指令顺序反映的文本特征。
- 使用 **Graphlets** 特征模板表示程序结构的细节。是程序流程图的子图，反映程序局部结构。
- **Supergraphlets** 类似于在折叠控制流图上定义的指令摘要图。
- **Call Graphlets** 用于直接获取过程间控制流和程序与外部库的交互。
- **N-grams** 是三或四各字节的短串，捕获特定的指令操作码以及立即数和内存操作数。
- **Library call** 记录 **Call Graphlets** 中对外部库的调用。

定义以上特征模板是为了筛选出能够反映作者归属的特征，而不是使用全部的特征进行分类。

### 分类

分类问题中，假设存在一组已知的程序员，并以每个程序员写的程序作为训练样本。给定一组程序作者和一组带作者标签的训练程序，分类器的任务就是对输入的新程序，指出对可能的作者身份。

为了评估特征对作者身份识别的影响，将训练集分类，一部分用于训练分类器，另一部分用于评估其精度。通过这样的交叉验证以选择更优的特征子集。

使用线性支持向量机，从二元分类扩展到 k 元。

### 聚类

聚类是无监督学习，通过程序相似性分组。作者身份归属的聚类对应不存在假定作者的情况下寻找风格相似的程序的任务。聚类没有训练集，因此可能得到对预期之外的不同属性的聚类。

为了让聚类结果更好的反映作者身份，可以转换特征空间，使风格相似的程序彼此接近。

定义一个距离度量 $A$ 使得编程风格相似的程序在该度量下的接近。$A$ 可以通过监督学习得到。

### 评估

从以下几个方面评估：

- 从二进制程序中恢复作者风格的程度。
- 不精确分类的权衡。
- 是否可以通过一组程序中训练得出的度量优化另一组程序的聚类结果。

测试表明：

- 程序风格经过编译过程后保留。
- 作者身份分类器具有良好的准确性。
- 监督学习中获取的作者身份归属相关知识可以转移到作者聚类，提升聚类准确率。

分类问题中，简单的特征模板如 **Idioms** 和 **N-grams** 对作者身份识别影响更大。


