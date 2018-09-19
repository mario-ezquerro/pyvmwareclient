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
    # Set a yrange for counters which unit is percentage
    yrange = '0:100' 
    #gnuplot_term = os.environ['GNUPLOT_TERM'] if os.environ.get('GNUPLOT_TERM') else 'dumb'
    gnuplot_term = 'qt'

    fs, path = tempfile.mkstemp(prefix='pvcgnuplot-script-')

    fd, datafile = tempfile.mkstemp(prefix='pvcgnuplot-data-')
    #script = create_gnuplot_script(
    #        datafile=datafile,
    #        instances=conexion.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0].summary.quickStats.overallCpuUsage
    #)

    lines = []
    #l = '"{datafile}" using 1:0 title "INSTANCIALL" with lines'
    formating_template = (
        '"{0}" using 1:2 title "CPU-Usage" with lines, '
        '"{0}" using 1:3 title "Memory-Usage" with lines, '
        '"{0}" using 1:4 title "CPU-Fairness" with lines, '
        '"{0}" using 1:4 title "Memory-Fairness" with lines'
        )

    # For use with matplotlib
    grafic2 = []
    grafic3 = []
    grafic4 = []
    
    #plt.grid(True)
    #
    #plt.plot(data1, marker='x', linestyle=':', color='b', linewidth=0.55, label='CPU-Usage')
    #plt.plot(grafic2, marker='*', linestyle='-', color='g', linewidth=0.25, label='Memory-Usage')
    #plt.plot(grafic3, marker='o', linestyle='--', color='r', linewidth=0.25, label='CPU-Fairness')
    #plt.plot(grafic4, marker='+', linestyle='-.', color='m', linewidth=0.25, label='Memory-Fairness')
    #plt.legend(loc='upper left')

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

    """
    # End for use with matplotlig
    l = formating_template.format(datafile)
    
    lines.append(l)"""
    """for index, instance in enumerate(instances):
            l = '"{datafile}" using 1:{index} title "{instance}" with lines'.format(
                datafile=datafile,
                index=index+2,
                instance=instance
            )
            lines.append(l)"""

    script_template = (
            "# gnuplot(1) script created by pyvmware\n"
            "set title '{name} - {title}'\n"
            "set term {term}\n"
            "set grid\n"
            "set xdata time\n"
            "set timefmt '%s'\n"
            "set format x '%H:%M:%S'\n"
            "set xlabel 'Time'\n"
            "set ylabel '{unit}'\n"
            "set key outside right center\n"
            "set datafile separator comma\n"
            "set autoscale fix\n"
            "#set yrange [{yrange}]\n"
            "plot {lines}\n"
            "pause {pause}\n"
            "reread\n"
        )

    gnuplot_script = script_template.format(
            name=list_data_host[0],
            title=list_data_host[2],
            term=gnuplot_term,
            unit=5,
            lines=', '.join(lines),
            pause = 5,
            yrange=yrange
    )

    with open(path, 'w') as f:
          f.write(gnuplot_script)
    

    #p = subprocess.Popen(args=['cat', path])
    metric=[]
    metric.append(host.summary.quickStats.overallCpuUsage)
    metric.append(host.summary.quickStats.overallMemoryUsage)
    metric.append(host.summary.quickStats.distributedCpuFairness)
    metric.append(host.summary.quickStats.distributedMemoryFairness)
    #
    #timestamp = time.time()
    #data1.append(host.summary.quickStats.overallCpuUsage)
    #grafic2.append(host.summary.quickStats.overallMemoryUsage)
    #grafic3.append(host.summary.quickStats.distributedCpuFairness)
    #grafic4.append(host.summary.quickStats.distributedMemoryFairness)
    
    #plt.show(block=False)
    #metric.append(host.summary.quickStats.uptime)
    data=metric
    with open(datafile, 'w') as fd:
            timestamp = time.time()
            fd.write('{},{}\n'.format(str(timestamp),','.join([str(one_data) for one_data in data])))
    
    """while True:
            timestamp = time.time()
            grafic1.append(host.summary.quickStats.overallCpuUsage)
            grafic2.append(host.summary.quickStats.overallMemoryUsage)
            grafic3.append(host.summary.quickStats.distributedCpuFairness)
            grafic4.append(host.summary.quickStats.distributedMemoryFairness)
            
            plt.plot(grafic1, grafic1)

            print('here')
            #plt.plot()
            plt.pause(0.001)"""
   

    #q_write = threading.Thread(target=write_data_host_file, args=(host, datafile, plt, grafic1, grafic2, grafic3, grafic4))
    #q_write.setDaemon(True)
    #q_write.start()
    #######p = subprocess.Popen(args=['gnuplot', path])

    """dlg_draw = wx.MessageDialog(None, "Press OK to stop plotting the graph and exit",'Confirm Exit', wx.OK  | wx.ICON_INFORMATION)
    result = dlg_draw.ShowModal()
    if result == wx.ID_OK:
        p.terminate()
        q_write.join(0.0)
        dlg_draw.Destroy()"""

    
        
    

def write_data_host_file(host, datafile, plt, grafic1, grafic2, grafic3, grafic4):
        while True:
            timestamp = time.time()
            metric=[]
            metric.append(host.summary.quickStats.overallCpuUsage)
            metric.append(host.summary.quickStats.overallMemoryUsage)
            metric.append(host.summary.quickStats.distributedCpuFairness)
            metric.append(host.summary.quickStats.distributedMemoryFairness)
            #metric.append(host.summary.quickStats.uptime)
            grafic1.append(host.summary.quickStats.overallCpuUsage)
            grafic2.append(host.summary.quickStats.overallMemoryUsage)
            grafic3.append(host.summary.quickStats.distributedCpuFairness)
            grafic4.append(host.summary.quickStats.distributedMemoryFairness)
            
            plt.plot(grafic1, grafic1)
            print('here')
            #plt.plot()
            plt.pause(5.00)
           
            """
            save_performance_samples(
                path=datafile,
                data=metric
            )
            """

    


def save_performance_samples(path, data):
        """
        Save performance samples to a file

        New samples are appended to the file

        NOTE: If the performance counter unit is percentage we need
              to make sure that the sample value is divided by
              a hundred, as the returned sample value
              represents a 1/100th of the percent.

        Args:
            path                                      (str): Path to the datafile
            data  (vim.PerformanceManager.EntityMetricBase): The data to be saved

        """
        #all_values = [v.value for v in data.value]
        #samples = zip(data.sampleInfo, *all_values)
        samples = data

        with open(path, 'a') as f:
            timestamp = time.time()
            f.write('{},{}\n'.format(str(timestamp), ','.join([str(one_data) for one_data in data])))


        """with open(path, 'a') as f:
            for sample in samples:
                timestamp, values = sample[0].timestamp, sample[1:]
                if self.counter.unitInfo.key == 'percent':
                    f.write('{},{}\n'.format(str(timestamp), ','.join([str(v / 100) for v in values])))
                else:
                    f.write('{},{}\n'.format(str(timestamp), ','.join([str(v) for v in values])))"""

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

    

