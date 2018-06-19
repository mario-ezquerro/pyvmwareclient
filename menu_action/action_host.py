#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""
Actions to make at the menu

"""

import sys
import os
import wx
import wx.lib.mixins.listctrl as listmix
import ssl
import OpenSSL
import logging.config
import humanize
from wxgladegen import dialogos
import wx.lib.mixins.listctrl as listmix
from pyVmomi import vim
from tools import tasks
from distutils.spawn import find_executable

__author__ = "Mario Ezquerro."

__all__ = [
    'locatehost',
]



def locatehost(self, conexion, logger):
    """
        Arg:
            event       (Var from menu)
            conexion    (Var whit a conexion datacenter)
            logger      (Var objet to pass the log)
    """
    
    MBFACTOR = float(1 << 20)
    index = 0
  
    my_dialogo_host = dialogos.Dialogo_host(None, -1, 'Host en vcenter')

    self.list_ctrl_host = theListCtrlHost(my_dialogo_host, -1, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.SUNKEN_BORDER)

    name_rows = ['Data center', 'Resource Name', 'Host Name', 'CPU usage', 'Host memory capacity', 'Host memory usag', 'Free memory percentage']
    # cargamos los nombres de los elementos
    
    for i in range(len(name_rows)):
        self.list_ctrl_host.InsertColumn(i, name_rows[i])

    #Find the all items host to checking
    max = 0
    for datacenter in conexion.rootFolder.childEntity:
        max += 1
        if hasattr(datacenter.vmFolder, 'childEntity'):
            hostFolder = datacenter.hostFolder
            computeResourceList = hostFolder.childEntity
            for computeResource in computeResourceList:
                max += 1
                hostList = computeResource.host
                max = max + len(hostList)
    if logger != None: logger.info('el maximo es : {}'.format(max))
    
    keepGoing = True
    count = 0
    dlg = wx.ProgressDialog("Proceso cargando datos",
                            "Cargando datos",
                            maximum = max, )
    keepGoing = dlg.Update(count)


    for datacenter in conexion.rootFolder.childEntity:
            count += 1
            keepGoing = dlg.Update(count, "Loading")
      
            if hasattr(datacenter.vmFolder, 'childEntity'):
         
                    hostFolder = datacenter.hostFolder
                    computeResourceList = hostFolder.childEntity
                    
                    for computeResource in computeResourceList:
                        count += 1
                        keepGoing = dlg.Update(count, "Loading")
                        hostList = computeResource.host
                        for host in hostList:
                            count += 1
                            keepGoing = dlg.Update(count, "Loading")

                            summary = host.summary
                            stats = summary.quickStats
                            hardware = host.hardware
                            cpuUsage = stats.overallCpuUsage
                            memoryCapacity = hardware.memorySize
                            memoryCapacityInMB = hardware.memorySize/MBFACTOR
                            memoryUsage = stats.overallMemoryUsage
                            freeMemoryPercentage = 100 - ((float(memoryUsage) / memoryCapacityInMB) * 100)

                            #print ("--------------------------------------------------")
                            #print ("Host name: ", host.name)
                            #print ("Host CPU usage: ", cpuUsage)
                            #print ("Host memory capacity: ", humanize.naturalsize(memoryCapacity, binary=True))
                            #print ("Host memory usage: ", memoryUsage / 1024, "GiB")
                            #print ("Free memory percentage: " + str(freeMemoryPercentage) + "%")
                            #print ("--------------------------------------------------")

                            self.list_ctrl_host.InsertItem(index, datacenter.name)
                            self.list_ctrl_host.SetItem(index, 1, str(computeResource.name))
                            self.list_ctrl_host.SetItem(index, 2, str(host.name))
                            self.list_ctrl_host.SetItem(index, 3, str(cpuUsage))
                            self.list_ctrl_host.SetItem(index, 4, str(humanize.naturalsize(memoryCapacity, binary=True)))
                            self.list_ctrl_host.SetItem(index, 5, str(memoryUsage / 1024) + " GiB")
                            self.list_ctrl_host.SetItem(index, 6, str(freeMemoryPercentage) + " %")
                            #for use to auto use for auto sort colum
                            self.list_ctrl_host.SetItemData(index, index)
                            index += 1

    dlg.Destroy()

    my_dialogo_host.sizer_main.Add(self.list_ctrl_host,  1, wx.ALL | wx.EXPAND, 0)
    #my_dialogo_host.sizer_main.Replace(self, my_dialogo_host.sizer_main.list_ctrl_host_old, self.list_ctrl_host, recursive=False)
    
    my_dialogo_host.SetSizer(my_dialogo_host.sizer_main)

    # For use to auto-orden --- Call to Getlistctrl
    self.list_ctrl_host.data_to_orden(self.list_ctrl_host, name_rows)
    
    my_dialogo_host.ShowModal()
    #manager_graf.display_plot(conexion)

class theListCtrlHost(wx.ListCtrl, listmix.ColumnSorterMixin):

  def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

  def data_to_orden(self, list_ctrl_host, name_rows):
    self.list_ctrl_host=list_ctrl_host
    self.name_rows=name_rows
    self.tabla_host=[]
    for line_host in range(self.list_ctrl_host.GetItemCount()):
        linea=[]
        for item_linea in range(len(self.name_rows)):
            linea.append(self.list_ctrl_host.GetItemText(line_host, item_linea))
        self.tabla_host.append(linea)

    # For use to auto-orden --- Call to Getlistctrl
    self.itemDataMap = self.tabla_host
    listmix.ColumnSorterMixin.__init__(self, len(self.name_rows))


  # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
  def GetListCtrl(self):
       return self.list_ctrl_host