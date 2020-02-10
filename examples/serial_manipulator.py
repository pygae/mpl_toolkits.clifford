# from https://enkimute.github.io/ganja.js/examples/coffeeshop.html#AFVs70eea

import math

from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import mpl_toolkits.clifford

from clifford.g3c import *


fig = plt.figure(figsize=(4, 4))
ax = fig.add_subplot(1, 1, 1, projection="3d")
ax.set(xlim=[-1, 1], ylim=[0, 2], zlim=[-1, 1], autoscale_on=False)
ax.view_init(azim=120)

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


# Draw a robot base
C = up(0.2*e1)^up(0.2*e3)^up(-0.2*e1);

trajectory = []

@basic_animation(fig, interval=0.005, save_count=100)
def animation(t):
    # Set up time varying parameters for the the rotors
    speed = 4
    theta0 = math.cos(speed*t/3)*math.pi/2
    theta1 = math.cos(speed*t/1)*math.pi/4
    theta2 = math.cos(speed*t/0.5)*math.pi/2

    # Create a time varying rotor to mimic the behaviour of the base
    R0 = (-theta0*e13/2).exp()
    R1 = (-theta1*e12/2).exp()
    Rbase = (R0*R1).normal()

    #  Define the points of the robot
    elb0 = Rbase*e2*(~Rbase)

    # This is the motor in the elbow
    R2 = Rbase*(-theta2*e12/2).exp()

    # The end point
    endpoint = elb0 + R2*0.5*e2*~R2
    trajectory.append(up(endpoint))

    yield from mpl_toolkits.clifford.plot(ax, [up(0), R0*up(0.2*e1)*~R0], color='tab:blue')
    yield from mpl_toolkits.clifford.plot(ax, [C], color='tab:blue')
    yield from mpl_toolkits.clifford.plot(ax, [up(0), up(elb0), up(endpoint)], marker='x', color='tab:orange')
    yield from mpl_toolkits.clifford.plot(ax, trajectory, color='tab:gray', linewidth=0.5)

# animation.save('test2.gif', writer='imagemagick')

plt.show()
