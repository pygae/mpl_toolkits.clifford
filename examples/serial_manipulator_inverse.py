# from https://enkimute.github.io/ganja.js/examples/coffeeshop.html#pQ--C9FL_

import math
from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import mpl_toolkits.clifford

from clifford.g3c import *


fig = plt.figure(figsize=(4, 4))
ax = fig.add_subplot(1, 1, 1, projection="3d")
ax.set(xlim=[-1, 1], ylim=[0, 2], zlim=[-1, 1], autoscale_on=False)
ax.view_init(azim=150)

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


target_traj = [
    0.8*e2 + 0.5*e3,
    0.6*e2 + 0.5*e1,
    0.4*e2 - 0.5*e3,
    0.6*e2 - 0.5*e1,
]


@basic_animation(fig, interval=0.005, save_count=100)
def animation(t):
    speed = 16

    # Set the lengths of the arm pieces
    rho = 0.8
    l = 0.6

    # Choose a target
    cycles, traj_frac = divmod(t * speed, len(target_traj))
    ind, frac = divmod(traj_frac, 1)
    ind = int(ind)
    next_ind = (ind + 1) % len(target_traj)

    target = up(target_traj[ind]*(1-frac) + target_traj[next_ind]*frac)

    # Draw a robot base
    Cbase = up(0.2*e1)^up(0.2*e3)^up(-0.2*e1)

    # The actual inverse kinematics of the robot
    S0 = (up(0) - 0.5*rho**2*einf).dual()
    S1 = (target - 0.5*l**2*einf).dual()
    C = S0&S1
    P = target^up(0)^up(e2)^einf
    PP = -P&C

    # The square of the point pair describes if the spheres intersect
    if (PP*PP)[0] > 0:
        # If the spheres intersect then we can just choose one solution
        proj = (1 + PP*(1/math.sqrt((PP*PP)[0])))
        elb = proj*(PP|einf)
        endpoint = target
    else:
        # If the spheres do not intersect then we will just reach for the object.
        endpoint = up((rho+l)*down(target).normal())
        elb = up(rho*down(target).normal())

    yield from mpl_toolkits.clifford.plot(ax, [S0, S1, P], color='k', alpha=0.1)
    yield from mpl_toolkits.clifford.plot(ax, [Cbase], color='tab:blue')
    yield from mpl_toolkits.clifford.plot(ax, [up(0), elb, endpoint], marker='x', color='tab:orange')
    yield from mpl_toolkits.clifford.plot(ax, [C], color='tab:red')
    yield from mpl_toolkits.clifford.plot(ax, [target], color='tab:red')
    yield from mpl_toolkits.clifford.plot(ax, [PP], color='tab:red')
    yield from mpl_toolkits.clifford.plot(ax, [up(t) for t in (target_traj + target_traj[:1])], color='tab:gray', linewidth=0.5)

# animation.save(Path(__file__).with_suffix('.gif'), writer='imagemagick')

plt.show()
