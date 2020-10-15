import numpy as np
import math

w1 = np.array([
    [-1],
    [-1],
], dtype=float)

w2 = np.array([
    [0],
    [0],
], dtype=float)

w3 = np.array([
    [1],
    [1],
], dtype=float)

# 初始化 预处理
C = 1
m, n = w1.shape
w = np.zeros((m + 1, 3))
print("Initial:\n", w)

add_row = np.ones(n)
w1 = np.row_stack((w1, add_row))
w2 = np.row_stack((w2, add_row))
w3 = np.row_stack((w3, add_row))
# w2 = -1 * w2

w1 = np.matrix(w1)
w2 = np.matrix(w2)
w3 = np.matrix(w3)
w = np.matrix(w)

def interate(idx, wn):
    changed = False
    d = w[idx] * wn
    for i in range(0, w.shape[0]):
        cur_w = w[i]
        if d <= cur_w * wn and i != idx:
            changed = True
            w[i] -= C * wn.T
    if changed:
        w[idx] += C * wn.T
    return changed

cnt = 0
while True:
    changed = False
    changed |= interate(0, w1) 
    changed |= interate(1, w2) 
    changed |= interate(2, w3)

    cnt += 1
    if not changed:
        break

print(cnt, "times\n ", w)