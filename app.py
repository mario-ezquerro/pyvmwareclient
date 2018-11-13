#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import wx
import wx.lib.mixins.listctrl as listmix
import wx.lib.inspection
import atexit
import ssl
import os
import re
import time
import OpenSSL
import webbrowser
import logging.config
import humanize
import sys
import csv
import maquina
#from threading import Thread #The snapshot is crating in a tread to not stop the app
from wxgladegen import dialogos
from pyVim.connect import SmartConnect, Disconnect
from tools import tasks
from tools import vm
from tools import alarm
from pyVmomi import vim

from menu_action import action_vm
from menu_action import action_host
from menu_action import manager_snap
from menu_action import manager_graf_vm

import datetime
import tempfile
import subprocess


class theListCtrl(wx.ListCtrl):
    # ----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        
class MyPanel(wx.Panel, listmix.ColumnSorterMixin):
    """
        Create the center window 
    
    """
    global conexion

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        

        # self.Bind(wx.EVT_BUTTON, self.OnSelectFont, btn)

        self.list_ctrl = theListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.SUNKEN_BORDER)
        st1 = wx.StaticText(self, label='Find String VM: ')
        self.strind_search = wx.TextCtrl(self)
        btn_find_vm = wx.Button(self, label="Find")
        btn_load_vm = wx.Button(self, label="Load VCenter DATA")
        btn_save_file_vm = wx.Button(self, label="Save file VM")
        btn_load_file_vm = wx.Button(self, label="Load file VM")
        btnhost = wx.Button(self, label="host")

        self.name_rows = ['Folder', 'Name', 'IP', 'State', 'DNS-Name', 'Path Disk', 'Sistem', 'Note', 'uuid', 'Macs', 'Sign', 'Resource Pool']

        # Import the table name_rows into supertable
        for x in range(len(self.name_rows)):
            self.list_ctrl.InsertColumn(x, self.name_rows[x],format=wx.LIST_FORMAT_LEFT, width=150)

        #conexion = connect_with_vcenter(self, id)
        
        self.tabla = []
        ### -> if the app is loading at start the VM, you need uncomment the next line (you need uncomment another lines).
        ######self.tabla = download_list_folder_and_vm(conexion)
        self.vm_buscados = []

        ### -> if the app is loading at start the VM, you need uncomment the next line (you need uncomment another lines).
        #self.cargardatos_en_listctrl(self.tabla)
        
        """# For use to auto-orden --- Call to Getlistctrl
        self.itemDataMap = self.tabla
        listmix.ColumnSorterMixin.__init__(self, len(self.name_rows))"""

        # Add menu to Click element in VM 
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onItemSelected, self.list_ctrl)
        #self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self.list_ctrl)
        #self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onItemSelected, self.list_ctrl)

        # This code put items into window with orden.
        self.count_str_vm = wx.StaticText(self, label='All VM: ' + str(len(self.tabla)))
        sizer = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        hbox1.Add(btn_load_vm, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)
        hbox1.Add(btn_save_file_vm, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)
        hbox1.Add(btn_load_file_vm, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)

        hbox1.Add(st1, wx.ALL | wx.ALIGN_RIGHT, 5)
        hbox1.Add(self.strind_search, wx.ALL | wx.ALIGN_CENTER, 5)
        hbox1.Add(btn_find_vm, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)
        
        hbox1.Add(btnhost, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)
        hbox1.Add(self.count_str_vm, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_CENTER, border=2)
        self.Bind(wx.EVT_BUTTON, self.search_data_vm, btn_find_vm)
        self.Bind(wx.EVT_BUTTON, self.reload_vm, btn_load_vm)#onItemSelected
        self.Bind(wx.EVT_BUTTON, self.save_file_vm, btn_save_file_vm)
        self.Bind(wx.EVT_BUTTON, self.load_file_vm, btn_load_file_vm)
        self.Bind(wx.EVT_BUTTON, self.bntlocateHost, btnhost)
        
        sizer.Add(self.list_ctrl, 1, wx.EXPAND)
        self.SetSizer(sizer)
        sizer.Layout()

        #Call to function for locate the esxi
        #onItemSelected

        # tools for search an debug (to use uncomment the next line, works only linux)
        # wx.lib.inspection.InspectionTool().Show()

    def bntlocateHost(self, event):
        
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_host.locatehost(self, conexion, logger)
    # ----------------------------------------------------------------------
    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.list_ctrl

    # buscamos un string en el nombre de las VM y lo pintamos de amarillo
    # si habia antes algo de amarillo lo ponemos blanco
    def search_data_vm(self, event):

            self.cargardatos_en_listctrl(self.tabla)
            
            parabuscar = self.strind_search.GetValue()
        
            #parabuscar = re.comp(parabuscar, re.IGNORECASE)
            if parabuscar:
                i = self.list_ctrl.GetItemCount() - 1
                while i >= 0 : # find data in name col=1, ip col=2 and mac col=9 dns_name=4
                    if re.search(parabuscar, self.list_ctrl.GetItemText(i, col=1),re.IGNORECASE) or \
                    re.search(parabuscar, self.list_ctrl.GetItemText(i, col=2),re.IGNORECASE) or \
                    re.search(parabuscar, self.list_ctrl.GetItemText(i, col=4),re.IGNORECASE) or \
                    re.search(parabuscar, self.list_ctrl.GetItemText(i, col=9),re.IGNORECASE):
                        self.list_ctrl.SetItemBackgroundColour(i, 'yellow')
                    else:
                        self.list_ctrl.DeleteItem(i)
                    i -= 1
            else:
                self.cargardatos_en_listctrl(self.tabla)

    def reload_vm(self, event):
        # conexion = connect_with_vcenter(self, id)
        #for i in range(self.list_ctrl.GetItemCount() - 1):
        #   self.list_ctrl.DeleteItem(i)
        
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        try:
            control = conexion.rootFolder.childEntity
            if logger != None: logger.info('connecting: {}'.format(conexion.rootFolder.childEntity))
            if logger != None: logger.info('connecting')

        except:
            if logger != None: logger.info('NOT connecting')
            conexion = connect_with_vcenter()

        self.servidores = []
        ###print( 'La conexion esta: {}'.format(conexion))

        self.servidores = download_list_folder_and_vm(conexion)
        # The array obj VM traslate to table

        self.tabla = []
        elemento = []
    
        for i in range(len(self.servidores)):
            elemento.append(self.servidores[i].listado_folders)
            elemento.append(self.servidores[i].name)
            elemento.append(self.servidores[i].dirip)
            elemento.append(self.servidores[i].state)
            elemento.append(self.servidores[i].dns_name)
            elemento.append(self.servidores[i].path)
            elemento.append(self.servidores[i].guest)
            elemento.append(self.servidores[i].anotacion)
            elemento.append(self.servidores[i].uuid)
            elemento.append(self.servidores[i].dirmacs)
            elemento.append(self.servidores[i].sing)
            elemento.append(self.servidores[i].resource_pool)
            self.tabla.append(elemento)
            elemento = []

        self.vm_buscados = []
        self.cargardatos_en_listctrl(self.tabla, _save = True)

    def save_file_vm(self, event=None):
        """
        This function write a file wiht table information.

        :param event:   when call this funtcion from button the pass a event
                        when call from another code the event = Nont
        :return: Not return need

        """
        saveFileDialog = wx.FileDialog(frame, "Save file with VM data", "", "", 
                                      "Python files ('table_vm.csv')|*.csv", 
                                       wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        saveFileDialog.ShowModal()
        file_to_save = saveFileDialog.GetPath()
        saveFileDialog.Destroy()
        if logger != None: logger.info('Start to write table -> {}'.format(file_to_save))

        with open(file_to_save, 'w')as my_csv_file_vm:
             f_writer = csv.writer(my_csv_file_vm, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
             f_writer.writerow([head for head in self.name_rows])
             for row in self.tabla:
                 row_witnout_return = []
                 for x in range(len(row)):
                     element_without_return = row[x].split('\n')
                     element_without_return = str(element_without_return[0])
                     row_witnout_return.append(element_without_return)
                 f_writer.writerow(row_witnout_return)
                 #f_writer.writerows("end")
             #f_writer.writerows(self.tabla)
        my_csv_file_vm.close()
        
        # For use to auto-orden --- Call to Getlistctrl
        self.itemDataMap = self.tabla
        listmix.ColumnSorterMixin.__init__(self, len(self.name_rows))

        if logger != None: logger.info('End to write table -> {}'.format(file_to_save))
    
    def load_file_vm(self, event=None):
        openFileDialog = wx.FileDialog(frame, "Open", "", "", 
                                      "Python files (*.csv)|*.csv", 
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        if logger != None: logger.info('file select to load {}'.format(openFileDialog.GetPath()))
        file_to_open = openFileDialog.GetPath()
        openFileDialog.Destroy()

        if logger != None: logger.info('Start to Load table from {}'.format(file_to_open))
        self.tabla=[]
        with open(file_to_open, 'r')as my_csv_file_vm:
             f_reader = csv.reader(my_csv_file_vm, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
             for row in f_reader:
                 self.tabla.append(row)
        #delete head they are not real data similar self.tabla.pop(0)
        try:       
            self.tabla.remove(self.name_rows)
            self.cargardatos_en_listctrl(self.tabla)
        except:
            dlgerror = wx.MessageDialog(self,
                                   "Error load file, error in data {}.".format(file_to_open),
                                   caption = "Info Error load {}.".format(file_to_open),
                                   style= wx.OK | wx.ICON_QUESTION)
            dlgerror.ShowModal()
            dlgerror.Destroy()
            if logger != None: logger.warning('Error load {} file'.format(file_to_open))

        my_csv_file_vm.close()
        
        # For use to auto-orden --- Call to Getlistctrl
        self.itemDataMap = self.tabla
        listmix.ColumnSorterMixin.__init__(self, len(self.name_rows))

        if logger != None: logger.info('End to load table from {}'.format(file_to_open))

    

    def cargardatos_en_listctrl(self, _tabla_paracargar, _save = False):
        # cargamos las busquedas en el listado de tablas.
        #self.myRowDict = {}
        self.list_ctrl.DeleteAllItems()
        index = 0
        for elemen in _tabla_paracargar:
            self.list_ctrl.InsertItem(index, elemen[0])
            total_elemen = len(elemen)
            for i in range((total_elemen)):
                self.list_ctrl.SetItem(index, i, str(elemen[i]))
            # the nex line is for work the auto list
            self.list_ctrl.SetItemData(index, index)
            #self.myRowDict[index] = elemen
            index += 1
        if _save: self.save_file_vm()
        self.count_str_vm.SetLabel('All VM: ' + str(len(self.tabla)))



    # Prepare menu about dialog click over VM machine in list ##############
    def onItemSelected(self, event):

        #localizamos el elemento seleccionado en el listado ordenado , y cargamos la fila
        if logger != None: logger.info('evento= '+ str(event.Index))
        self.posicionLista = event.Index
        self.listadoVM = []
        if logger != None: logger.info('datos en la fila= '+ str(self.list_ctrl.GetColumnCount()))
        for item_comlum in range(self.list_ctrl.GetColumnCount()):
            self.listadoVM.append(self.list_ctrl.GetItemText( self.posicionLista,item_comlum))
        if logger != None: logger.info( 'el otro ' + self.list_ctrl.GetItemText( self.posicionLista,1))
        if logger != None: logger.info( 'posicionlista= {} listadovm= {}'.format(self.posicionLista, self.listadoVM))

        #if not hasattr(self, "sshID"):
        self.info_vm = wx.NewId()
        self.event_vm = wx.NewId()
        self.graf_vm = wx.NewId()
        self.set_note = wx.NewId()
        self.sshID = wx.NewId()
        self.rdpID = wx.NewId()
        self.vmrcID = wx.NewId()
        self.htmlID = wx.NewId()
        self.html_id_ip = wx.NewId()
        self.separador = wx.NewId()
        self.softreboot = wx.NewId()
        self.softpoweroff = wx.NewId()
        self.reboot = wx.NewId()
        self.powerOn = wx.NewId()
        self.powerOff = wx.NewId()
        self.exitID = wx.NewId()
        self.Bind(wx.EVT_MENU, self.on_info, id=self.info_vm)
        self.Bind(wx.EVT_MENU, self.on_event, id=self.event_vm)
        self.Bind(wx.EVT_MENU, self.on_graf_vm, id=self.graf_vm)
        self.Bind(wx.EVT_MENU, self.on_set_note, id=self.set_note)
        self.Bind(wx.EVT_MENU, self.onSsh, id=self.sshID)
        self.Bind(wx.EVT_MENU, self.onRdp, id=self.rdpID)
        self.Bind(wx.EVT_MENU, self.on_vmrc, id=self.vmrcID)
        self.Bind(wx.EVT_MENU, self.onHtml, id=self.htmlID)
        self.Bind(wx.EVT_MENU, self.on_httml_ip, id=self.html_id_ip)
        self.Bind(wx.EVT_MENU, self.onsoftreboot, id=self.softreboot)
        self.Bind(wx.EVT_MENU, self.onsoftPowerOff, id=self.softpoweroff)
        self.Bind(wx.EVT_MENU, self.onreboot, id=self.reboot)
        self.Bind(wx.EVT_MENU, self.onpower_on, id=self.powerOn)
        self.Bind(wx.EVT_MENU, self.onpowerOff, id=self.powerOff)
        self.Bind(wx.EVT_MENU, self.onExit, id=self.exitID)

        # build the submenu-snapshot
        self.snapIDlist  = wx.NewId()
        self.snapIDcreate  = wx.NewId()
        self.snapIDmanager  = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onSnap_list, id=self.snapIDlist)
        self.Bind(wx.EVT_MENU, self.onSnap_create, id=self.snapIDcreate)
        self.Bind(wx.EVT_MENU, self.onSnap_manager, id=self.snapIDmanager)

        self.snap_menu=wx.Menu()
        item_snap_list = self.snap_menu.Append(self.snapIDlist, "List snapshot...")
        item_snap_create = self.snap_menu.Append(self.snapIDcreate, "Create snapshot...")
        item_snap_manager = self.snap_menu.Append(self.snapIDmanager, "Manager snapshot...")


        # build the menu
        self.menu = wx.Menu()
        item_info_vm = self.menu.Append(self.info_vm, "Info VM...")
        item_event_vm = self.menu.Append(self.event_vm, "Envents VM...")
        item_graf_vm = self.menu.Append(self.graf_vm, "Grafics VM...")
        item_set_note = self.menu.Append(self.set_note, "Set Note...")
        item_snap_menu = self.menu.Append(wx.ID_ANY,'Manager Snapshot', self.snap_menu)
        item_ssh = self.menu.Append(self.sshID, "Connection ssh")
        item_rdp = self.menu.Append(self.rdpID, "Connection rdp")
        item_vmrc = self.menu.Append(self.vmrcID, "Connection vmrc")
        item_html = self.menu.Append(self.htmlID, "Connection html")
        item_html_ip = self.menu.Append(self.html_id_ip, "Connect vm with web")
        item_separador = self.menu.AppendSeparator()
        item_soft_rebbot = self.menu.Append(self.softreboot, "Soft-reboot...")
        item_soft_rebbot = self.menu.Append(self.softpoweroff, "Soft-PowerOff...")
        item_reboot = self.menu.Append(self.reboot, "Reboot...")
        item_poweron = self.menu.Append(self.powerOn, "PowerOn...")
        item_poweroff = self.menu.Append(self.powerOff, "PowerOff...")
        item_separador = self.menu.AppendSeparator()
        item_exit = self.menu.Append(self.exitID, "Exit")



        # show the popup menu
        self.PopupMenu(self.menu)
        self.menu.Destroy()

    #########ADD the command to the events in the display dilog ######
    

    def on_info(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.on_info_vm(self, event, conexion, logger)
    
    def on_event(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.on_event_vm(self, event, conexion, logger)

    def on_graf_vm(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        manager_graf_vm.graf_vm(self, event, conexion, logger)
 
    def on_set_note(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.on_set_note(self, event, conexion, logger)
 
    def onSnap_list(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.onSnap_list(self, event, conexion, logger)
        
    def onSnap_create(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.onSnap_create(self, event, conexion, logger)
        #subproceso_snap = Thread(name='hilo', target=action_vm.onSnap_create, args=(self, event, conexion, logger,))
        #subproceso_snap.start()

    def onSnap_manager(self, event):
        menu = manager_snap.ManagerSnap(self, event, conexion, logger)
        del menu

    def onSsh(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        #global conexion
        #conexion = self.checking_conexion(conexion)
        #For connect with ssh is not use with "conexion"
        action_vm.onSsh(self, event, conexion, logger)
        
    def onRdp(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        #global conexion
        #conexion = self.checking_conexion(conexion)
        #For connect with ssh is not use with "conexion"
        action_vm.onRdp(self, event, conexion, logger)       

    def on_vmrc(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.on_vmrc(self, event, conexion, logger) 
 
    def onHtml(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.onHtml(self, event, conexion, logger)
    
    def on_httml_ip(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        #global conexion
        #conexion = self.checking_conexion(conexion)
        action_vm.on_httml_ip(self, event, conexion, logger)

    def onsoftreboot(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.onsoftreboot(self, event, conexion, logger)

    def onsoftPowerOff(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.onsoftPowerOff(self, event, conexion, logger)

    def onreboot(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.onreboot(self, event, conexion, logger)
        
    def onpower_on(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.onpower_on(self, event, conexion, logger)              

    def onpowerOff(self, event):
        # If past the timeout to connecto to vcenter or esxi you need reconnect one time more
        global conexion
        conexion = self.checking_conexion(conexion)
        action_vm.onpowerOff(self, event, conexion, logger)
        
    def onExit(self, event):
        """
        Exit program
        """
        self.Close()
        sys.exit(0)

    def checking_conexion(self, conexion):
        """
        Checking teh conexion is active with the vcenter or esxi

        :param conexion: The actual conexion to check it is alive.
        :return conexion: Retrun the actual or new conexion.

        """
        try:
            control = conexion.rootFolder.childEntity
            if logger != None: logger.info('connecting: {}'.format(conexion.rootFolder.childEntity))
            if logger != None: logger.info('connecting')
            return conexion
            
        except:
            if logger != None: logger.info('NOT connecting')
            conexion = connect_with_vcenter()
            return conexion


# #######################################################################
class MyFrame(wx.Frame):
    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY, "Intances VM")
        panel = MyPanel(self)
        self.Show()
    # ----------------------------------------------------------------------


# ######Display data for connet whit esxi an vcenter ######################

class DialogAcceso():
    def __init__(self):

        self.my_dialog_acceso_vcenter = dialogos.Dialogo_acceso_vcenter(None, -1, 'Data to connect')

        # precarga de fichero config
        self.cfg = wx.Config('appconfig')
        if self.cfg.Exists('vcenter'):
            self.my_dialog_acceso_vcenter.nombre_vcenter.SetValue(self.cfg.Read('vcenter'))
            self.my_dialog_acceso_vcenter.login_vcenter .SetValue(self.cfg.Read('login'))
            self.my_dialog_acceso_vcenter.passwor_vcenter .SetValue(self.cfg.Read('pwd'))
            self.my_dialog_acceso_vcenter.puert_vcenter.SetValue(self.cfg.Read('port'))

        else:
            self.my_dialog_acceso_vcenter.nombre_vcenter.SetValue(self.cfg.Read('Vcenter-name.host.com'))
            self.my_dialog_acceso_vcenter.login_vcenter.SetValue(self.cfg.Read('user@demo.local'))
            self.my_dialog_acceso_vcenter.passwor_vcenter.SetValue(self.cfg.Read('estanoes'))
            self.my_dialog_acceso_vcenter.puert_vcenter.SetValue(self.cfg.Read('443'))

        self.si = None



    def OnConnect(self):
        self.vcenter = self.my_dialog_acceso_vcenter.nombre_vcenter.GetValue()
        self.login = self.my_dialog_acceso_vcenter.login_vcenter.GetValue()
        self.pwd = self.my_dialog_acceso_vcenter.passwor_vcenter.GetValue()
        self.port = self.my_dialog_acceso_vcenter.puert_vcenter.GetValue()

        # wirte data  at config file fichero
        self.cfg.WriteInt('version', 1)
        self.cfg.Write('vcenter', self.vcenter)
        self.cfg.Write('login', self.login)
        self.cfg.Write('pwd', self.pwd)
        self.cfg.Write('port', self.port)


        # Acces to vcenter
        try:
            if not self.si:
                # [RFR] Changing way to create the ssl context as TLSv1.0 is disabled by VMware for vSphere 6.7 #315
                self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                self.context.verify_mode = ssl.CERT_NONE
                if logger != None: logger.info('vcenter:  ' + self.vcenter)

                self.si = SmartConnect(host=self.vcenter,
                                       user=self.login,
                                       pwd=self.pwd,
                                       port=int(self.port),
                                       sslContext=self.context,
                                       connectionPoolTimeout=0)

                #self.Close(True)

       
        except:
                dlgexcept = wx.MessageDialog(self.my_dialog_acceso_vcenter,
                                   "Error en Conexion o ya esta conectado Verifique parametros",
                                   caption= "Confirm Exit",
                                   style= wx.OK | wx.ICON_QUESTION)
                dlgexcept.ShowModal()
                dlgexcept.Destroy()
                if logger != None: logger.warning('Error en el acceso a vcenter')

            

    def OnDisConnect(self):
        if logger != None: logger.info('OUT Desconect')
        dlg = wx.MessageDialog(self.my_dialog_acceso_vcenter, 'Do you really want to close this application?',
                               'Confirm Exit', wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        # wx.MessageDialog()
        result = dlg.ShowModal()
        #dlg.Destroy()
        if result == wx.ID_OK:
            dlg.Destroy()
            sys.exit(0)



# ----------------------------------------------------------------------
# connect with Vcenter code and Dialog
def connect_with_vcenter():
        """
        Present a dialog box to get the data for conect to esxi or vcenter
        """

        dlgDialogo = DialogAcceso()

        while not dlgDialogo.si:
           result = dlgDialogo.my_dialog_acceso_vcenter.ShowModal()
           if result == wx.ID_OK:
               dlgDialogo.OnConnect()
               if dlgDialogo.si:
                   if logger != None: logger.info('conectado')
                   atexit.register(Disconnect, dlgDialogo.si)
                   content = dlgDialogo.si.RetrieveContent()
                   dlgDialogo.my_dialog_acceso_vcenter.Destroy()
                   return content
               else:
                    sys.exit(0)
           else:
               dlgDialogo.OnDisConnect()



# ----------------------------------------------------------------------
# Locate info about Machine MV
# ----------------------------------------------------------------------

def download_list_folder_and_vm(conexion):
    """
    Locate a vm in the vcenter or esxi  and chek if the the data
    agout vm  is corect or not.

    :param conexion: this is a connector with vcenter or exi
    :return serviores: A table with information with all VM 

    """
    condemore = conexion
    container = condemore.rootFolder  # starting point to look into
    viewType = [vim.VirtualMachine]  # object types to look for
    recursive = True  # whether we should look into it recursively
    containerView = condemore.viewManager.CreateContainerView(container, viewType, recursive)
    children = containerView.view
    
    # Calculate the max data to read to show process bar

    wait_cursor = wx.BusyCursor()
    max = len(children)
    if logger != None: logger.info('The max virtual machine: {}'.format(max))
    keepGoing = True
    count = 0
    dlg = wx.ProgressDialog("Loading Data Process",
                            "Loading VM data",
                            maximum = max,
                            #parent=-1,
                            #style = wx.PD_APP_MODAL
                            #| wx.PD_CAN_ABORT
                            #| wx.PD_ELAPSED_TIME
                            #| wx.PD_ESTIMATED_TIME
                            #| wx.PD_REMAINING_TIME
                            )
    keepGoing = dlg.Update(count)

    servidores = []
    for child in children:
        count += 1
        keepGoing = dlg.Update(count, "Loading")

        servidor = maquina.Maquina(child)
        servidores.append(servidor)
    dlg.Destroy()
    del wait_cursor
    
    return servidores









########################### Start the program  ####################
if __name__ == "__main__":

    def yes_no(answer):
        yes = set(['yes','y', 'ye', ''])
        no = set(['no','n'])

        while True:
            choice = input(answer).lower()
            if choice in yes:
               return True
            elif choice in no:
               return False
            else:
               print("Please respond with 'yes' or 'no'\n")

    def update_pyvmwareclient():
        try:
            from git import Repo
            repo_path = os.getcwd()
            repo = Repo(repo_path)
            print('Repo at {} Start loaded.'.format(repo_path))
            if logger != None: logger.info('Repo at {} Start loaded.'.format(repo_path))
            result=repo.git.pull()
            print('Repo at {} successfully loaded.'.format(repo_path))
            if logger != None: logger.info('Repo at {} successfully loaded.'.format(repo_path))
            print(result)
            if not result == 'Already up-to-date.':
                print('Program update, need rexecute program')
                if logger != None: logger.info('Program update, need rexecute program')
                sys.exit(0)
                
        except:
            print('Error: Can not update pyvmwareclient...')
            if logger != None: logger.info('Error: Can not update pyvmwareclient...')

    #parser    = argparse.ArgumentParser ( description= 'si pasamos a al aplicación --d tendremos debug' )
    #parser.add_argument('--d', action="store_true", help='imprimir informacion  debug')
    #args     =    parser.parse_args()


    # Use logger to control the activate log.
    logger = None
    #read inital config file

    if os.name == 'posix':
        logging.config.fileConfig('logging.conf')
        logger = logging.getLogger('pyvmwareclient')
        logger.info("# Start here a new loggin now")
        #pass
    
        #Update to last version pyvmwareclient
        """answer_yes_no =  yes_no('Can update pyvmware: [yes/no]')
        if answer_yes_no == True:
            update_pyvmwareclient()"""
 
        
    app = wx.App(False)
    ### -> if the app is loading at start the VM, you need uncomment the next line (you need uncomment another lines).
    #conexion = connect_with_vcenter()
    conexion = object
    frame = MyFrame()
    app.MainLoop()

    
