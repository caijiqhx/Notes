# 网络协议安全

> 2020 Fall UCAS 
> 
> Network Protocol Security
> 
> liyang@iie.ac.cn
> 
> 从攻击和防御两个角度自底向上详细分析了现有的各层网络协议
> 
> 讲的相当不错

## 网络协议安全基础

- TCP/IP 协议栈、OSI 参考模型、**LTE 用户面协议栈**
- TCP/IP 协议族安全性
  - 分组交换，易受攻击
  - 没有认证机制，路由器不具备数据追踪功能
  - 尽力而为
  - 匿名与隐私，终端名与地址分离
  - 网络基础设施不可靠
- 网络漏洞分类
  - 基于头部：协议头部与标准冲突，TCP 的  FLAG 误用攻击
  - 基于协议：乱序发包、DoS、SYM 雪崩
  - 基于验证：欺骗，MAC、IP 地址、DNS
  - 基于流量：雪崩、嗅探

| Layers     | Attacks                             |
| ---------- | ----------------------------------- |
| 应用层     | DNS 污染、HTTPS、Web 漏洞、病毒木马 |
| 传输层     | TCP 欺骗、DoS、端口扫描             |
| 网络层     | IP 欺骗、ICMP、路由欺骗             |
| 数据链路层 | MAC 欺骗、MAC 泛洪、ARP 欺骗        |
| 物理层     | 设备破坏、线路侦听                  |

- 网络攻击过程
  - 扫描，主机、端口、操作系统、漏洞
  - 监听，流量劫持、数据解析
  - DoS，检测、防范、流量清洗

## 链路层协议安全

- 以太网 802.3
  - DL 分为 LLC 和 MAC 两个子层
  - 局域网介质共享，要解决介质冲突问题
  - CSMA/CD，先听后发、边发边听、冲突停发、随机延迟后重发
  - 集线器 L1
  - 交换机 L2 隔离冲突域、扩容
  - Content Addressable Memory MAC-端口 地址表，转发、学习、广播、更新
- 802.3 安全威胁
  - MAC 泛洪，发送带有伪造 MAC 地址源的数据，CAM 耗尽后会广播
  - 防御，利用交换机的端口安全性功能，限制端口上所允许的有效 MAC 地址数量，为端口分配安全 MAC 地址
  - MAC 欺骗，端口占用，伪造以太网帧，源 MAC 为受害者 MAC
  - ARP 缓存 IP 与 MAC 地址的映射，ARP 报文可以直接封装成帧，不用放入 IP 报文，没有对应 MAC 就广播请求
  - ARP 欺骗，不需要请求报文直接发送 reply 报文即可实现欺骗，伪造受害者 IP [**代码实现**](https://www.freebuf.com/articles/network/210852.html)
  - 检测，网速慢、查看正确的网关 MAC 地址、局域网存在大量 ARP reply 包
  - 防御，MAC 地址绑定、静态 ARP 缓存、使用 ARP 服务器
- 无线 WLAN 802.11
  - SSID Service Set ID、STA Station、AP Access Point
  - BSS、ESS、DS
  - Ad Hoc 无线自组织网络，无需 AP
- 802.11 安全威胁
  - 恶意访问接入点，伪造的 AP 放大信号、相同的 SSID
  - 内部人员搭建无线 AP，外人进入内网
- 802.11 安全机制
  - 