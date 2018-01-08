
#import wx
#import wx.lib.mixins.listctrl as listmix
#import wx.lib.inspection
import logging.config
from wxgladegen import dialogos
#from pyVim.connect import SmartConnect, Disconnect
#from pyVmomi import vim


def on_info_vm(self, event, conexion, logger):
        fila = self.listadoVM
        print (self, event, conexion)
        for i in range(len(fila)):
            if logger != None: logger.info(fila[i])
            
        # El 9 elemento es el UUID
        
        # List about vm detail in dialog box

        self.my_dialogo_texto = dialogos.Dialogo_texto(None, -1, 'Listados de datos VM')

        vm = conexion.searchIndex.FindByUuid(None,fila[8], True)
        

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