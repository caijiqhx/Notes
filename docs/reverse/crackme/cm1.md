# 001.Acid burn (Nag, Name/Serial, Serial)

主要步骤就是去 nag 窗口、破解 Name/Serial、破解 Serial。

主要方法就是在 MessageBoxA 下断点，然后根据断点处栈的返回地址向上分析，找到调用 nag 窗口以及比较序列号的位置。