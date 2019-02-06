#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#Импортируем библиотеку Math
import math
#Импортируем один из пакетов Matplotlib
import pylab
#Импортируем пакет со вспомогательными функциями
from matplotlib import mlab

#Рисуем график функции y = sin(x)
def func (x):
    """
    sin (x)
    """
    return math.sin (x)
    
#Указываем X наименьее и наибольшее
xmin = -10.0
xmax = 10.0

# Шаг между точками
dx = 0.01

#Создадим список координат по оси 
#X на отрезке [-xmin; xmax], включая концы
xlist = mlab.frange (xmin, xmax, dx)

# Вычислим значение функции в заданных точках
ylist = [func (x) for x in xlist]

#Нарисуем одномерный график
pylab.plot (xlist, ylist)

#Покажем окно с нарисованным графиком
pylab.show()
