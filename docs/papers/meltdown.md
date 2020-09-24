# Meltdown 

> https://meltdownattack.com/meltdown.pdf

The security of computer systems fundamentally relies on memory isolation.

OS ensure that user programs cannot access each other's memory or kernel memory.

On modern processors, the isolation between the kernel and user processes is typically realized by a supervisor bit of the processor that defines whether a memory page of the kernel can be accessed or not.


Meltdown is a novel attack that allows overcoming memory isolation completely by providing a simple way for any user process to read the entire kernel memory of the machine it executes on.

The root cause of the simplicity and strength of Meltdown are side effects caused by out-of-order execution.


Out-of-order execution is an important performance feature of today's processors in order to overcome latencies of busy execution units.

A memory fetch unit needs to wait for data arrival from memory. Instead of stalling the execution, modern processors run operations out-of-order, they look ahead and schedule subsequent operations to idle execution unit of the core. 

 