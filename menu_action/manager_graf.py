#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""
Actions to make at the menu

"""

#import sys
#import os
import wx
import ssl
import OpenSSL
import logging.config
from wxgladegen import dialogos
from pyVmomi import vim
from tools import tasks

__author__ = "Mario Ezquerro."

__all__ = [
    'display_plot'
]



######################################
# New code to create plot draw about #
######################################

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
            f.write('{},{}\n'.format(str(timestamp), data))


        """with open(path, 'a') as f:
            for sample in samples:
                timestamp, values = sample[0].timestamp, sample[1:]
                if self.counter.unitInfo.key == 'percent':
                    f.write('{},{}\n'.format(str(timestamp), ','.join([str(v / 100) for v in values])))
                else:
                    f.write('{},{}\n'.format(str(timestamp), ','.join([str(v) for v in values])))"""


def display_plot(conexion):

    print(" The manual debug: {}".format(conexion.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0].summary.quickStats.overallCpuUsage))

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
    l = '"{}" using 0:1 title "INSTANCIALL" with lines'.format(datafile)
    
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
            "set timefmt '%Y-%m-%d %H:%M:%S+00:00'\n"
            "set format x '%H:%M:%S'\n"
            "set xlabel 'Time'\n"
            "set ylabel '{unit}'\n"
            "set key outside right center\n"
            "set datafile separator ','\n"
            "set autoscale fix\n"
            "set yrange [{yrange}]\n"
            "plot {lines}\n"
            "pause {pause}\n"
            '#reread\n'
        )

    gnuplot_script = script_template.format(
            name='Name',
            title='titulo',
            term=gnuplot_term,
            unit=5,
            lines=', '.join(lines),
            pause='mouse',
            yrange=yrange
    )

    with open(path, 'w') as f:
          f.write(gnuplot_script)
    

    p = subprocess.Popen(args=['cat', path])
    p = subprocess.Popen(args=['gnuplot', gnuplot_script])
    while True:
            #data = self.pm.QueryPerf(querySpec=[query_spec]).pop()
            #print("que hay en data: " + str(conexion.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0].summary.quickStats.overallCpuUsage))
            
            save_performance_samples(
                path=datafile,
                data=str(conexion.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0].summary.quickStats.overallCpuUsage)
            )

            """dlg = wx.MessageDialog(None, "Do you really want to close this application?",'Confirm Exit', wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            dlg.ShowModal()
               
            if dlg == wx.ID_OK:
                dlg.Destroy()
                break"""
            

    p.terminate()


    


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

        text = (
            'Graph updates every {} seconds.\n\n'
            'Press CANCEL in order to stop plotting the '
            'graph and exit.\n'
        )

        while True:
            data = self.pm.QueryPerf(querySpec=[query_spec]).pop()
            self.save_performance_samples(
                path=datafile,
                data=data
            )
            code = self.dialog.pause(
                title=self.title,
                text=text.format(interval_id),
                height=15,
                width=60,
                seconds=interval_id
            )
            if code == self.dialog.CANCEL:
                break

        p.terminate()

    my_dialogo_host.ShowModal()"""
    # For use to auto-orden --- Call to Getlistctrl
    #self.itemDataMap = self.tabla
    #my_dialogo_host.list_ctrl_host.ColumnSorterMixin.__init__(self, len(name_rows))

