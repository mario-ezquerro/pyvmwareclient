#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
#
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Class to create graf about VM

"""

import wx
import ssl
import OpenSSL
import logging.config
from wxgladegen import dialogos
from pyVmomi import vim
from tools import tasks

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation


__author__ = "Mario Ezquerro."


__all__ = [
    'ManagerGrafVM',
]

def data_gen_maxCpuUsage(oid):
        while True:
            x = oid.runtime.maxCpuUsage
            yield x 

def data_gen_maxMemoryUsage(oid):
        while True:
            x = oid.runtime.maxMemoryUsage
            yield x 

def data_gen_memorySizeMB(oid):
        while True:
            x = oid.summary.config.memorySizeMB
            yield x 

def data_gen_memory_overallCpuUsage(oid):
        while True:
            x = oid.summary.quickStats.overallCpuUsage
            yield x 

def data_gen_memory_overallCpuDemand(oid):
        while True:
            x = oid.summary.quickStats.overallCpuDemand
            yield x 

def data_gen_memory_guestMemoryUsage(oid):
        while True:
            x = oid.summary.quickStats.guestMemoryUsage
            yield x 

def data_gen_memory_privateMemory(oid):
        while True:
            x = oid.summary.quickStats.privateMemory
            yield x 

def data_gen_memory_sharedMemory(oid):
        while True:
            x = oid.summary.quickStats.sharedMemory
            yield x 


def data_gen_memory_swappedMemory(oid):
        while True:
            x = oid.summary.quickStats.swappedMemory
            yield x 


def graf_vm(self, event, conexion, logger):
    """
    Arg:
        event       (Var from menu)
        conexion    (Var whit a conexion datacenter)
        logger      (Var objet to pass the log)
    """
    fila = self.listadoVM
    for i in range(len(fila)):
        if logger != None: logger.info('Create plots about: ' + fila[i])
    vm = conexion.searchIndex.FindByUuid(None,fila[8], True)


    #grafica 1
    fig1, ax = plt.subplots(3, 3)

    scope_maxCpuUsage = Scope(ax[0,0],
                          label ='maxCpuUsage',
                          oid = vm.runtime.maxCpuUsage,
                          maxy = 500,
                          maxt = 100)


    graf_ani1 = animation.FuncAnimation(fig1, 
                                       scope_maxCpuUsage.update,
                                       data_gen_maxCpuUsage(oid=vm),
                                       interval=1000,
                                       blit=False)
    
    #grafica 2
    graf_memory_memorySizeMB = Scope(ax[0,1],
                          label ='memorySizeMB',
                          oid = vm.runtime.maxMemoryUsage,
                          maxy = 10000,
                          maxt = 100)


    graf_ani2 = animation.FuncAnimation(fig1, 
                                       graf_memory_memorySizeMB.update,
                                       data_gen_memorySizeMB(oid=vm),
                                       interval=1000,
                                       blit=False)


    #grafica 3
    graf_cpu_memorySizeMB = Scope(ax[0,2],
                          label ='memorySizeMB',
                          oid = vm.summary.config.memorySizeMB,
                          maxy = 50,
                          maxt = 100)


    graf_ani3 = animation.FuncAnimation(fig1, 
                                       graf_cpu_memorySizeMB.update,
                                       data_gen_memorySizeMB(oid=vm),
                                       interval=1000,
                                       blit=False)
    #grafica 4
    graf_memory_overallCpuUsage = Scope(ax[1,0],
                          label ='overallCpuUsage',
                          oid = vm.summary.quickStats.overallCpuUsage,
                          maxy = 50,
                          maxt = 100)


    graf_ani4 = animation.FuncAnimation(fig1,
                                       graf_memory_overallCpuUsage.update,
                                       data_gen_memory_overallCpuUsage(oid=vm),
                                       interval=1000,
                                       blit=False)

    #grafica 5
    graf_memory_overallCpuDemand = Scope(ax[1,1],
                          label ='overallCpuDemand',
                          oid = vm.summary.quickStats.overallCpuDemand,
                          maxy = 50,
                          maxt = 100)


    graf_ani5 = animation.FuncAnimation(fig1,
                                       graf_memory_overallCpuDemand.update,
                                       data_gen_memory_overallCpuDemand(oid=vm),
                                       interval=1000,
                                       blit=False)

    #grafica 6
    graf_memory_guestMemoryUsage = Scope(ax[1,2],
                          label ='guestMemoryUsage',
                          oid = vm.summary.quickStats.guestMemoryUsage,
                          maxy = 50,
                          maxt = 100)


    graf_ani6 = animation.FuncAnimation(fig1,
                                       graf_memory_guestMemoryUsage.update,
                                       data_gen_memory_guestMemoryUsage(oid=vm),
                                       interval=1000,
                                       blit=False)

    #grafica 7
    graf_memory_privateMemory = Scope(ax[2,0],
                          label ='privateMemory',
                          oid = vm.summary.quickStats.privateMemory,
                          maxy = 50,
                          maxt = 100)


    graf_ani7 = animation.FuncAnimation(fig1,
                                       graf_memory_privateMemory.update,
                                       data_gen_memory_privateMemory(oid=vm),
                                       interval=1000,
                                       blit=False)

    #grafica 8
    graf_memory_sharedMemory = Scope(ax[2,1],
                          label ='sharedMemory',
                          oid = vm.summary.quickStats.sharedMemory,
                          maxy = 50,
                          maxt = 100)


    graf_ani8 = animation.FuncAnimation(fig1,
                                       graf_memory_sharedMemory.update,
                                       data_gen_memory_sharedMemory(oid=vm),
                                       interval=1000,
                                       blit=False)

    #grafica 9
    graf_memory_swappedMemory = Scope(ax[2,2],
                          label ='swappedMemory',
                          oid = vm.summary.quickStats.swappedMemory,
                          maxy = 50,
                          maxt = 100)


    graf_ani9 = animation.FuncAnimation(fig1,
                                       graf_memory_swappedMemory.update,
                                       data_gen_memory_swappedMemory(oid=vm),
                                       interval=1000,
                                       blit=False)


    #plt.subplot_tool()
    fig1.suptitle('Data VM: {}'.format(vm.summary.config.name))
    plt.show()

class Scope(object):

    def __init__(self, ax, label, oid, maxy=500, maxt=100):
        self.ax = ax
        #self.name_host =  name_host
        self.label = label
        self.oid = oid
        self.maxy = maxy
        self.suma_maxy = self.oid + self.maxy
        self.maxt = maxt
        self.tdata = [0]
        self.ydata = [0]
        self.line = Line2D(self.tdata, self.ydata)
        self.ax.add_line(self.line)
        self.ax.set_ylim(0, self.suma_maxy)
        self.ax.set_xlim(0, self.maxt)
        self.ax.set_xlabel('Time [s]')
        #self.ax.set_ylabel('{}'.format(label))
        self.ax.grid()
        #self.ax.set_title('Host: {}'.format(self.name_host))
        self.ax.plot([], [], marker='x', linestyle=':', color='b', linewidth=0.55, label=self.label)
        #self.ax.plot([], [], marker='x', linestyle=':', color='b', linewidth=0.55)
        self.ax.legend(loc='upper left')
        self.t = 0


    def update(self, data):
        # update the data
        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.ydata = [self.ydata[-1]]
            self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax.figure.canvas.draw()
        
        lasty = self.ydata[-1] 
        if lasty > (self.suma_maxy -(self.suma_maxy/4)) :
            self.suma_maxy = self.suma_maxy + self.maxy
            #self.tdata = [self.tdata[-1]]
            #self.ydata = [self.ydata[-1]]
            self.ax.set_ylim(0, self.suma_maxy)
            self.ax.figure.canvas.draw()
        #seg = time.gmtime(time.time()).tm_sec
        self.t =  self.t + 1
        #self.y = self.tdata[-1] - time.gmtime(time.time()).tm_sec
        self.tdata.append(self.t)
        self.ydata.append(data)
        self.line.set_data(self.tdata, self.ydata)
        return self.line,
