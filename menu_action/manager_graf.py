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
import matplotlib.pyplot as plt
import matplotlib.animation as animation

__author__ = "Mario Ezquerro."

__all__ = [
    'display_plot'
]

def display_plot(self, event, logger, conexion):

    def data_animate(*args):
        #data1.append(host.summary.quickStats.overallCpuUsage)     
        return data1,

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
                       oui_host_data = host
                       break

    if logger != None: logger.info('The OUI is : {}'.format(oui_host_data))    
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
    print("{}".format(oui_host_data.summary.quickStats))
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
    
    plt.grid(True)
    #plt.xlabel('Time') 
    #plt.plot(data1, marker='x', linestyle=':', color='b', linewidth=0.55, label='CPU-Usage')
    #plt.plot(grafic2, marker='*', linestyle='-', color='g', linewidth=0.25, label='Memory-Usage')
    #plt.plot(grafic3, marker='o', linestyle='--', color='r', linewidth=0.25, label='CPU-Fairness')
    #plt.plot(grafic4, marker='+', linestyle='-.', color='m', linewidth=0.25, label='Memory-Fairness')
    #plt.legend(loc='upper left')

    fig1 = plt.figure()
    data1 = []
    data1.append(host.summary.quickStats.overallCpuUsage)

    l1, = plt.plot([], [], marker='x', linestyle=':', color='b', linewidth=0.55, label='CPU-Usage')
    l2, = plt.plot([], [], marker='*', linestyle='-', color='g', linewidth=0.25, label='Memory-Usage')

    plt.title("{name} - {title}".format(name=list_data_host[0],title=list_data_host[2]))

    graf_ani = animation.FuncAnimation(fig1, 
                                       data_animate, 
                                       data1, 
                                       interval=50, 
                                       repeat_delay=3000, 
                                       blit=True)
    
    plt.show()


    #plt.show()
    # End for use with matplotlig
    l = formating_template.format(datafile)
    
    lines.append(l)
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



""" metric_id = [
            pyVmomi.vim.PerformanceManager.MetricId(
                counterId=self.counter.key,
                instance='' if instance == self.obj.name else instance
            ) for instance in selected_instances
        ]

     query_spec = pyVmomi.vim.PerformanceManager.QuerySpec(
            maxSample=1,
            entity=self.obj,
            metricId=metric_id,
            intervalId=interval_id
        )

        p = subprocess.Popen(
            args=['gnuplot', script]
        )

        

        while True:
            data = self.pm.QueryPerf(querySpec=[query_spec]).pop()
            self.save_performance_samples(
                path=datafile,
                data=data
            )
            

    my_dialogo_host.ShowModal()"""

