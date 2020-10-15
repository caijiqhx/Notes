import numpy as np
import math
import matplotlib.pyplot as plt
x = []
y = []

w1 = [[0, 0], [2, 0], [2, 2], [0, 2]]
w2 = [[4, 4], [6, 4], [6, 6], [4, 6]]

a = np.linspace(0, 6)
print(a)

def func(x):
    y = 6 - x
    return y

for i in a:
    x.append(i)
    y.append(func(i))

print(x, y)
plt.plot(x, y)

for i in w1:
    plt.plot(i[0], i[1], 'go')
for i in w2:
    plt.plot(i[0], i[1], 'ro')

plt.show()