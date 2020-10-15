import matplotlib.pyplot as plt
import numpy as np
import math

fig = plt.figure()
x = np.arange(-5, 5, 0.1)

ax = fig.add_subplot()

ax.spines['left'].set_position('center')
ax.spines['bottom'].set_position('center')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
# The lines to plot
y1 = 1 - x
y2 = x - 1

plt.ylim(-5, 5)

# Plotting of lines
# l1, = plt.plot([0]*len(x), x, label='$d_{12}(x) = -x_1 = 0$', color='b')
# l2, = plt.plot(x, y1, label='$d_{13}(x) = x_1 + x_2 - 1 = 0$', color='r')
# l3, = plt.plot(x, y2, label='$d_{23}(x) = x_1 - x_2 - 1 = 0$', color='g')

# Filling between lines
# (1)
# plt.fill_between(x, y1, y2, where=(x<=[0]*len(x)), color='green', alpha='0.5')
# y3 = np.maximum(y1, y2)
# plt.fill_between(x, y3, [10]*len(y3), where=(x>=[0]*len(x)), color='red', alpha='0.5')
# y4 = np.minimum(y1, y2)
# plt.fill_between(x, [-10]*len(y4), y4, where=(x>=[0]*len(x)), color='blue', alpha='0.5')

# (2)
# plt.fill_between(x, y1, [10]*len(y1), where=(x<[0]*len(x)), color='green', alpha='0.5')
# plt.fill_between(x, y1, y2, where=(x<[1]*len(x)), color='red', alpha='0.5')
# plt.fill_between(x, [-10]*len(y2), y2, where=(x>[0]*len(x)), color='blue', alpha='0.5')

# (3)
y12 = 1 - 2*x
y23 = [0]*len(x)
y31 = 2*x - 1

l12 = plt.plot(x, y12, label='$d_{12}(x) = d_1(x) - d_2(x) = -2x_1 - x_2 + 1 = 0$', color='b')
l23 = plt.plot(x, y23, label='$d_{23}(x) = d_2(x) - d_3(x) = 2x_2 = 0$', color='r')
l31 = plt.plot(x, y31, label='$d_{31}(x) = d_3(x) - d_1(x) = 2x_1 - x_2 - 1 = 0$', color='g')

plt.fill_between(x, y31, y12, where=(x<[0.5]*len(x)), color='green', alpha='0.5')
y4 = np.maximum(y12, [0]*len(y12))
plt.fill_between(x, y4, [10]*len(y4), color='red', alpha='0.5')
y5 = np.minimum([0]*len(y31), y31)
plt.fill_between(x, [-10]*len(y5), y5, color='blue', alpha='0.5')
# Labels of fills
# green_patch = mpatches.Patch(color='green', label='w1')
# red_patch = mpatches.Patch(color='red',label='w2')
# blue_patch = mpatches.Patch(color='blue',label='w3')

plt.text(-2, 0.5, '$\omega_1$')
plt.text(2, 2, '$\omega_2$')
plt.text(2, -2, '$\omega_3$')

# plt.legend()
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left', ncol=2, borderaxespad=0.)
plt.show()