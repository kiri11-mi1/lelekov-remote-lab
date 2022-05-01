"""
Клиент UDP для обмена данными с имитатором КА
@author: ttyUSB0
"""
import time
import os

from lelekov_remote_lab.plotter import Plotter
from lelekov_remote_lab.communicator import Communicator
import numpy as np


#%% Предобработка данных
def sensor2BodyFrame(data):
    """ Перевод значений из приборной в связанную СК
    связанная СК: z по вертикали, х от RPi на зрителя, y вправо к вентилятору
    """
    state = {'u':data[0],
            'a':[data[3], -data[2], data[1]],
            'w':[data[6], -data[5], data[4]],
            'mAK':[-data[9], -data[7], data[8]],
            'mQMC':[-data[12], -data[10], data[11]]}
    return state


def calcState(state):
    """ расчёт угла ориентации по магнитометру QMC"""
    state['pos'] = np.arctan2(state['mQMC'][1], state['mQMC'][0])*180/np.pi
    state['vel'] = state['w'][2]
    return state


def linsmf(x,a,b):
    if x<a:
        return 0
    elif x<=b:
        return (x-a)/(b-a)
    else:
        return 1


def linzmf(x,a,b):
    if x<a:
        return 1
    elif x<=b:
        return 1-(x-a)/(b-a)
    else:
        return 0


def trapmf(x, a,b,c,d):
    return max(min((x-a)/(b-a),1,(d-x)/(d-c)),0)


def notf(a):
    return 1-a


def orf(*A):
    return max(*A)


def andf(*A):
    return min(*A)


#%% Закон управления
def control(t, W, phi):
    """ управление """
    w = abs(W)

    o1a, o1b = 0, 0.1
    o2a, o2b, o2c, o2d = 0.07, 0.2, 0.5, 0.65
    o3a, o3b = 0.7, 1

    i1a, i1b = 0, 3
    i2a, i2b = 5, 20

    i1mf = linzmf(w, i1a, i1b)  # 'скорость требуемая'
    i2mf = linsmf(w, i2a, i2b)  # 'скорость большая'

    # Применяем условия
    ant1 = i2mf
    ant2 = i1mf
    ant3 = andf(notf(i1mf), notf(i2mf))

    # Имликация
    impl1 = lambda u: min(ant1, linsmf(u, o3a, o3b))
    impl2 = lambda u: min(ant2, linzmf(u, o1a, o1b))
    impl3 = lambda u: min(ant3, trapmf(u, o2a, o2b, o2c, o2d))

    # Агрегация классическая / дефаззификация

    agg = []
    y_vector = np.linspace(0, 1, 20)
    for yi in y_vector:
        agg.append(max(impl1(yi), impl2(yi), impl3(yi)))

    # Находим ЦМ
    sumAYDy, sumADy = 0., 0.
    for (yi, aggi) in zip(y_vector, agg):
        sumAYDy = sumAYDy + aggi * yi
        sumADy += aggi

    return -np.sign(W) * sumAYDy/sumADy

#%% Основной цикл
state = {'vel':0, 'pos':0}
HOST_IP = os.environ.get('HOST_IP')

with Communicator(
        host_ip=HOST_IP,
        host_port=6503,
        bind_port=6501) as comm, Plotter() as plotter:

    t0 = time.time()
    while True:
        try:
            # расчёт управления
            u = control(time.time()-t0, state['vel'], state['pos'])

            # отправляем его в НОК
            comm.control(u)

            # принимаем ответ
            data = comm.measure()

            # переводим из ПСК в СвСК
            data = sensor2BodyFrame(data)

            # рассчитываем состояние
            state = calcState(data)

            plotter.add_data(time.time()-t0, (state['pos'], state['vel'], u))
            if plotter.stop_now:
                break

        except KeyboardInterrupt:
            print('\n[*] Exit...')
            break
