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
from menu_action import manager_graf_host
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
    self.list_ctrl_host.logger = logger
    self.list_ctrl_host.conexion = conexion

    name_rows = ['Data center',
                 'Resource Name',
                 'Host Name',
                 'CPU usage',
                 'Host memory capacity',
                 'Host memory usag',
                 'Free memory percentage',
                 'datacenter',
                 'computeResource',
                 'host']
    # cargamos los nombres de los elementos
    
    for i in range(len(name_rows)):
        self.list_ctrl_host.InsertColumn(i, name_rows[i], format=wx.LIST_FORMAT_LEFT, width=150)

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
                            self.list_ctrl_host.SetItem(index, 7, str(datacenter))
                            self.list_ctrl_host.SetItem(index, 8, str(computeResource))
                            self.list_ctrl_host.SetItem(index, 9, str(host))
                            #for use to auto use for auto sort colum
                            self.list_ctrl_host.SetItemData(index, index)
                            index += 1

    dlg.Destroy()

    my_dialogo_host.sizer_main.Add(self.list_ctrl_host,  -1, wx.ALL | wx.EXPAND, 5)
    #my_dialogo_host.sizer_main.Replace(my_dialogo_host.sizer_main.list_ctrl_host_old, my_dialogo_host.sizer_main.self.list_ctrl_host, recursive=False)
    
    my_dialogo_host.SetSizer(my_dialogo_host.sizer_main)

    # For use to auto-orden --- Call to Getlistctrl
    self.list_ctrl_host.data_to_orden(self.list_ctrl_host, name_rows)  
    my_dialogo_host.ShowModal()


class theListCtrlHost(wx.ListCtrl, listmix.ColumnSorterMixin):
  global conexion

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

    # Add menu to Click element in VM 
    self.list_ctrl_host.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_iten_host_selected, self.list_ctrl_host)


  # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
  def GetListCtrl(self):
       return self.list_ctrl_host


  # Prepare menu about dialog click over VM machine in list ##############
  def on_iten_host_selected(self, event):
        #localizamos el elemento seleccionado en el listado ordenado , y cargamos la fila
        if self.logger != None: self.logger.info('evento= '+ str(event.Index))
        self.posicionLista = event.Index
        self.listado_host = []
        if self.logger != None: self.logger.info('datos en la fila= '+ str(self.list_ctrl_host.GetColumnCount()))
        for item_comlum in range(self.list_ctrl_host.GetColumnCount()):
            self.listado_host.append(self.list_ctrl_host.GetItemText( self.posicionLista,item_comlum))
        if self.logger != None: self.logger.info( 'el otro ' + self.list_ctrl_host.GetItemText( self.posicionLista,1))
        if self.logger != None: self.logger.info( 'posicionlista= {} listado host= {}'.format(self.posicionLista, self.listado_host))

        #if not hasattr(self, "sshID"):
        self.graf_host = wx.NewId()
        self.event_host = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_graf_host, id=self.graf_host)
        self.Bind(wx.EVT_MENU, self.on_event_host, id=self.event_host)
        
        # build the menu
        self.menu_host = wx.Menu()
        item_separador = self.menu_host.AppendSeparator()
        item_graf_vm = self.menu_host.Append(self.graf_host, "Grafic Host...")
        item_event_vm = self.menu_host.Append(self.event_host, "Event Host...")
        item_separador = self.menu_host.AppendSeparator()
        
        # show the popup menu
        self.PopupMenu(self.menu_host)
        self.menu_host.Destroy()

    #########ADD the command to the events in the display dilog ######
  def on_graf_host(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        """conexion = self.checking_conexion(conexion)"""
        manager_graf_host.display_plot(self, event, self.logger, self.conexion)

  def on_event_host(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        """conexion = self.checking_conexion(conexion)"""
        #manager_graf_host.display_plot(self, event, self.logger, self.conexion)
        dlg_info_pass = wx.MessageDialog(None,
                                     'Not implemented',
                                     'Not implemented',
                                     wx.OK )
        result_dlg_info_pass = dlg_info_pass.ShowModal()
        dlg_info_pass.Destroy()