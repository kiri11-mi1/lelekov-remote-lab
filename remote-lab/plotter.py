import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np


class Plotter:
    """Отображение рисунков"""
    def __init__(self, figNum=None, maxPoints=300, figSize=(6,6)):
        if figNum is None:
            self.figure, axes = plt.subplots(3, 1, figsize=figSize)
            self.figNum = plt.gcf().number
        else:
            self.figure = plt.figure(num=figNum, clear=True)
            axes = self.figure.subplots(3, 1)
            self.figNum = figNum
        #self.figure.tight_layout()

        # init data, add empty lines with colors
        self.lines = {}
        self.axes = {}
        self.data = {'t':[0., 0.]} # добавляем два пустых отсчёта (c NaN), для замеров dt
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        self.keys = ['t', 'theta', 'omega', 'u']
        dimension = ['s', 'deg', 'deg/s', '-1..1']
        for (key, ax, c, dim) in zip(self.keys[1:], axes, colors, dimension[1:]):
            self.axes[key] = ax
            ax.grid(b=True) # сетку на всех осях
            self.data[key] = [np.nan, np.nan]
            self.lines[key], = self.axes[key].plot(
                self.data['t'],
                self.data[key],
                color=c
            ) # и пустую линию
            self.axes[key].set_ylabel(key+' ['+dim+']') # обозначения на осях
        self.axes['theta'].set_title('dt = %5.2f ms'%(0.,))
        self.maxPoints = maxPoints

        self.stopNow = False
        self.axButton = plt.axes([0.7, 0.895, 0.2, 0.05])
        self.button = Button(self.axButton, 'Stop') # Создание кнопки
        self.button.on_clicked(self.onButtonClicked)

    def on_button_clicked(self, event):
        """ обработчик клика """
        self.stopNow = True

    def add_data(self, t, ThetaOmegaU):
        ttwu = [t]
        ttwu.extend(ThetaOmegaU)
        for (key, d) in zip(self.keys, ttwu):
            self.data[key].append(d)
            if len(self.data[key])>self.maxPoints: # cut len to maxPoints
                self.data[key] = self.data[key][1:]

        for key in self.keys[1:]: # updating data values
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

        self.axes['theta'].set_title('dt = %5.2f ms'%(1000*np.mean(np.diff(self.data['t'])),)) #(self.data['t'][-1]-self.data['t'][-2])
        self.figure.canvas.draw() # drawing updated values
        self.figure.canvas.flush_events()

    def get_data(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        plt.close(self.figNum)
