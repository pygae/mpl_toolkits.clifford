import math
from typing import Iterator
import itertools
import collections
import functools
import warnings

from matplotlib.artist import Artist
from matplotlib.patches import Circle, FancyArrowPatch, Patch
from matplotlib.collections import PatchCollection
from matplotlib.tri import Triangulation
from matplotlib.path import Path
from matplotlib.lines import Line2D

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d, art3d

import numpy as np

from clifford.tools import classify
import clifford

from ._version import __version__

__all__ = ['plot']


def _line_style_for_radius(r):
    return '-' if r.imag == 0 else ":"


def plot(ax, cga_objs, **kwargs):
    """
    Plot a multivector or list of multivectors
    """
    if isinstance(cga_objs, clifford.MultiVector):
        cga_objs = [cga_objs]
    if not cga_objs:
        return []

    layout = cga_objs[0].layout
    if not all(cga_obj.layout is layout for cga_obj in cga_objs[1:]):
        raise ValueError("All multivectors must have the same layout")

    if not isinstance(layout, clifford.ConformalLayout):
        raise TypeError("Layout must be conformal")

    if isinstance(ax, Axes3D):
        axis_dims = 3
    else:
        axis_dims = 2
    obj_dims = layout.dims - 2  # for ei, eo
    if obj_dims == axis_dims == 2:
        return list(_Plotter2d(ax, layout).plot(cga_objs, **kwargs))
    elif obj_dims == axis_dims == 3:
        return list(_Plotter3d(ax, layout).plot(cga_objs, **kwargs))
    elif obj_dims == axis_dims:
        raise NotImplementedError("Cannot plot {}-D objects".format(obj_dims))
    elif obj_dims != axis_dims:
        raise TypeError("Objects live in {}-D space, but the axes are {}-D".format(obj_dims, axis_dims))


def _groupby(l, key=lambda x: x):
    d = collections.defaultdict(list)
    for item in l:
        d[key(item)].append(item)
    return d.items()


def _ray_box_intersection(origin, direction, mins, maxs):
    n = len(origin)
    valid_points = []
    # ok to ignore these, the `NaN`s end up not meeting the comparison conditions
    with np.errstate(invalid='ignore', divide='ignore'):
        for src in mins, maxs:
            lams = (src - origin) / direction
            for i, lam in enumerate(lams):
                i_other = (i + np.arange(1, n)) % n
                p = origin + lam*direction
                if (mins[i_other,] <= p[i_other,]).all() and (p[i_other,] <= maxs[i_other,]).all():
                    valid_points.append((lam, p))
    valid_points.sort(key=lambda t: t[0])
    if valid_points:
        return np.array([valid_points[0][1], valid_points[-1][1]])
    else:
        return np.empty((0, n))


class _InfiniteLine:
    def __init__(self, origin, direction):
        self._origin = np.asarray(origin)
        self._direction = np.asarray(direction)


class InfiniteLine2D(Line2D, _InfiniteLine):
    def __init__(self, origin, direction, *args, **kwargs):
        Line2D.__init__(self, [], [], *args, **kwargs)
        _InfiniteLine.__init__(self, origin, direction)

    def draw(self, renderer):
        mins, maxs = np.array([
            self.axes.get_xbound(),
            self.axes.get_ybound(),
        ]).T

        points = _ray_box_intersection(self._origin, self._direction, mins, maxs)
        self.set_data(*points.T)
        super().draw(renderer)


class InfiniteLine3D(art3d.Line3D, _InfiniteLine):
    def __init__(self, origin, direction, *args, **kwargs):
        art3d.Line3D.__init__(self, [], [], [], *args, **kwargs)
        _InfiniteLine.__init__(self, origin, direction)

    def draw(self, renderer):
        mins, maxs = np.array([
            self.axes.get_xbound(),
            self.axes.get_ybound(),
            self.axes.get_zbound(),
        ]).T
        points = _ray_box_intersection(self._origin, self._direction, mins, maxs)
        self._verts3d = points.T
        super().draw(renderer)


class _Plotter:
    def __init__(self, ax, layout):
        self._layout = layout
        self._ax = ax

    def plot(self, cga_objs, **kwargs) -> Iterator[Artist]:
        all_os = [classify.classify(cga_obj) for cga_obj in cga_objs]
        for handler, os in _groupby(all_os, lambda o: functools._find_impl(type(o), self._handlers)):
            if not handler:
                unsupported_msg = (\
                    "Unable to plot any of the following objects:\n{}"
                    .format("\n".join(" * {!r}".format(o) for o in os))
                )
                warnings.warn(unsupported_msg)
            else:
                yield from handler(self, os, **kwargs)


class _Plotter2d(_Plotter):
    _handlers = {}

    def _handles(t, _handlers=_handlers):
        def decorator(f):
            _handlers[t] = f
            return f
        return decorator

    @classmethod
    def _as_point_tuple_2d(cls, p):
        return p[(1,)], p[(2,)]

    @_handles(classify.Point)
    def _plot_Point(self, os, **kwargs) -> Iterator[Artist]:
        x, y = zip(*[self._as_point_tuple_2d(point.location) for point in os])
        yield from self._ax.plot(x, y, **kwargs)

    @_handles(classify.Tangent[2])
    def _plot_Tangent(self, os, **kwargs) -> Iterator[Artist]:
        for tangent in os:
            p = FancyArrowPatch(
                self._as_point_tuple_2d(tangent.location),
                self._as_point_tuple_2d(tangent.location + tangent.direction.normal()),
                arrowstyle="->", shrinkA=0, shrinkB=0, mutation_scale=10
            )
            self._ax.add_patch(p)
            yield p

    @_handles(classify.PointPair)
    def _plot_PointPair(self, os, **kwargs) -> Iterator[Artist]:
        for o in os:
            d = o.direction.normal()
            a = o.location - abs(o.radius) * d
            b = o.location + abs(o.radius) * d
            x, y = zip(*[self._as_point_tuple_2d(end) for end in (a, b)])
            yield from self._ax.plot(x, y, linestyle=_line_style_for_radius(o.radius), **kwargs)

    @_handles(classify.Line)
    def _plot_Line(self, os, **kwargs) -> Iterator[Artist]:
        for line in os:
            l = InfiniteLine2D(
                self._as_point_tuple_2d(line.location),
                self._as_point_tuple_2d(line.direction),
                **kwargs
            )
            self._ax.add_line(l)
            yield l

    @_handles(classify.Circle)
    def _plot_Circle(self, os, **kwargs) -> Iterator[Artist]:
        # adjust the color arguments to make sense
        kwargs.setdefault('facecolors', 'none')
        try:
            color = kwargs.pop('color')
        except KeyError:
            raise
        else:
            kwargs['edgecolors'] = color
        c = [
            Circle(self._as_point_tuple_2d(circle.location), abs(circle.radius))
            for circle in os
        ]
        linestyles = [_line_style_for_radius(circle.radius) for circle in os]
        col = PatchCollection(c, linestyles=linestyles, **kwargs)
        self._ax.add_collection(col)
        self._ax.autoscale_view(None)
        yield col



class Arrow3D(FancyArrowPatch):
    def __init__(self, posA, posB, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._posA_3d = posA
        self._posB_3d = posB

    def do_3d_projection(self, renderer):
        xs3d, ys3d, zs3d = zip(self._posA_3d, self._posB_3d)
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        return min(zs)


class Circle3D(Patch):
    def __init__(self, center, radius, matrix, **kwargs):
        Patch.__init__(self, **kwargs)
        path = Path.unit_circle()
        self.radius = radius
        self._code3d = path.codes
        self._segment3d = center + radius * (path.vertices @ matrix.T)
        self._path2d = Path(np.zeros((0, 2)))

    def get_path(self):
        return self._path2d

    def do_3d_projection(self, renderer):
        s = self._segment3d
        xs, ys, zs = zip(*s)
        vxs, vys, vzs, vis = proj3d.proj_transform_clip(xs, ys, zs, renderer.M)
        self._path2d = Path(np.column_stack([vxs, vys]), self._code3d)
        return min(vzs)

    # def draw(self, renderer):
    #     self.do_3d_projection()
    #     super().draw(self, renderer)




class _Plotter3d(_Plotter):
    _handlers = {}

    def _handles(t, _handlers=_handlers):
        def decorator(f):
            _handlers[t] = f
            return f
        return decorator

    @classmethod
    def _as_point_tuple_3d(cls, p):
        return p[(1,)], p[(2,)], p[(3,)]

    @_handles(classify.Point)
    def _plot_Point(self, os, **kwargs) -> Iterator[Artist]:
        coords = zip(*[self._as_point_tuple_3d(point.location) for point in os])
        return self._ax.plot(*coords, **kwargs)

    @_handles(classify.Tangent[2])
    def _plot_Tangent(self, os, **kwargs) -> Iterator[Artist]:
        for tangent in os:
            p = Arrow3D(
                self._as_point_tuple_3d(tangent.location),
                self._as_point_tuple_3d(tangent.location + tangent.direction.normal()),
                arrowstyle="->", shrinkA=0, shrinkB=0, mutation_scale=10
            )
            self._ax.add_patch(p)
            yield p

    @_handles(classify.PointPair)
    def _plot_PointPair(self, os, **kwargs) -> Iterator[Artist]:
        for o in os:
            d = o.direction.normal()
            a = o.location - abs(o.radius) * d
            b = o.location + abs(o.radius) * d
            coords = zip(*[self._as_point_tuple_3d(end) for end in (a, b)])
            yield from self._ax.plot(*coords, linestyle=_line_style_for_radius(o.radius), **kwargs)

    @_handles(classify.Line)
    def _plot_Line(self, os, **kwargs) -> Iterator[Artist]:
        for o in os:
            l = InfiniteLine3D(
                origin=self._as_point_tuple_3d(o.location),
                direction=self._as_point_tuple_3d(o.direction), **kwargs)
            self._ax.add_line(l)
            yield l

    @_handles(classify.Circle)
    def _plot_Circle(self, os, **kwargs) -> Iterator[Artist]:
        # adjust the color arguments to make sense
        kwargs.setdefault('facecolor', 'none')
        try:
            color = kwargs.pop('color')
        except KeyError:
            raise
        else:
            kwargs['edgecolor'] = color

        e1, e2, e3 = self._layout.blades['e1'], self._layout.blades['e2'], self._layout.blades['e3']
        ret = []
        for circle in os:
            rotor = (circle.direction.normal() * (e1 ^ e2) + 1).normal()
            mat = clifford.linear_operator_as_matrix(lambda x: rotor * x * ~rotor, [e1, e2], [e1, e2, e3])
            p = Circle3D(
                self._as_point_tuple_3d(circle.location),
                abs(circle.radius), mat,
                linestyle=_line_style_for_radius(circle.radius),
                **kwargs
            )
            self._ax.add_patch(p)
            yield p

    @_handles(classify.Plane)
    def _plot_Plane(self, os, **kwargs) -> Iterator[Artist]:
        kwargs.setdefault('alpha', 0.5)
        for plane in os:
            loc = plane.location
            dir = plane.direction
            (a, b), sc = dir.factorise()

            # todo: make this extend to the bounds of the plot area
            points = np.sqrt(sc)*np.array([
                [self._as_point_tuple_3d(loc - a), self._as_point_tuple_3d(loc - b)],
                [self._as_point_tuple_3d(loc + b), self._as_point_tuple_3d(loc + a)]
            ])
            yield self._ax.plot_surface(*points.T, **kwargs)

    @_handles(classify.Sphere)
    def _plot_Sphere(self, os, **kwargs) -> Iterator[Artist]:
        from trimesh.creation import icosphere
        kwargs.setdefault('alpha', 0.5)
        ret = []
        for o in os:
            tmesh = icosphere(radius=abs(o.radius))
            loc = self._as_point_tuple_3d(o.location)
            t = Triangulation(loc[0] + tmesh.vertices[:, 0], loc[1] + tmesh.vertices[:, 1], triangles=tmesh.faces)
            yield self._ax.plot_trisurf(t, loc[2] + tmesh.vertices[:, 2], **kwargs)
