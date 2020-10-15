import numpy as np
import math

w1 = np.array([
    [0, 1, 1, 1],
    [0, 0, 0, 1],
    [0, 0, 1, 0],
], dtype=np.float)

w2 = np.array([
    [0, 0, 0, 1],
    [0, 1, 1, 1],
    [1, 1, 0, 1],
], dtype=np.float)

# 初始化 预处理
C = 1
m, n = w1.shape
w = np.zeros(m + 1)
print("Initial: ", w)
add_row = np.ones(w1.shape[1])
w1 = np.row_stack((w1, add_row))
w2 = np.row_stack((w2, add_row))
w2 = -1 * w2

w1 = np.matrix(w1)
w2 = np.matrix(w2)
w = np.matrix(w)

cnt = 0
while True:
    changed = False
    # w1  if w·x
    for i in range(0, n):
        cur_col = w1[:, i]
        if (w * cur_col)[0, 0] <= 0:
            changed = True
            w += (C * cur_col).T
            print('\t', w)
    
    for i in range(0, n):
        cur_col = w2[:, i]
        if (w * cur_col)[0, 0] <= 0:
            changed = True
            w += (C * cur_col).T
            print('\t', w)
    cnt += 1
    if not changed:
        break

print(cnt, "times ", w)