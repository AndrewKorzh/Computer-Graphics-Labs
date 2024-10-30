import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from matplotlib.patches import Circle
from scipy.interpolate import make_interp_spline
import numpy as np

class BezierEditor:
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.points = []
        self.circles = []
        self.curve = None
        self.selected_circle = None

        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def add_point(self, x, y):
        point = np.array([x, y])
        self.points.append(point)

        circle = Circle((x, y), 0.2, color='red', picker=True)
        self.circles.append(circle)
        self.ax.add_patch(circle)

        self.update_curve()

    def remove_point(self, circle):
        index = self.circles.index(circle)
        self.points.pop(index)
        circle.remove()
        self.circles.pop(index)
        self.update_curve()

    def update_curve(self):
        if self.curve:
            self.curve.remove()
        if len(self.points) >= 4:
            x_vals, y_vals = zip(*self.points)
            t = np.linspace(0, 1, 100)
            spline_x = make_interp_spline(range(len(x_vals)), x_vals, k=3)
            spline_y = make_interp_spline(range(len(y_vals)), y_vals, k=3)
            curve_points_x = spline_x(t * (len(x_vals) - 1))
            curve_points_y = spline_y(t * (len(y_vals) - 1))
            self.curve, = self.ax.plot(curve_points_x, curve_points_y, 'blue')

        self.fig.canvas.draw()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        if event.button == MouseButton.LEFT:
            for circle in self.circles:
                contains, _ = circle.contains(event)
                if contains:
                    self.selected_circle = circle
                    return
            self.add_point(event.xdata, event.ydata)
        elif event.button == MouseButton.RIGHT:
            for circle in self.circles:
                contains, _ = circle.contains(event)
                if contains:
                    self.remove_point(circle)
                    return

    def on_release(self, event):
        self.selected_circle = None

    def on_motion(self, event):
        if not self.selected_circle or event.inaxes != self.ax:
            return
        index = self.circles.index(self.selected_circle)
        self.points[index] = np.array([event.xdata, event.ydata])
        self.selected_circle.center = (event.xdata, event.ydata)
        self.update_curve()

    def show(self):
        plt.show()

if __name__ == "__main__":
    editor = BezierEditor()
    editor.show()
