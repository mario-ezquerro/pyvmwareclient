#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import wx
import wx.lib.mixins.listctrl as listmix
import atexit
import ssl
import os
import re
import OpenSSL
import webbrowser
import logging.config
# import argparse
import sys
import wx.lib.inspection
from wxgladegen import dialogos
from pyVim.connect import SmartConnect, Disconnect
from tools import tasks
from tools import vm
from pyVmomi import vim
#from tools import virtual_machine_device_info as vminfo


class theListCtrl(wx.ListCtrl):
    # ----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)


########################################################################



class MyPanel(wx.Panel, listmix.ColumnSorterMixin):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        # self.Bind(wx.EVT_BUTTON, self.OnSelectFont, btn)

        self.list_ctrl = theListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.SUNKEN_BORDER)
        st1 = wx.StaticText(self, label=' Cadena Busqueda')
        self.cadenaBusqueda = wx.TextCtrl(self)
        btnbusqueda = wx.Button(self, label="Buscar")
        btnrecargaVM = wx.Button(self, label="Actualizar VM")

        name_rows = ['Carpeta', 'Nombre', 'IP', 'Estado', 'pregunta', 'Disco Path', 'Sistema', 'Notas', 'uuid']

        # cargamos los nombres de los elementos
        for x in range(len(name_rows)):
            self.list_ctrl.InsertColumn(x, name_rows[x])

        # conexion = conectar_con_vcenter(self, id)
        self.tabla = []
        self.tabla = sacar_listado_capertas(conexion)
        self.vm_buscados = []

        self.cargardatos_en_listctrl(self.tabla)

        # para la ordenacion--- llama a Getlistctrl
        self.itemDataMap = self.tabla
        listmix.ColumnSorterMixin.__init__(self, len(name_rows))
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self.list_ctrl)
        # self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onItemSelected, self.list_ctrl)

        # Metemos las cosas en le ventana en orden
        txtcontador = wx.StaticText(self, label='total VM: ' + str(len(self.tabla)))
        sizer = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(st1, wx.ALL | wx.ALIGN_CENTER, 5)
        hbox1.Add(self.cadenaBusqueda, wx.ALL | wx.ALIGN_CENTER, 5)
        hbox1.Add(btnbusqueda, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)
        hbox1.Add(btnrecargaVM, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)
        hbox1.Add(txtcontador, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_CENTER, border=2)
        self.Bind(wx.EVT_BUTTON, self.busquedadatos, btnbusqueda)
        self.Bind(wx.EVT_BUTTON, self.recarga_VM, btnrecargaVM)

        sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        # tools for search an debug (to use uncomment the next line, works only linux)
        # wx.lib.inspection.InspectionTool().Show()

    # ----------------------------------------------------------------------
    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.list_ctrl

    # buscamos un string en el nombre de las VM y lo pintamos de amarillo
    # si habia antes algo de amarillo lo ponemos blanco
    def busquedadatos(self, event):

        parabuscar = self.cadenaBusqueda.GetValue()
        if parabuscar:
            i = self.list_ctrl.GetItemCount() - 1
            while i >= 0 :
                if re.search(parabuscar, self.list_ctrl.GetItemText(i, col=1)):
                    self.list_ctrl.SetItemBackgroundColour(i, 'yellow')
                else:
                    self.list_ctrl.DeleteItem(i)
                i -= 1
        else:
            self.cargardatos_en_listctrl(self.tabla)

    def recarga_VM(self, event):
        # conexion = conectar_con_vcenter(self, id)
        self.tabla = []
        self.tabla = sacar_listado_capertas(conexion)
        self.vm_buscados = []



        #sacar datos acerca de vcenter.
        object_about = conexion.about
        """for obj in object_view.view:
            print(obj)
            if isinstance(obj, vim.VirtualMachine):
                vm.print_vm_info(obj)"""
        print (object_about)
        print(object_about.version)

        object_view = conexion.viewManager.CreateContainerView(conexion.rootFolder, [], True)
        for obj in object_view.view:
            print(obj)
            if isinstance(obj, vim.HostSystem):
                    print("El host es: " + obj.name)

        object_view.Destroy()




        if logger != None: logger.info("Reload of VM: {0}".format(self.tabla))

        self.cargardatos_en_listctrl(self.tabla)




    def cargardatos_en_listctrl(self, _tabla_paracargar):
        # cargamos las busquedas en el listado de tablas.
        self.myRowDict = {}
        index = 0
        for elemen in _tabla_paracargar:
            self.list_ctrl.InsertItem(index, elemen[0])
            total_elemen = len(elemen)
            for i in range(total_elemen):
                self.list_ctrl.SetItem(index, i, elemen[i])
            self.list_ctrl.SetItemData(index, index)
            self.myRowDict[index] = elemen
            index += 1



    # Cuando selecionamos una fila activamos el menu de contexto##############
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

        if not hasattr(self, "sshID"):
            self.info_vm = wx.NewId()
            self.sshID = wx.NewId()
            self.htmlID = wx.NewId()
            self.rdpID = wx.NewId()
            self.separador = wx.NewId()
            self.softreboot = wx.NewId()
            self.softpoweroff = wx.NewId()
            self.reboot = wx.NewId()
            self.powerOn = wx.NewId()
            self.powerOff = wx.NewId()
            self.exitID = wx.NewId()
            self.Bind(wx.EVT_MENU, self.on_info_vm, id=self.info_vm)
            self.Bind(wx.EVT_MENU, self.onSsh, id=self.sshID)
            self.Bind(wx.EVT_MENU, self.onHtml, id=self.htmlID)
            self.Bind(wx.EVT_MENU, self.onRdp, id=self.rdpID)
            self.Bind(wx.EVT_MENU, self.onsoftreboot, id=self.softreboot)
            self.Bind(wx.EVT_MENU, self.onsoftPowerOff, id=self.softpoweroff)
            self.Bind(wx.EVT_MENU, self.onreboot, id=self.reboot)
            self.Bind(wx.EVT_MENU, self.onpower_on, id=self.powerOn)
            self.Bind(wx.EVT_MENU, self.onpowerOff, id=self.powerOff)
            self.Bind(wx.EVT_MENU, self.onExit, id=self.exitID)

        # build the submenu-snapshot
        self.snapIDlist  = wx.NewId()
        self.snapIDcreate  = wx.NewId()
        self.Bind(wx.EVT_MENU, self.onSnap_list, id=self.snapIDlist)
        self.Bind(wx.EVT_MENU, self.onSnap_create, id=self.snapIDcreate)

        self.snap_menu=wx.Menu()
        item_snap_list = self.snap_menu.Append(self.snapIDlist, "List snapshot...")
        item_snap_create = self.snap_menu.Append(self.snapIDcreate, "Create snapshot...")


        # build the menu
        self.menu = wx.Menu()
        item_info_vm = self.menu.Append(self.info_vm, "Info VM...")
        item_snap_menu = self.menu.Append(wx.ID_ANY,'Manager Snapshot', self.snap_menu)
        item_ssh = self.menu.Append(self.sshID, "Conexión ssh")
        item_html = self.menu.Append(self.htmlID, "Conexión html")
        item_rdp = self.menu.Append(self.rdpID, "conexión rdp")
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

    #########Evetnto del menu de contexto sobre maquina VM ######




    def on_info_vm(self, event):
        fila = self.listadoVM
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


    def onSnap_list(self, event):
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


    def onSnap_create(self, event):
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
                tasks.wait_for_tasks(conexion, [TASK])
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




    def onSsh(self, event):
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



    def onHtml(self, event):
        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El tercer elemento es la ip y el 9 es el UUID
        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        vm_name = vm.summary.config.name
        vm_moid = vm._moId
        if logger != None: logger.info('void= '.format(vm_moid))
        vcenter_data = conexion.setting
        vcenter_settings = vcenter_data.setting
        console_port = '9443'
        puerto_vcenter= '443'

        for item in vcenter_settings:
            key = getattr(item, 'key')
            #print ('key: ' + key + ' =>'+ str(getattr(item, 'value')))
            if key == 'VirtualCenter.FQDN':
                vcenter_fqdn = getattr(item, 'value')
                #if key == 'WebService.Ports.https':
                #console_port = str(getattr(item, 'value'))

        host = vcenter_fqdn

        session_manager = conexion.sessionManager
        session = session_manager.AcquireCloneTicket()
        vc_cert = ssl.get_server_certificate((host, int(puerto_vcenter)))
        vc_pem = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,vc_cert)
        vc_fingerprint = vc_pem.digest('sha1')

        if logger != None: logger.info("Open the following URL in your browser to access the " \
                                       "Remote Console.\n" \
                                       "You have 60 seconds to open the URL, or the session" \
                                       "will be terminated.\n")
        print(str(vcenter_data))

        # Locate the version of vcenter the object .version for locate the version of vcenter
        object_about = conexion.about
        #For version vcenter 5.5
        if object_about.version == '5.5.0':
            console_portv5 = '7331'
            URL5 = "http://" + host + ":" + console_portv5 + "/console/?vmId=" \
                   + str(vm_moid) + "&vmName=" + vm_name + "&host=" + vcenter_fqdn \
                   + "&sessionTicket=" + session + "&thumbprint=" + vc_fingerprint.decode('utf8')
            webbrowser.open(URL5, new=1, autoraise=True)

        #For version vcenter 6.0 and 6.5
        if object_about.version == '6.0.0' or object_about.version == '6.5.0':
            URL = "https://" + host + ":" + console_port + "/vsphere-client/webconsole.html?vmId=" \
                  + str(vm_moid) + "&vmName=" + vm_name + "&host=" + vcenter_fqdn \
                  + "&sessionTicket=" + session + "&thumbprint.info=" + vc_fingerprint.decode('utf-8')
            if logger != None: logger.info(URL)
            webbrowser.open(URL, new=1, autoraise=True)
            if logger != None: logger.info ("Waiting for 60 seconds, then exit")


    def onRdp(self, event):
        if sys.platform == 'darwin':
            fila = self.listadoVM
            for i in range(len(fila)):
                if logger != None: logger.info(fila[i])
            # El tercer elemento es la ip es decier la fila[2]
            ruta_fichero_config = os.getcwd()
            archConfiguracion = open('conexion.rdp', 'w')
            archConfiguracion.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">' + '\n')
            archConfiguracion.write('<plist version="1.0">' + '\n')
            archConfiguracion.write('<dict>' + '\n')
            archConfiguracion.write('<key>AddToKeychain</key>' + '\n')
            archConfiguracion.write('<true/>' + '\n')
            archConfiguracion.write('<key>ApplicationPath</key>' + '\n')
            archConfiguracion.write('<string></string>' + '\n')
            archConfiguracion.write('<key>AudioRedirectionMode</key>' + '\n')
            archConfiguracion.write('<integer>0</integer>' + '\n')
            archConfiguracion.write('<key>AuthenticateLevel</key>' + '\n')
            archConfiguracion.write('<integer>0</integer>' + '\n')
            archConfiguracion.write('<key>AutoReconnect</key>' + '\n')
            archConfiguracion.write('<true/>' + '\n')
            archConfiguracion.write('<key>BitmapCaching</key>' + '\n')
            archConfiguracion.write('<true/>' + '\n')
            archConfiguracion.write('<key>ColorDepth</key>' + '\n')
            archConfiguracion.write('<integer>1</integer>' + '\n')
            archConfiguracion.write('<key>ConnectionString</key>' + '\n')
            archConfiguracion.write('<string>' + fila[2] + '</string>' + '\n')
            archConfiguracion.write('<key>DesktopSize</key>' + '\n')
            archConfiguracion.write('' + '\n')
            archConfiguracion.write('' + '\n')
            archConfiguracion.write('' + '\n')
            archConfiguracion.write('' + '\n')
            archConfiguracion.write('</dict>' + '\n')
            archConfiguracion.write('</plist>' + '\n')
            archConfiguracion.close
            comando = 'open -a \"Remote Desktop Connection.app\" ' + ruta_fichero_config +'/conexion.rdp' + ' &'
            os.system(comando)

        if os.name == 'nt':
            fila = self.listadoVM
            for i in range(len(fila)):
                if logger != None: logger.info(fila[i])
            # El tercer elemento es la ip es decier la fila[2]
            comando = 'mstsc ' +'/v:'+ fila[2]
            os.system(comando)

        if os.name == 'posix':
            fila = self.listadoVM
            for i in range(len(fila)):
                if logger != None: logger.info(fila[i])
            # El tercer elemento es la ip osea la fila 2
            ruta_fichero_config = os.getcwd()
            archConfiguracion = open('remminaconfig.remmina','w')
            archConfiguracion.write('[remmina]' + '\n')
            archConfiguracion.write('disableclipboard=0' + '\n')
            archConfiguracion.write('ssh_auth=0' + '\n')
            archConfiguracion.write('clientname=' + '\n')
            archConfiguracion.write('quality=0' + '\n')
            archConfiguracion.write('ssh_charset=' + '\n')
            archConfiguracion.write('ssh_privatekey=' + '\n')
            archConfiguracion.write('sharesmartcard=0' + '\n')
            archConfiguracion.write('resolution=' + '\n')
            archConfiguracion.write('group=' + '\n')
            archConfiguracion.write('password=' + '\n')
            archConfiguracion.write('name=' + fila[1] + '\n')
            archConfiguracion.write('ssh_loopback=0' + '\n')
            archConfiguracion.write('sharelogger.infoer=0' + '\n')
            archConfiguracion.write('ssh_username=' + '\n')
            archConfiguracion.write('ssh_server=' + '\n')
            archConfiguracion.write('security=' + '\n')
            archConfiguracion.write('protocol=RDP' + '\n')
            archConfiguracion.write('execpath=' + '\n')
            archConfiguracion.write('sound=off' + '\n')
            archConfiguracion.write('exec=' + '\n')
            archConfiguracion.write('ssh_enabled=0' + '\n')
            archConfiguracion.write('username=' + '\n')
            archConfiguracion.write('sharefolder=' + '\n')
            archConfiguracion.write('console=0' + '\n')
            archConfiguracion.write('domain=' + '\n')
            archConfiguracion.write('server=' +fila[2] + '\n')
            archConfiguracion.write('colordepth=24' + '\n')
            archConfiguracion.write('window_maximize=0' + '\n')
            archConfiguracion.write('window_height=' + '\n')
            archConfiguracion.write('window_width=' + '\n')
            archConfiguracion.write('viewmode=1' + '\n')
            archConfiguracion.write('scale=1' + '\n')
            archConfiguracion.close
            comando = 'remmina -c ' + ruta_fichero_config +'/remminaconfig.remmina' + ' &'
            os.system(comando)



# url del VMRC https://www.vmware.com/go/download-vmrc

    def onsoftreboot(self, event):
        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        #Pedimos confirmacion del reset de la mv con ventana dialogo
        dlg_reset = wx.MessageDialog(self,
                                     "Estas a punto de reiniciar \n " + fila[1] + " ",
                                     "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg_reset.ShowModal()
        dlg_reset.Destroy()

        if result == wx.ID_OK:
            vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
            if  vm  is not None:

                if logger != None: logger.info ("The current powerState is: {0}".format(vm.runtime.powerState))
                TASK = vm.RebootGuest()
                #Este da error tasks.wait_for_tasks(conexion, [TASK])
                if logger != None: logger.info("Soft reboot its done.")

    def onsoftPowerOff(self, event):
        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        #Pedimos confirmacion del reset de la mv con ventana dialogo
        dlg_reset = wx.MessageDialog(self,
                                     "Estas a punto de Soft Apagar \n " + fila[1] + " ",
                                     "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg_reset.ShowModal()
        dlg_reset.Destroy()

        if result == wx.ID_OK:
            vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
            if  vm  is not None:

                if logger != None: logger.info ("The current powerState is: {0}".format(vm.runtime.powerState))
                TASK = vm.ShutdownGuest()
                #Este da error tasks.wait_for_tasks(conexion, [TASK])
                if logger != None: logger.info("Soft poweroff its done.")

    # Reiniciamos el ordenador seleccionado en el menu contextual
    def onreboot(self, event):
        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        #Pedimos confirmacion del reset de la mv con ventana dialogo
        dlg_reset = wx.MessageDialog(self,
                                     "Estas a punto de reiniciar \n " + fila[1] + " ",
                                     "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg_reset.ShowModal()
        dlg_reset.Destroy()

        if result == wx.ID_OK:
            vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
            if  vm  is not None:

                if logger != None: logger.info ("The current powerState is: {0}".format(vm.runtime.powerState))
                TASK = vm.ResetVM_Task()
                tasks.wait_for_tasks(conexion, [TASK])
                if logger != None: logger.info("reboot its done.")

    def onpower_on(self, event):
        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        #Pedimos confirmacion del poweron de la mv con ventana dialogo
        dlg_reset = wx.MessageDialog(self,
                                     "Estas a punto de iniciar \n " + fila[1] + "\nAhora esta:  " + fila[3],
                                     "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg_reset.ShowModal()
        dlg_reset.Destroy()

        if result == wx.ID_OK:
            vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
            if  vm  is not None and not vm.runtime.powerState == 'poweredOn':
                if logger != None: logger.info ("The current powerState is: {0}".format(vm.runtime.powerState))
                TASK = vm.PowerOn()
                tasks.wait_for_tasks(conexion, [TASK])
                if logger != None: logger.info("Power ON  its done.")

    def onpowerOff(self, event):
        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        #Pedimos confirmacion del reset de la mv con ventana dialogo
        dlg_reset = wx.MessageDialog(self,
                                     "Estas a punto de Apagar \n " + fila[1] + " ",
                                     "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg_reset.ShowModal()
        dlg_reset.Destroy()

        if result == wx.ID_OK:
            vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
            if  vm  is not None and not vm.runtime.powerState == 'poweredOff':
                if logger != None: logger.info ("The current powerState is: {0}".format(vm.runtime.powerState))
                TASK = vm.PowerOff()
                tasks.wait_for_tasks(conexion, [TASK])
                if logger != None: logger.info("Power OFF its done.")

    def onExit(self, event):
        """
        Exit program
        """
        self.Close()
        sys.exit(0)


# #######################################################################
class MyFrame(wx.Frame):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY, "Maquinas VM")
        panel = MyPanel(self)
        self.Show()

        # ----------------------------------------------------------------------


# ######Pantalla para el Dialogo de acceso a vcenter######################

class DialogAcceso():
    def __init__(self):

        self.my_dialog_acceso_vcenter = dialogos.Dialogo_acceso_vcenter(None, -1, 'Datos de conexión')

        # precarga de fichero config
        self.cfg = wx.Config('appconfig')
        if self.cfg.Exists('vcenter'):
            self.my_dialog_acceso_vcenter.nombre_vcenter.SetValue(self.cfg.Read('vcenter'))
            self.my_dialog_acceso_vcenter.login_vcenter .SetValue(self.cfg.Read('login'))
            self.my_dialog_acceso_vcenter.passwor_vcenter .SetValue(self.cfg.Read('pwd'))
            self.my_dialog_acceso_vcenter.puert_vcenter.SetValue(self.cfg.Read('port'))

        else:
            self.my_dialog_acceso_vcenter.nombre_vcenter.SetValue(self.cfg.Read('vcenter.host.com'))
            self.my_dialog_acceso_vcenter.login_vcenter.SetValue(self.cfg.Read('usuario@dominio.es'))
            self.my_dialog_acceso_vcenter.passwor_vcenter.SetValue(self.cfg.Read('estanoes'))
            self.my_dialog_acceso_vcenter.puert_vcenter.SetValue(self.cfg.Read('443'))

        self.si = None


    def OnConnect(self):
        self.vcenter = self.my_dialog_acceso_vcenter.nombre_vcenter.GetValue()
        self.login = self.my_dialog_acceso_vcenter.login_vcenter.GetValue()
        self.pwd = self.my_dialog_acceso_vcenter.passwor_vcenter.GetValue()
        self.port = self.my_dialog_acceso_vcenter.puert_vcenter.GetValue()

        # grabamos datos en el fichero config
        self.cfg.WriteInt('version', 1)
        self.cfg.Write('vcenter', self.vcenter)
        self.cfg.Write('login', self.login)
        self.cfg.Write('pwd', self.pwd)
        self.cfg.Write('port', self.port)


        # accedemos al vcenter
        try:
            if not self.si:
                self.context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
                self.context.verify_mode = ssl.CERT_NONE
                if logger != None: logger.info('vcenter:  ' + self.vcenter)

                self.si = SmartConnect(host=self.vcenter,
                                       user=self.login,
                                       pwd=self.pwd,
                                       port=int(self.port),
                                       sslContext=self.context)
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
        if logger != None: logger.info('desconecion')
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
def conectar_con_vcenter():

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
# Sacar listado carpetas

def sacar_listado_capertas(conexion):
    listado_carpetas = []
    name = []
    path = []
    guest = []
    anotacion = []
    estado = []
    dirip = []
    pregunta = []
    uuid = []


    #Calculamos el maximo de elementos a analizar
    max = 0
    for child in conexion.rootFolder.childEntity:
        max += 1
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity
            max = max + len(vmList)

    if logger != None: logger.info('el maximo es : {}'.format(max))
    keepGoing = True
    count = 0
    dlg = wx.ProgressDialog("Proceso cargando datos",
                            "Cargando datos",
                            maximum = max,
                            #parent=-1,
                            #style = wx.PD_APP_MODAL
                            #| wx.PD_CAN_ABORT
                            #| wx.PD_ELAPSED_TIME
                            #| wx.PD_ESTIMATED_TIME
                            #| wx.PD_REMAINING_TIME
                            )
    keepGoing = dlg.Update(count)

    # miramos el arbol de Virtual Machine
    for child in conexion.rootFolder.childEntity:
        count += 1
        keepGoing = dlg.Update(count, "Loading")
        if hasattr(child, 'vmFolder'):
            datacenter = child
            vmFolder = datacenter.vmFolder
            vmList = vmFolder.childEntity

            for vm in vmList:
                count += 1
                keepGoing= dlg.Update(count, "Loading")
                # if logger != None: logger.info (vm.name) # imprime todo el listado de carpetas
                carpeta = vm.name
                PrintVmInfo(vm, name, path, guest, anotacion, estado, dirip, pregunta, uuid, carpeta, listado_carpetas)

    # salida tabulada----------------------------------------
    if logger != None: logger.info('###############################')

    tabla = []
    elemento = []
    for i in range(len(name)):
        elemento.append(listado_carpetas[i])

        elemento.append(name[i])
        elemento.append(dirip[i])
        elemento.append(estado[i])
        elemento.append(pregunta[i])
        elemento.append(path[i])
        elemento.append(guest[i])
        elemento.append(anotacion[i])
        elemento.append(uuid[i])
        tabla.append(elemento)
        elemento = []

    # headers=['Carpeta', 'pool', 'Nombre','IP','Estado','pregunta', 'Disco Path', 'Sistema', 'Notas', 'uuid']
    # if logger != None: logger.info (tabulate(tabla, headers, tablefmt="fancy_grid"))

    dlg.Destroy()
    return (tabla)


# ----------------------------------------------------------------------
# Sacar listado carpetas

def PrintVmInfo(vm, name, path, guest, anotacion, estado, dirip, pregunta, uuid, carpeta, listado_carpetas, depth=1):
    """
   Print information for a particular virtual machine or recurse into a folder
    with depth protection
   """
    maxdepth = 50

    # if this is a group it will have children. if it does, recurse into them
    # and then return

    if hasattr(vm, 'childEntity'):
        if depth > maxdepth:
            return
        vmList = vm.childEntity

        for c in vmList:
            PrintVmInfo(c, name, path, guest, anotacion, estado, dirip, pregunta, uuid, carpeta, listado_carpetas,
                        depth + 1)
        return

    summary = vm.summary

    if carpeta != None or carpeta != "":
        listado_carpetas.append(carpeta)
    else:
        listado_carpetas.append('sin carpeta')

    name.append(summary.config.name)
    path.append(summary.config.vmPathName)
    guest.append(summary.config.guestFullName)
    estado.append(summary.runtime.powerState)
    uuid.append(summary.config.uuid)

    annotation = summary.config.annotation
    if annotation != None and annotation != "":
        anotacion.append(summary.config.annotation)
    else:
        anotacion.append('sin anotacion')

    # if logger != None: logger.info("State      : ", summary.runtime.powerState)
    if summary.guest != None:
        ip = summary.guest.ipAddress
        if ip is not None and ip != "":
            dirip.append(summary.guest.ipAddress)

        else:
            dirip.append('ip?')

    if summary.runtime.question is not None:
        pregunta.append(summary.runtime.question)
    else:
        pregunta.append('no datos')
        # if logger != None: logger.info("Question  : ", summary.runtime.question.text)
        # if logger != None: logger.info("")


########################### Start the program  ####################
if __name__ == "__main__":

    #parser    = argparse.ArgumentParser ( description= 'si pasamos a al aplicación --d tendremos debug' )
    #parser.add_argument('--d', action="store_true", help='imprimir informacion  debug')
    #args     =    parser.parse_args()
    # Use logger to control the activate log.
    logger = None
    #read inital config file
    # log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')
    if os.name == 'posix':
        logging.config.fileConfig('logging.conf')
        # create logger
        logger = logging.getLogger('pyvmwareclient')
        logger.info("# Start here a new loggin now")
      # logger.getLogger(__name__)
      # logger.basicConfig(filename='pyVMwareClient.log',format='%(asctime)s %(name)-5s %(levelname)-5s %(message)s', level=logger.DEBUG)


    app = wx.App(False)
    conexion = conectar_con_vcenter()
    frame = MyFrame()
    app.MainLoop()
