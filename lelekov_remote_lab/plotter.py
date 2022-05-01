import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np


class Plotter:
    """Отображение рисунков"""
    def __init__(self, fig_num=None, max_points=300, fig_size=(6,6)):
        if fig_num is None:
            self.figure, axes = plt.subplots(3, 1, figsize=fig_size)
            self.fig_num = plt.gcf().number
        else:
            self.figure = plt.figure(num=fig_num, clear=True)
            axes = self.figure.subplots(3, 1)
            self.fig_num = fig_num

        # init data, add empty lines with colors
        self.lines = {}
        self.axes = {}

        # добавляем два пустых отсчёта (c NaN), для замеров dt
        self.data = {'t': [0., 0.]}
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        self.keys = ['t', 'theta', 'omega', 'u']
        dimension = ['s', 'deg', 'deg/s', '-1..1']
        for (key, ax, c, dim) in zip(self.keys[1:], axes, colors, dimension[1:]):
            self.axes[key] = ax
            ax.grid(b=True)
            self.data[key] = [np.nan, np.nan]
            self.lines[key], = self.axes[key].plot(
                self.data['t'],
                self.data[key],
                color=c
            )
            # обозначения на осях
            self.axes[key].set_ylabel(key+' ['+dim+']')
        self.axes['theta'].set_title('dt = %5.2f ms'%(0.,))
        self.max_points = max_points

        self.stop_now = False
        self.ax_button = plt.axes([0.7, 0.895, 0.2, 0.05])
        self.button = Button(self.ax_button, 'Stop')
        self.button.on_clicked(self.on_button_clicked)

    def on_button_clicked(self, event):
        """ обработчик клика """
        self.stop_now = True

    def add_data(self, t, theta_omega_u):
        ttwu = [t]
        ttwu.extend(theta_omega_u)
        for (key, d) in zip(self.keys, ttwu):
            self.data[key].append(d)
            if len(self.data[key]) > self.max_points:
                self.data[key] = self.data[key][1:]

        for key in self.keys[1:]:
            self.lines[key].set_xdata(self.data['t'])
            self.lines[key].set_ydata(self.data[key])
            self.axes[key].set_xlim(right=self.data['t'][-1],
                                    left=self.data['t'][0])
            top = np.nanmax(self.data[key])
            if np.isnan(top):
                top = 1
            bottom = np.nanmin(self.data[key])
            if np.isnan(bottom):
                bottom = 0
            self.axes[key].set_ylim(top=top, bottom=bottom)

        self.axes['theta'].set_title('dt = %5.2f ms' % (1000*np.mean(np.diff(self.data['t'])),)) #(self.data['t'][-1]-self.data['t'][-2])
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def get_data(self):
        return self.data

    def __enter__(self):
        plt.ion()
        plt.show()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        plt.close(self.fig_num)
