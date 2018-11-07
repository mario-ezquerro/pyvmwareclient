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
import subprocess
from wxgladegen import dialogos
from pyVmomi import vim
from tools import tasks
from tools import alarm
from distutils.spawn import find_executable

__author__ = "Mario Ezquerro."

__all__ = [
    'on_info_vm', 'on_set_note', 'onSnap_list', 
    'onSnap_create', 'onSsh', 'onHtml', 'on_vmrc',
    'onRdp', 'onsoftreboot', 'onsoftPowerOff', 
    'onreboot', 'onpower_on', 'onpowerOff',
]




def on_info_vm(self, event, conexion, logger):
        """
        Arg:
            event       (Var from menu)
            conexion    (Var whit a conexion datacenter)
            logger      (Var objet to pass the log)
        """
        fila = self.listadoVM
        #print (self, event, conexion)
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


def on_event_vm(self, event, conexion, logger):
        """
        Arg:
            event       (Var from menu)
            conexion    (Var whit a conexion datacenter)
            logger      (Var objet to pass the log)
        """
        fila = self.listadoVM
        #print (self, event, conexion)
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
            
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        
        # List about vm detail in dialog box

        self.my_dialogo_texto = dialogos.Dialogo_texto(None, -1, 'Listados de Eventos VM')

        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        if logger != None: logger.info('informacion vm: '+ vm.summary.config.name)
        
        snaptexto  = "=====================\n "
        snaptexto += 'Maquna vm = ' + fila[1] + '\n'
        snaptexto += 'Triggerd: ' + str(alarm.print_triggered_alarms(entity=vm)) + '\n'
        snaptexto += 'Refs: ' + str(alarm.get_alarm_refs(entity=vm)) + '\n'

        # Since the above method will list all of the triggered alarms we will now
        # prompt the user for the entity info needed to reset an alarm from red
        # to green
        """
            if alarm.reset_alarm(entity_moref=HOST._moId,
                                 entity_type='HostSystem',
                                 alarm_moref=alarm_mor.strip(),
                                 service_instance=SI):
               snaptexto +="Successfully reset alarm {0} to green.".format(alarm_mor)"""

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

        self.my_dialogo_ssh = dialogos.DialogNote(None, -1, 'New Note in: {0}' .format(vm.name))
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


        self.my_dialogo_list = dialogos.Dialog_list(None, -1, 'Snapshots List')
        name_rows = ['VM Name', 'Name Snap', 'Description', 'Create time', 'State']
        # cargamos los nombres de los elementos
        for i in range(len(name_rows)):
            self.my_dialogo_list.list_ctrl_basic.InsertColumn(i, name_rows[i])

        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        snap_info = vm.snapshot

        index = 0
        
           
        if not snap_info:
            self.my_dialogo_list.list_ctrl_basic.InsertItem(index, fila[1])
            self.my_dialogo_list.list_ctrl_basic.SetItem(index, 1, 'No hay snapshot')
            if logger != None: logger.info ('No hay snapshot')
        else:
            tree = snap_info.rootSnapshotList
            while tree[0].childSnapshotList is not None:
                self.my_dialogo_list.list_ctrl_basic.InsertItem(index, fila[1])
                self.my_dialogo_list.list_ctrl_basic.SetItem(index, 1, str(tree[0].name))
                self.my_dialogo_list.list_ctrl_basic.SetItem(index, 2, str(tree[0].description))
                self.my_dialogo_list.list_ctrl_basic.SetItem(index, 3, str(tree[0].createTime))
                self.my_dialogo_list.list_ctrl_basic.SetItem(index, 4, str(tree[0].state))
                if logger != None: logger.info("Snap: {0} => {1}".format(tree[0].name, tree[0].description))
                if len(tree[0].childSnapshotList) < 1:
                    break
                tree = tree[0].childSnapshotList
                index += 1

        result = self.my_dialogo_list.ShowModal() # pintamos la ventana con la informcion
        self.my_dialogo_list.Destroy()



def onSnap_create(self, event, conexion, logger):

        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El 9 elemento es el UUID
        if logger != None: logger.info (fila[8])
        #Dialogo para pedir datos para el snapshop......

        self.my_dialogo_snapshot = dialogos.Dialog_snapshot(None, -1, 'Propiedades Snapshot')

        self.my_dialogo_snapshot.nombre_snap.SetValue(fila[1] + ' Razon del snapshot? ...' )
        result = self.my_dialogo_snapshot.ShowModal()

        nombre = str(self.my_dialogo_snapshot.nombre_snap.GetValue())
        descricion = str(self.my_dialogo_snapshot.descripcion_snap.GetValue())
        checkbox_memory=self.my_dialogo_snapshot.checkbox_memory.GetValue()
        checkbox_quiesce=self.my_dialogo_snapshot.checkbox_quiesce.GetValue()
        self.my_dialogo_snapshot.Destroy()

        #if logger != None: logger.info ('resultado = ' + str(result))
        #if logger != None: logger.info('wx.ID_OK = ' + str(wx.ID_OK))


        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        # Window progress task
        keepGoing = True
        dlg_process = wx.ProgressDialog("Process task snapshot ",
                            "Task process",
                            maximum = 100, )
        keepGoing = dlg_process.Update(0)

        if result == wx.ID_OK:
            if  vm  is not None:
                if logger != None: logger.info ("The current powerState is: {0}".format(vm.runtime.powerState))
                TASK = task = vm.CreateSnapshot_Task(nombre, description = descricion, memory=checkbox_memory, quiesce=checkbox_quiesce)
                #contador de tareas
                #count = 0
                #state_task= task.info.state
                wait_cursor = wx.BusyCursor()
                while task.info.state != vim.TaskInfo.State.success:
                    #if logger != None: logger.info('Running => {0}  state: {1} info.result = {2}'.format(count, task.info.state, task.info.result))
                    #if logger != None: logger.info('Running => {0}  %'.format(task.info.progress))
                    #count += 1
                    try:
                        porcentage = int(task.info.progress)
                    except:
                        pass

                    else:
                        keepGoing = dlg_process.Update(porcentage, "Snapshot {}%".format(porcentage))

                #tasks.wait_for_tasks(conexion, [TASK])
                if logger != None: logger.info("Snapshot Completed.")
                del wait_cursor

        dlg_process.Destroy()

        #listado de snapshot en una ventana emergente

        self.my_dialogo_texto = dialogos.Dialogo_texto(None, -1, 'Listados de Snapshots')

        del vm
        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        snap_info = vm.snapshot


        #Show the actual state snapshot
        onSnap_list(self, event, conexion, logger)




def onSsh(self, event, conexion, logger):
        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El tercer elemento es la ip es decier la fila[2]
        ips = fila[2].split()
        self.my_dialogo_ssh = dialogos.Dialogo_user_pass(None, -1, 'Ususario y password')
        for ip in ips:
            self.my_dialogo_ssh.combo_box_ip.Append(ip)
        # Load from file config the user to use with login to ssh
        cfg = wx.Config('appconfig')
        user_dominio = cfg.Read('login')
        user=user_dominio.split('@')
        self.my_dialogo_ssh.usuario.SetValue(user[0])
        #self.my_dialogo_ssh.usuario.SetValue('root')
        result = self.my_dialogo_ssh.ShowModal()  # show the dialog window with the information
        if result == wx.ID_OK:
            if os.name == 'nt' or os.name == 'posix': #If I have windwos or linux with putty in the path cmd
                comando = 'putty ' + self.my_dialogo_ssh.combo_box_ip.GetStringSelection() + ' -l ' + str(self.my_dialogo_ssh.usuario.GetValue()) + ' &'
                os.system(comando)    
            if sys.platform == 'darwin': # If I have a Macos
                comando = 'ssh ' + self.my_dialogo_ssh.combo_box_ip.GetStringSelection() +'@'+ str(self.my_dialogo_ssh.usuario.GetValue()) + ' &' 
                os.system(comando)
        self.my_dialogo_ssh.Destroy()

# url del VMRC https://www.vmware.com/go/download-vmrc
def on_vmrc(self, event, conexion, logger):
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
  
        # Locate the version of vcenter the object .version for locate the version of vcenter
        object_about = conexion.about
    
        #subprocess.call('nohup ' + executable + vmplayerargs + ' &', shell=True)

	    #vmrc://clone:[TICKET]@[HOST]:[PORT]/?moid=[VM-MOREF]
        URL_vmrc = 'vmrc://clone:{}@{}:{}/?moid={}'.format(session, host, puerto_vcenter, vm_moid)
        if logger != None: logger.info(URL_vmrc)
        
        #If you intall vmplayer workstation you need use vmplayer, if not you nee intall vmrc
        #The code detec if you intall vmplayer or vmrc and use the fist (the vmplayer it is at worstation instalation)
        estaelprograma = find_executable("vmplayer")
              
        if   estaelprograma:
            comando_vmrc = 'vmplayer ' + URL_vmrc  + ' &'
        else:    
            estaelprograma = find_executable('vmrc')
            if  estaelprograma:
                comando_vmrc = 'vmrc ' + URL_vmrc  + ' &'
            else:
                if logger != None: logger.info('Can not find the vrmc or vmplayer') 
        
        # Locate system to execute comand
        if os.name == 'nt':
            os.system(comando_vmrc)
        else: 
            subprocess.call(comando_vmrc, shell=True)





def onHtml(self, event, conexion, logger):
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
        #print(str(vcenter_data))

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


def on_httml_ip(self, event, conexion, logger):
        fila = self.listadoVM
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
        # El tercer elemento es la ip es decier la fila[2]
        ips = fila[2].split()
        self.my_dialogo_ssh = dialogos.Dialogo_user_pass(None, -1, 'Port and password')
        for ip in ips:
            self.my_dialogo_ssh.combo_box_ip.Append(ip)
        # Load from file config the user to use with login to ssh
        cfg = wx.Config('appconfig')
        port= '80'      
        self.my_dialogo_ssh.usuario.SetValue(port)
        #self.my_dialogo_ssh.usuario.SetValue('root')
        result = self.my_dialogo_ssh.ShowModal()  # show the dialog window with the information
        if result == wx.ID_OK:
            URL = "http://" + self.my_dialogo_ssh.combo_box_ip.GetStringSelection() + ':' + str(self.my_dialogo_ssh.usuario.GetValue())
            if logger != None: logger.info(URL)
            webbrowser.open(URL, new=1, autoraise=True)
            if logger != None: logger.info ("Waiting for open web seconds, then exit")


def onRdp(self, event, conexion, logger):
        if sys.platform == 'darwin':
            fila = self.listadoVM
            for i in range(len(fila)):
                if logger != None: logger.info(fila[i])
            # El tercer elemento es la ip osea la fila 2 
            ips = fila[2].split() # but now are a list
            self.my_dialogo_ssh = dialogos.Dialogo_user_pass(None, -1, 'Select a ip to connect')
            for ip in ips:
                self.my_dialogo_ssh.combo_box_ip.Append(ip)
            
            self.my_dialogo_ssh.label_user.Show(False)
            self.my_dialogo_ssh.usuario.Show(False)

            result = self.my_dialogo_ssh.ShowModal()  # show the ask window about ip
            if result == wx.ID_OK:
                ip_selecction = self.my_dialogo_ssh.combo_box_ip.GetStringSelection() 
            self.my_dialogo_ssh.Destroy()
            
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
            archConfiguracion.write('<string>' + ip_selecction + '</string>' + '\n')
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
            # El tercer elemento es la ip osea la fila 2 
            ips = fila[2].split() # but now are a list
            self.my_dialogo_ssh = dialogos.Dialogo_user_pass(None, -1, 'Select a ip to connect')
            for ip in ips:
                self.my_dialogo_ssh.combo_box_ip.Append(ip)
            
            self.my_dialogo_ssh.label_user.Show(False)
            self.my_dialogo_ssh.usuario.Show(False)

            result = self.my_dialogo_ssh.ShowModal()  # show the ask window about ip
            if result == wx.ID_OK:
                ip_selecction = self.my_dialogo_ssh.combo_box_ip.GetStringSelection() 
            self.my_dialogo_ssh.Destroy()

            comando = 'mstsc ' +'/v:'+ ip_selecction
            os.system(comando)

        if os.name == 'posix':
            fila = self.listadoVM
            for i in range(len(fila)):
                if logger != None: logger.info(fila[i])
            # El tercer elemento es la ip osea la fila 2 
            ips = fila[2].split() # but now are a list
            self.my_dialogo_ssh = dialogos.Dialogo_user_pass(None, -1, 'Select a ip to connect')
            for ip in ips:
                self.my_dialogo_ssh.combo_box_ip.Append(ip)
            
            self.my_dialogo_ssh.label_user.Show(False)
            self.my_dialogo_ssh.usuario.Show(False)

            result = self.my_dialogo_ssh.ShowModal()  # show the ask window about ip
            if result == wx.ID_OK:
                ip_selecction = self.my_dialogo_ssh.combo_box_ip.GetStringSelection() 
            self.my_dialogo_ssh.Destroy()

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
            archConfiguracion.write('server=' + ip_selecction + '\n')
            archConfiguracion.write('colordepth=24' + '\n')
            archConfiguracion.write('window_maximize=0' + '\n')
            archConfiguracion.write('window_height=' + '\n')
            archConfiguracion.write('window_width=' + '\n')
            archConfiguracion.write('viewmode=1' + '\n')
            archConfiguracion.write('scale=1' + '\n')
            archConfiguracion.close
            comando = 'remmina -c ' + ruta_fichero_config +'/remminaconfig.remmina' + ' &'
            os.system(comando)


def onsoftreboot(self, event, conexion, logger):
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


def onsoftPowerOff(self, event, conexion, logger):
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
def onreboot(self, event, conexion, logger):
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

def onpower_on(self, event, conexion, logger):
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


def onpowerOff(self, event, conexion, logger):
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



