#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""
Actions to make at the menu

"""

import sys
import os
import wx
import ssl
import OpenSSL
import webbrowser
import logging.config
#import wx.lib.mixins.listctrl as listmix
from wxgladegen import dialogos
from pyVmomi import vim

__author__ = "Mario Ezquerro."

__all__ = [
    'onSnap_manager',
]



class ManagerSnap():

    def __init__(self, self_panel, event, conexion, logger):
        """Constructor"""

        self_panel.event = event
        self.conexion = conexion
        self.logger = logger
        self_panel.vim = vim

        

        self.my_dialogo_list = dialogos.Dialog_list(None, -1, 'Snapshots List')
        name_rows = ['VM Name', 'Name Snap', 'Description', 'Create time', 'State']
        # cargamos los nombres de los elementos
        for i in range(len(name_rows)):
            self.my_dialogo_list.list_ctrl_basic.InsertColumn(i, name_rows[i])

        self.fila = self_panel.listadoVM
        for i in range(len(self.fila)):
            if self.logger != None: self.logger.info(self.fila[i])
        self.vm = self.conexion.searchIndex.FindByUuid(None,self.fila[8], True)
        self.snap_info = self.vm.snapshot

        index = 0

        
           
        if not self.snap_info:
            self.my_dialogo_list.list_ctrl_basic.InsertItem(index, self.fila[1])
            self.my_dialogo_list.list_ctrl_basic.SetItem(index, 1, 'Not snapshot')
            if self.logger != None: self.logger.info ('Not snapshot')
        else:
            self.tree = self.snap_info.rootSnapshotList
            while self.tree[0].childSnapshotList is not None:
                self.my_dialogo_list.list_ctrl_basic.InsertItem(index, self.fila[1])
                self.my_dialogo_list.list_ctrl_basic.SetItem(index, 1, str(self.tree[0].name))
                self.my_dialogo_list.list_ctrl_basic.SetItem(index, 2, str(self.tree[0].description))
                self.my_dialogo_list.list_ctrl_basic.SetItem(index, 3, str(self.tree[0].createTime))
                self.my_dialogo_list.list_ctrl_basic.SetItem(index, 4, str(self.tree[0].state))              
                # next line is for pertmit auto menu ordenate
                self.my_dialogo_list.list_ctrl_basic.SetItemData(index, index)
                if self.logger != None: self.logger.info("Snap: {0} => {1}".format(self.tree[0].name, self.tree[0].description))
                if len(self.tree[0].childSnapshotList) < 1:
                    break
                self.tree = self.tree[0].childSnapshotList
                index += 1

        self.my_dialogo_list.list_ctrl_basic.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_snap_selected, self.my_dialogo_list.list_ctrl_basic)
        result = self.my_dialogo_list.ShowModal() # pintamos la ventana con la informcion

        self.my_dialogo_list.Destroy()

    def on_snap_selected(self, event2):
        #localizamos el elemento seleccionado en el listado ordenado , y cargamos la fila
        
        self.list_position = event2.Index
        #print ('posicion en lista ' + str(self.list_position))
        #print(self.my_dialogo_list.list_ctrl_basic.GetItemText(list_position, 1))
        self.separador = wx.NewId()
        self.delete_snap = wx.NewId()
        self.rebert_snap = wx.NewId()
        self.my_dialogo_list.Bind(wx.EVT_MENU, self.on_delete_snap, id=self.delete_snap)
        self.my_dialogo_list.Bind(wx.EVT_MENU, self.on_rebert_snap, id=self.rebert_snap)
        # build the menu
        self.menu_snap = wx.Menu()
        item_snap_delete = self.menu_snap.Append(self.delete_snap, "Delete_snap...")
        item_snap_delete = self.menu_snap.Append(self.rebert_snap, "Rebert_snap...")
        self.my_dialogo_list.PopupMenu(self.menu_snap)
        self.menu_snap.Destroy()

    def on_delete_snap(self, event3):

        #print( 'eliminando snapshot')
        #print(str(self.vm))
        #print('Mv name {}'.format(self.fila[1]))

        list_position1 = self.list_position
        snapshot_name = self.my_dialogo_list.list_ctrl_basic.GetItemText(list_position1, 1)
        tree_snapshot = self.tree
        #print(str(list_position1))
        #print(snapshot_name)

        if self.my_dialogo_list.list_ctrl_basic.GetItemText(list_position1, 1 ) == 'Not snapshot':
                self.dlg_info = wx.MessageDialog(None,
                                     'Not sanpshot at: {} \n'.format(self.fila[1]) +'Snapshot name: {}'.format(snapshot_name),
                                     'Snapshot name: {}'.format(snapshot_name),
                                     wx.OK )
                self.result_dlg_info= self.dlg_info.ShowModal()
                self.dlg_info.Destroy()

        else:

                self.dlg_reset = wx.MessageDialog(None,
                                     'Delete Snapshot from VM: {} \n'.format(self.fila[1]) +'Snapshot name: {}'.format(snapshot_name),
                                     'Snapshot name: {}'.format(snapshot_name),
                                     wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                self.result = self.dlg_reset.ShowModal()
                self.dlg_reset.Destroy()

                # Window progress task
                keepGoing = True
                dlg_process = wx.ProgressDialog("Process Delete snapshot ",
                            "Task process",
                            maximum = 100, )
                keepGoing = dlg_process.Update(0)

                if self.result == wx.ID_OK:
                    if  self.vm  is not None:
                       
                        wait_cursor = wx.BusyCursor()
                        #print(self.vm.snapshot.rootSnapshotList)
                        locate_snap_in_tree = self.vm.snapshot.rootSnapshotList    
                        while locate_snap_in_tree[0].childSnapshotList is not None:    
                                if self.logger != None: self.logger.info('locate name snapshot to delete:' + locate_snap_in_tree[0].name )  
                                if self.logger != None: self.logger.info('ID snapshot delete {}'.format(locate_snap_in_tree[0].snapshot))

                                if  snapshot_name == locate_snap_in_tree[0].name:
                                    snapshot_eliminar = locate_snap_in_tree[0].snapshot
                                    print (snapshot_eliminar)
                                    if self.logger != None: self.logger.info ("The current powerState is: {0}".format(self.vm.runtime.powerState))
                                    TASK = task = snapshot_eliminar.RemoveSnapshot_Task(removeChildren=False, consolidate=False)
                                    state_task= task.info.state
                                    while task.info.state != vim.TaskInfo.State.success:
                                        #if logger != None: logger.info('Running => {0}  state: {1} info.result = {2}'.format(count, task.info.state, task.info.result))
                                        #if logger != None: logger.info('Running => {0}  %'.format(task.info.progress))
                                        try:
                                            porcentage = int(task.info.progress)
                                        except:
                                            pass

                                        else:   
                                            keepGoing = dlg_process.Update(porcentage, "Snapshot {}%".format(porcentage))

                                if len(locate_snap_in_tree[0].childSnapshotList) < 1:
                                    break
                                locate_snap_in_tree = locate_snap_in_tree[0].childSnapshotList

                        #tasks.wait_for_tasks(conexion, [TASK])
                    if self.logger != None: self.logger.info("Snapshot Delete Completed.")
                    del wait_cursor
                    del self.vm
                    self.my_dialogo_list.Destroy()

                dlg_process.Destroy()

    def on_rebert_snap(self, event3):
        pass
        #listado de snapshot en una ventana emergente

        #self.my_dialogo_texto = dialogos.Dialogo_texto(None, -1, 'Listados de Snapshots')

        
        #self.vm = self.conexion.searchIndex.FindByUuid(None,self.fila[8], True)
        #snap_info = self.vm.snapshot


        #Show the actual state snapshot
        #onSnap_list(self, event, self.conexion, self.logger)
