from matplotlib import pyplot as plt
import mpl_toolkits.clifford
from clifford.g2c import *
import sys

fig = plt.figure()
ax = fig.add_subplot(1, 2, 1)
A = up(e1+e2)
B = up(e1)
C = up(e2)
ax.axis('equal')
mpl_toolkits.clifford.plot(ax, [(A ^ C).dual()], marker='x', color='tab:orange')
mpl_toolkits.clifford.plot(ax, [A ^ B ^ C], color='tab:blue')
mpl_toolkits.clifford.plot(ax, [A, B, C], marker='x', color='tab:red', linestyle='none')
mpl_toolkits.clifford.plot(ax, [A ^ B ^ einf], color='tab:green')
mpl_toolkits.clifford.plot(ax, [(A ^ B ^ C) | B], color='tab:purple')

from clifford.g3c import *
ax3 = fig.add_subplot(1, 2, 2, projection='3d')
A = up(-e1)
B = up(e1)
C = up(e2*0.6 + e3*0.8)
D = up(e3)
mpl_toolkits.clifford.plot(ax3, [(A ^ B ^ C).dual()], marker='x', color='tab:orange')
mpl_toolkits.clifford.plot(ax3, [A ^ B ^ C], color='tab:blue')
mpl_toolkits.clifford.plot(ax3, [A ^ B ^ C ^ D], color='tab:blue')
mpl_toolkits.clifford.plot(ax3, [A, B, C], marker='x', color='tab:red', linestyle='none')
mpl_toolkits.clifford.plot(ax3, [A ^ B ^ einf], color='tab:green')
mpl_toolkits.clifford.plot(ax3, [(A ^ B ^ C) | B], color='tab:purple')

plt.show()
