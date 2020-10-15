# 模式识别与机器学习

> 2020 Fall UCAS
> 
> Pattern Recognition and Machine Learning

## 数学基础

### 随机向量

如果一个对象的特征观察值为 $\{x_1, x_2, ..., x_n\}$，它可构成一个 $n$ 维的特征向量值 $\mathbf{x}$，即：
$$
\mathbf{x} = (x_1, x_2, ..., x_n)^\mathbf{T}
$$
式中，$x_1, x_2, ...,x_n$ 为特征向量 $\mathbf{x}$ 的各个分量。

一个特征可以看作 $n$ 维空间中的向量或点，此空间成为模式的特征空间 $\mathbf{R_n}$。

### 数学期望和方差

随机变量 $X$ 的数学期望记作 $E(X)$。

随机变量 $(X-E(X))^2$ 的数学期望成为 $X$ 的方差，记作 $\sigma^2$，而 $\sigma$成为 $X$ 的均方差。

1. 若 $X$ 是连续型随机变量，其分布密度为 $p(x)$，则（当积分绝对收敛时）
   $$
   m = E(X) = \int_{-\infty}^\infty xp(x)\mathrm{d}x \\
   \sigma^2 = E\{(X-m)^2\} = \int_{-\infty}^\infty(x-m)^2p(x)\mathrm{d}x
   $$

2. 若 $X$ 是离散型随机变量，其可能取值为 $x_k, k = 1, 2, ...$，且 $P(X=x_k) = p_k$，则（当级数绝对收敛时）
   $$
   m = E(X) = \sum_{k=1}^\infty x_kp_k
   D(X) = \sum_{k=1}^\infty(x_k - m)^2p_k
   $$

### 协方差矩阵

协方差矩阵说明随机向量 $\mathbf{X}$ 的各分量的分散情况，定义为：
$$
\begin{align}
C &= E\{(\mathbf{X}-m)(\mathbf{X}-m)^T\} \\
&=E\left\{
% 矩阵
\left[\begin{array}{c}
\left(X_{1}-m_{1}\right) \\
\vdots \\
\left(X_{n}-m_{n}\right)
\end{array}\right]

\left[\left(X_{1}-m_{1}\right) \quad \cdots \quad\left(X_{n}-m_{n}\right)\right]\right\}\\


&=\left[\begin{array}{ccc}
E\left[\left(X_{1}-m_{1}\right)\left(X_{1}-m_{1}\right)\right] & \cdots & E\left[\left(X_{1}-m_{1}\right)\left(X_{n}-m_{n}\right)\right] \\
\vdots & & \vdots \\
E\left[\left(X_{n}-m_{n}\right)\left(X_{1}-m_{1}\right)\right] & \cdots & E\left[\left(X_{n}-m_{n}\right)\left(X_{n}-m_{n}\right)\right]
\end{array}\right]\\
&=\left(\begin{array}{ccc}
\lambda_{11} & \cdots & \lambda_{1 n} \\
\vdots & & \vdots \\
\lambda_{n 1} & \cdots & \lambda_{n n}
\end{array}\right)
\end{align}
$$
其中，协方差矩阵的各分量为：
$$
\lambda_{ij} = E[(X_i - m_i)(X_j - m_j)]
$$

### 正态分布

#### 一维正态密度函数

一维随机变量 $X$ 的正态密度函数表示为：
$$
p(x) = \frac{1}{\sqrt{2\pi}\sigma}\exp{\left[-\frac{(x-m)^2}{2\sigma^2}\right]}
$$
其中，$m$ 为均值，$\sigma^2$ 为方差，$\sigma$ 为标准差。



