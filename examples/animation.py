import functools
import sys

from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import mpl_toolkits.clifford
from clifford.g2c import *

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.axis('equal')

def basic_animation(fig, *, interval, **kwargs):
    def decorator(f):
        last_artists = []
        def animate(i):
            for a in last_artists:
                a.remove()
            last_artists[:] = list(f(i*interval))
            return last_artists

        return animation.FuncAnimation(
            fig, animate, init_func=lambda: animate(0), **kwargs, interval=interval*1000)

    return decorator

@basic_animation(fig, interval=0.005, save_count=100)
def animation(t):
    freq = 0.5
    A = up(np.cos(t*2*np.pi*freq)*e1+  np.sin(t*2*np.pi*freq)*e2)
    B = up(e1)
    C = up(e2)
    yield from mpl_toolkits.clifford.plot(ax, [(A ^ C).dual()], marker='x', color='tab:orange')
    yield from mpl_toolkits.clifford.plot(ax, [A ^ B ^ C], color='tab:blue')
    yield from mpl_toolkits.clifford.plot(ax, [A, B, C], marker='x', color='tab:red', linestyle='none')
    yield from mpl_toolkits.clifford.plot(ax, [A ^ B ^ einf], color='tab:green')
    yield from mpl_toolkits.clifford.plot(ax, [(A ^ B ^ C) | B], color='tab:purple')

animation.save('test2.gif', writer='imagemagick')

plt.show()
