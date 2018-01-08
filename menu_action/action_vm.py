#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import sys
import os
import wx
import logging.config
from wxgladegen import dialogos
from pyVmomi import vim

__author__ = "Mario Ezquerro."


def on_info_vm(self, event, conexion, logger):
        fila = self.listadoVM
        print (self, event, conexion)
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
            
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        
        # List about vm detail in dialog box

        self.my_dialogo_texto = dialogos.Dialogo_texto(None, -1, 'Listados de datos VM')

        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        if logger != None: logger.info('informacion vm: '+ vm.summary.config.name)
        

        snaptexto ='\n Maquna vm = ' + fila[1] + '\n'

        snaptexto +="=====================\n"
        details = {'name': vm.summary.config.name,
                   'instance UUID': vm.summary.config.instanceUuid,
                   'bios UUID': vm.summary.config.uuid,
                   'path to VM': vm.summary.config.vmPathName,
                   'guest OS id': vm.summary.config.guestId,
                   'guest OS name': vm.summary.config.guestFullName,
                   'host name': vm.runtime.host.name,
                   'last booted timestamp': vm.runtime.bootTime}

        for name, value in details.items():
            snaptexto +=u"\n  {0:{width}{base}}: {1}".format(name, value, width=25, base='s')

        snaptexto += "\n------------------------------"
        snaptexto += "\nDevices:"
        snaptexto +="\n------------------------------\n"
        for device in vm.config.hardware.device:
            # diving into each device, we pull out a few interesting bits
            dev_details = {'key': device.key,
                           'summary': device.deviceInfo.summary,
                           'device type': type(device).__name__,
                           'backing type': type(device.backing).__name__}

            snaptexto +="\n------------------\n"
            snaptexto +=u"\n  label: {0}".format(device.deviceInfo.label)

            for name, value in dev_details.items():
                snaptexto +=u"\n    {0:{width}{base}}: {1}".format(name, value, width=15, base='s')

            if device.backing is None:
                continue

            # the following is a bit of a hack, but it lets us build a summary
            # without making many assumptions about the backing type, if the
            # backing type has a file name we *know* it's sitting on a datastore
            # and will have to have all of the following attributes.
            if hasattr(device.backing, 'fileName'):
                datastore = device.backing.datastore
                if datastore:
                    snaptexto +="    datastore\n"
                    snaptexto +="        name: {0}\n".format(datastore.name)
                    # there may be multiple hosts, the host property
                    # is a host mount info type not a host system type
                    # but we can navigate to the host system from there
                    for host_mount in datastore.host:
                        host_system = host_mount.key
                        snaptexto +=u"\n        host: {0}".format(host_system.name)
                    snaptexto +="        summary"
                    summary = {'capacity': datastore.summary.capacity,
                               'freeSpace': datastore.summary.freeSpace,
                               'file system': datastore.summary.type,
                               'url': datastore.summary.url}
                    for key, val in summary.items():
                        snaptexto +=(u"\n            {0}: {1}".format(key, val))
                snaptexto +=(u"\n    fileName: {0}".format(device.backing.fileName))
                snaptexto +=(u"\n    device ID: {0}".format(device.backing.backingObjectId))

            snaptexto +="\n--------------------------------------------\n"

        snaptexto += "====================="
        self.my_dialogo_texto.salida_texto.SetValue(snaptexto)
        result = self.my_dialogo_texto.ShowModal() # pintamos la ventana con la informcion
        self.my_dialogo_texto.Destroy()






def on_set_note(self, event, conexion, logger):
        fila = self.listadoVM
        for i in range(len(fila)):
                if logger != None: logger.info(fila[i])
        # At tree elemente are the name and the nine at the UUID

        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)

        self.my_dialogo_ssh = dialogos.Dialogo_user_pass(None, -1, 'New Note in: {0}' .format(vm.name))
        punteromaquina = vim.vm.ConfigSpec()

        # the actual file 8 is the Note

        self.my_dialogo_ssh.usuario.SetValue('{0}' .format(fila[7]) )


        result = self.my_dialogo_ssh.ShowModal() # pintamos la ventan con la informcion
        if result == wx.ID_OK:
                punteromaquina.annotation = str( self.my_dialogo_ssh.usuario.GetValue())
                task = vm.ReconfigVM_Task(punteromaquina)
                tasks.wait_for_tasks(conexion, [task])
        self.my_dialogo_ssh.Destroy()




def onSnap_list(self, event, conexion, logger):
        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        
        #listado de snapshot en una ventana emergente

        self.my_dialogo_texto = dialogos.Dialogo_texto(None, -1, 'Listados de Snapshots')
        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        snap_info = vm.snapshot
        self.my_dialogo_texto.salida_texto.SetValue('Maquna vm = ' + fila[1]  )
        snaptexto = 'Listado de snapshot \n'
        if not snap_info:
            self.my_dialogo_texto.salida_texto.SetValue('No hay snapshot')
            if logger != None: logger.info ('No hay snapshot')
        else:
            tree = snap_info.rootSnapshotList
            while tree[0].childSnapshotList is not None:
                snaptexto = snaptexto +  ("Nombre Snap: {0} = description> {1}  \n".format(tree[0].name, tree[0].description))
                if logger != None: logger.info("Snap: {0} => {1}".format(tree[0].name, tree[0].description))
                if len(tree[0].childSnapshotList) < 1:
                    break
                tree = tree[0].childSnapshotList
            self.my_dialogo_texto.salida_texto.SetValue(snaptexto)

        result = self.my_dialogo_texto.ShowModal() # pintamos la ventana con la informcion
        self.my_dialogo_texto.Destroy()


def onSnap_create(self, event, conexion, logger):

        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        #Dialogo para pedir datos para el snapshop......

        self.my_dialogo_sanshot = dialogos.Dialog_snapshot(None, -1, 'Propiedades Snapshot')

        self.my_dialogo_sanshot.nombre_snap.SetValue(fila[1] + ' Razon del snapshot? ...' )
        result = self.my_dialogo_sanshot.ShowModal()

        nombre = str(self.my_dialogo_sanshot.nombre_snap.GetValue())
        descricion = str(self.my_dialogo_sanshot.descripcion_snap.GetValue())
        checkbox_memory=self.my_dialogo_sanshot.checkbox_memory.GetValue()
        checkbox_quiesce=self.my_dialogo_sanshot.checkbox_quiesce.GetValue()


        self.my_dialogo_sanshot.Destroy()
        #if logger != None: logger.info ('resultado = ' + str(result))
        #if logger != None: logger.info('wx.ID_OK = ' + str(wx.ID_OK))

        """dlg_reset = wx.MessageDialog(self,
                                     "¿Hacer snapshot de : ? \n " + fila[1] + " ",
                                     "Confirm Exit",
                                     wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg_reset.ShowModal()
        dlg_reset.Destroy()"""

        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        if result == wx.ID_OK:
            if  vm  is not None:
                if logger != None: logger.info ("The current powerState is: {0}".format(vm.runtime.powerState))
                TASK = task = vm.CreateSnapshot_Task(nombre, description = descricion, memory=checkbox_memory, quiesce=checkbox_quiesce)
                #contador de tareas
                count = 0
                #state_task= task.info.state
                while task.info.state != vim.TaskInfo.State.success:
                    if logger != None: logger.info('Running => {0}  state: {1} info.result = {2}'.format(count, task.info.state, task.info.result))
                    count += 1

                #tasks.wait_for_tasks(conexion, [TASK])
                if logger != None: logger.info("Snapshot Completed.")

        #listado de snapshot en una ventana emergente

        self.my_dialogo_texto = dialogos.Dialogo_texto(None, -1, 'Listados de Snapshots')

        del vm
        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        snap_info = vm.snapshot
        self.my_dialogo_texto.salida_texto.SetValue('Maquna vm = ' + fila[1]  )
        snaptexto = 'Listado de snapshot \n'
        if not snap_info:
            self.my_dialogo_texto.salida_texto.SetValue('No hay snapshot')
            if logger != None: logger.info ('No hay snapshot')
        else:
            tree = snap_info.rootSnapshotList
            while tree[0].childSnapshotList is not None:
                snaptexto = snaptexto +  ("Nombre Snap: {0} = description> {1}  \n".format(tree[0].name, tree[0].description))
                if logger != None: logger.info("Snap: {0} => {1}".format(tree[0].name, tree[0].description))
                if len(tree[0].childSnapshotList) < 1:
                    break
                tree = tree[0].childSnapshotList
            self.my_dialogo_texto.salida_texto.SetValue(snaptexto)

        result = self.my_dialogo_texto.ShowModal() # pintamos la ventana con la informcion
        self.my_dialogo_texto.Destroy()


def onSsh(self, event, conexion, logger):
        if sys.platform == 'darwin':
            fila = self.listadoVM
            for i in range(len(fila)):
                if logger != None: logger.info(fila[i])
            # El tercer elemento es la ip es decier la fila[2]
            self.my_dialogo_ssh = dialogos.Dialogo_user_pass(None, -1, 'Ususario y password')
            self.my_dialogo_ssh.usuario.SetValue('root' )
            result = self.my_dialogo_ssh.ShowModal() # pintamos la ventan con la informcion
            if result == wx.ID_OK:
                comando = 'ssh ' + fila[2] +'@'+ str(self.my_dialogo_ssh.usuario.GetValue()) + ' &'
                os.system(comando)
            self.my_dialogo_ssh.Destroy()

        if os.name == 'nt' or os.name == 'posix':
            fila = self.listadoVM
            for i in range(len(fila)):
                if logger != None: logger.info(fila[i])
            # El tercer elemento es la ip es decier la fila[2]
            self.my_dialogo_ssh = dialogos.Dialogo_user_pass(None, -1, 'Ususario y password')
            self.my_dialogo_ssh.usuario.SetValue('root')
            result = self.my_dialogo_ssh.ShowModal()  # pintamos la ventan con la informcion
            if result == wx.ID_OK:
                comando = 'putty ' + fila[2] + ' -l ' + str(self.my_dialogo_ssh.usuario.GetValue()) + ' &'
                os.system(comando)
            self.my_dialogo_ssh.Destroy()



