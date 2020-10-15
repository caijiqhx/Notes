import numpy as np
import math
import matplotlib.pyplot as plt

w1 = np.array([
    [0, 1, 1, 1],
    [0, 0, 0, 1],
    [0, 1, 0, 0],
], dtype=np.float)

w2 = np.array([
    [0, 0, 0, 1],
    [0, 1, 1, 1],
    [1, 1, 0, 1],
], dtype=np.float)

p1 = p2 = 1/2

w1 = np.matrix(w1)
w2 = np.matrix(w2)

m1 = np.mean(w1, axis=1)
m2 = np.mean(w2, axis=1)

c1 = np.matrix(np.cov(w1, bias=True))
c2 = np.matrix(np.cov(w2, bias=True))

print('C1 == C2' if (c1 == c2).all() else 'C1 != C2')

X = ['x1', 'x2', 'x3']

result = 'd1 - d2 = '
C = (np.log(p1) - np.log(p2) - 1/2 * m1.T * c1.I * m1 + 1/2 * m2.T * c1.I * m2)[0, 0]
coes = ((m1 - m2).T * c1.I)[0].tolist()[0]
for idx, coe in enumerate(coes):
    result += ('- ' if coe < 0 else ('+ ' if idx > 0 else ' ')) + str(np.abs(coe)) + X[idx] + ' '
result += ('+ ' if C > 0 else ' ') + str(C) + ' = 0'
print(result)
