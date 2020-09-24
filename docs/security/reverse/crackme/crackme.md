## 001.Acid burn (Nag, Name/Serial, Serial)

主要步骤就是去 nag 窗口、破解 Name/Serial、破解 Serial。

主要方法就是在 MessageBoxA 下断点，然后根据断点处栈的返回地址向上分析，找到调用 nag 窗口以及比较序列号的位置。

## 002.Afkayas.1

简单的序列号下断，对 MessageBox 系列函数下断点，根据调用栈回溯，找到序列号生成了比较代码。