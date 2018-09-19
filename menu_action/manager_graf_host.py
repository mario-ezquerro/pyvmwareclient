#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""
Actions to make graf about host
"""

#import sys
#import os
import wx
import ssl
import OpenSSL
import logging.config
import subprocess
import datetime
import time
import tempfile
import threading
from wxgladegen import dialogos
from pyVmomi import vim
from tools import tasks
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation 


__author__ = "Mario Ezquerro."

__all__ = [
    'display_plot'
]


def data_gen_cpu_usage(oid):
        while True:
            x = oid.summary.quickStats.overallCpuUsage
            yield x 

def data_gen_memory_usage(oid):
        while True:
            x = oid.summary.quickStats.overallMemoryUsage
            yield x 

def data_gen_cpu_fairness(oid):
        while True:
            x = oid.summary.quickStats.distributedCpuFairness
            yield x 

def data_gen_memory_fairness(oid):
        while True:
            x = oid.summary.quickStats.distributedMemoryFairness
            yield x 

def display_plot(self, event, logger, conexion):

    

    if logger != None: logger.info(" \n The manual debug: {}".format(conexion.rootFolder.childEntity[0].hostFolder.childEntity[0].host))
    posicion=self.posicionLista
    list_data_host=self.listado_host
    #Find the OID HOST for read data  to checking
    for datacenter in conexion.rootFolder.childEntity:
        if hasattr(datacenter.vmFolder, 'childEntity'):
            hostFolder = datacenter.hostFolder
            computeResourceList = hostFolder.childEntity
            for computeResource in computeResourceList:
                hostList = computeResource.host
                for host in hostList:
                   if list_data_host[7]==str(datacenter) and list_data_host[8]==str(computeResource) and list_data_host[9]==str(host):
                       oid_host_data = host
                       break

    if logger != None: logger.info('The OUI is : {}'.format(oid_host_data))    
    try:
            subprocess.Popen(
                args=['gnuplot', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
                
    except OSError as e:

            if logger != None: logger.info('Error no gnunplot or not path to gnuplot')

            dlg = wx.MessageDialog(self.my_dialog, 'Unable to find gnuplot(1): \n{}\n'.format(e), style = wx.OK  | wx.ICON_QUESTION)
            dlg.ShowModal()
            dlg.Destroy()

            return

    #Locate metric on host
    print("{}".format(oid_host_data.summary.quickStats))
    #print("{}".format(conexion.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0].hardware))

    #grafica 1
    fig1, ax = plt.subplots(2, 2)

    scope_cpu = Scope(ax[0,0],
                          label ='CPU-Usage',
                          oid = oid_host_data.summary.quickStats.overallCpuUsage,
                          maxy = 500,
                          maxt = 100)


    graf_ani1 = animation.FuncAnimation(fig1, 
                                       scope_cpu.update,
                                       data_gen_cpu_usage(oid=oid_host_data),
                                       interval=1000,
                                       blit=False)
    
    #grafica 2
    graf_memory_usage = Scope(ax[0,1],
                          label ='Men-Usage',
                          oid = oid_host_data.summary.quickStats.overallMemoryUsage,
                          maxy = 10000,
                          maxt = 100)


    graf_ani2 = animation.FuncAnimation(fig1, 
                                       graf_memory_usage.update,
                                       data_gen_memory_usage(oid=oid_host_data),
                                       interval=1000,
                                       blit=False)


    #grafica 3
    graf_cpu_fairness = Scope(ax[1,0],
                          label ='CPU-UsFairness',
                          oid = oid_host_data.summary.quickStats.distributedCpuFairness,
                          maxy = 50,
                          maxt = 100)


    graf_ani3 = animation.FuncAnimation(fig1, 
                                       graf_cpu_fairness.update,
                                       data_gen_cpu_fairness(oid=oid_host_data),
                                       interval=1000,
                                       blit=False)
    #grafica 4
    graf_memory_fairness = Scope(ax[1,1],
                          label ='Men-Fairness',
                          oid = oid_host_data.summary.quickStats.distributedMemoryFairness,
                          maxy = 50,
                          maxt = 100)


    graf_ani4 = animation.FuncAnimation(fig1,
                                       graf_memory_fairness.update,
                                       data_gen_memory_fairness(oid=oid_host_data),
                                       interval=1000,
                                       blit=False)

    #plt.subplot_tool()
    fig1.suptitle('Data host: {}'.format(str(list_data_host[2])))
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
        if lasty > (self.suma_maxy -(self.suma_maxy/8)) :
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

    

