#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import wx
import wx.lib.mixins.listctrl as listmix
import atexit
import ssl
import os
import re
import time
import OpenSSL
import webbrowser
import logging.config
import humanize
# import argparse
import sys
import wx.lib.inspection
from wxgladegen import dialogos
from pyVim.connect import SmartConnect, Disconnect
from tools import tasks
from tools import vm
from pyVmomi import vim
from menu_action import action_vm



class theListCtrl(wx.ListCtrl):
    # ----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)






class MyPanel(wx.Panel, listmix.ColumnSorterMixin):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        # self.Bind(wx.EVT_BUTTON, self.OnSelectFont, btn)

        self.list_ctrl = theListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.SUNKEN_BORDER)
        st1 = wx.StaticText(self, label='Find String VM: ')
        self.cadenaBusqueda = wx.TextCtrl(self)
        btnbusqueda = wx.Button(self, label="Find")
        btnrecargaVM = wx.Button(self, label="Update VM")
        btnhost = wx.Button(self, label="host")

        name_rows = ['Carpeta', 'Nombre', 'IP', 'Estado', 'pregunta', 'Disco Path', 'Sistema', 'Notas', 'uuid']

        # cargamos los nombres de los elementos
        for x in range(len(name_rows)):
            self.list_ctrl.InsertColumn(x, name_rows[x])

        # conexion = conectar_con_vcenter(self, id)
        self.tabla = []
        self.tabla = sacar_listado_capertas(conexion)
        self.vm_buscados = []

        self.cargardatos_en_listctrl(self.tabla)

        # For use to auto-orden --- Call to Getlistctrl
        self.itemDataMap = self.tabla
        listmix.ColumnSorterMixin.__init__(self, len(name_rows))

        # Add menu to Click element in VM 
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected, self.list_ctrl)
        # self.list_ctrl.Bind(wx.EVT_CONTEXT_MENU, self.onItemSelected, self.list_ctrl)

        # This code put items into window with orden.
        txtcontador = wx.StaticText(self, label='total VM: ' + str(len(self.tabla)))
        sizer = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(st1, wx.ALL | wx.ALIGN_CENTER, 5)
        hbox1.Add(self.cadenaBusqueda, wx.ALL | wx.ALIGN_CENTER, 5)
        hbox1.Add(btnbusqueda, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)
        hbox1.Add(btnrecargaVM, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)
        hbox1.Add(btnhost, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER, 5)
        hbox1.Add(txtcontador, wx.ALL | wx.ALIGN_CENTER, 5)
        sizer.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_CENTER, border=2)
        self.Bind(wx.EVT_BUTTON, self.busquedadatos, btnbusqueda)
        self.Bind(wx.EVT_BUTTON, self.recarga_VM, btnrecargaVM)
        self.Bind(wx.EVT_BUTTON, self.bntlocateHost, btnhost)

        sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

        #Call to function for locate the esxi
        

        # tools for search an debug (to use uncomment the next line, works only linux)
        # wx.lib.inspection.InspectionTool().Show()

    def bntlocateHost(self, event):
        locatehost(conexion)
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
        #print (object_about)
        #print(object_about.version)

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
        #self.myRowDict = {}
        index = 0
        for elemen in _tabla_paracargar:
            self.list_ctrl.InsertItem(index, elemen[0])
            total_elemen = len(elemen)
            for i in range(total_elemen):
                self.list_ctrl.SetItem(index, i, str(elemen[i]))
            # the nex line is for work the auto list
            self.list_ctrl.SetItemData(index, index)
            #self.myRowDict[index] = elemen
            index += 1



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

        if not hasattr(self, "sshID"):
            self.info_vm = wx.NewId()
            self.set_note = wx.NewId()
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
            self.Bind(wx.EVT_MENU, self.on_info, id=self.info_vm)
            self.Bind(wx.EVT_MENU, self.on_set_note, id=self.set_note)
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
        item_set_note = self.menu.Append(self.set_note, "Set Note...")
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

    #########ADD the command to the events in the display dilog ######


    def on_info(self, event):
        action_vm.on_info_vm(self, event, conexion, logger)
 
    def on_set_note(self, event):
        action_vm.on_set_note(self, event, conexion, logger)
 
    def onSnap_list(self, event):
        action_vm.onSnap_list(self, event, conexion, logger)
        
    def onSnap_create(self, event):
        action_vm.onSnap_create(self, event, conexion, logger)

    def onSsh(self, event):
         action_vm.onSsh(self, event, conexion, logger)

    def onHtml(self, event):
        action_vm.onHtml(self, event, conexion, logger)
        
    def onRdp(self, event):
        action_vm.onRdp(self, event, conexion, logger)        

    def onsoftreboot(self, event):
        action_vm.onsoftreboot(self, event, conexion, logger)

    def onsoftPowerOff(self, event):
        action_vm.onsoftPowerOff(self, event, conexion, logger)

    def onreboot(self, event):
        action_vm.onreboot(self, event, conexion, logger)
        
    def onpower_on(self, event):
        action_vm.onpower_on(self, event, conexion, logger)              

    def onpowerOff(self, event):
        action_vm.onpowerOff(self, event, conexion, logger)
        
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


# ######Display data for connet whit esxi an vcenter ######################

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
        """
            Present a dialog box to get the datas for conect to esxi or vcenter
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
# Locate list on host
# ----------------------------------------------------------------------
def locatehost(conexion):
    """
        Locate all host an  info about memory, CPU usasge an other
        Need a conexion active to datecenter to locate data
    """

    MBFACTOR = float(1 << 20)
    index = 0

    my_dialogo_host = dialogos.Dialogo_host(None, -1, 'Host en vcenter')
    name_rows = ['Data center', 'Resource Name', 'Host Name', 'CPU usage', 'Host memory capacity', 'Host memory usag', 'Free memory percentage']
    # cargamos los nombres de los elementos
    for i in range(len(name_rows)):
        my_dialogo_host.list_ctrl_host.InsertColumn(i, name_rows[i])

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

                            my_dialogo_host.list_ctrl_host.InsertItem(index, datacenter.name)
                            my_dialogo_host.list_ctrl_host.SetItem(index, 1, str(computeResource.name))
                            my_dialogo_host.list_ctrl_host.SetItem(index, 2, str(host.name))
                            my_dialogo_host.list_ctrl_host.SetItem(index, 3, str(cpuUsage))
                            my_dialogo_host.list_ctrl_host.SetItem(index, 4, str(humanize.naturalsize(memoryCapacity, binary=True)))
                            my_dialogo_host.list_ctrl_host.SetItem(index, 5, str(memoryUsage / 1024) + " GiB")
                            my_dialogo_host.list_ctrl_host.SetItem(index, 6, str(freeMemoryPercentage) + " %")
                            #for use to auto use for auto sort colum
                            my_dialogo_host.list_ctrl_host.SetItemData(index, index)
                            index += 1

    dlg.Destroy()
    my_dialogo_host.ShowModal()
    # For use to auto-orden --- Call to Getlistctrl
    #self.itemDataMap = self.tabla
    #my_dialogo_host.list_ctrl_host.ColumnSorterMixin.__init__(self, len(name_rows))


# ----------------------------------------------------------------------
# Locate info about Machine MV
# ----------------------------------------------------------------------

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
