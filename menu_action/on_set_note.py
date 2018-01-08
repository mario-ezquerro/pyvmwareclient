"""
Written by Mario Ezquerro

Github: https://github.com/xx
Website: https://xx.github.io/
Blog: http://www.errr-online.com/
This code has been released under the terms of the Apache 2 licenses
http://www.apache.org/licenses/LICENSE-2.0.html

Helper module for menu operations.
"""

__author__ = "Mario Ezquerro."



def on_set_note(self, event):
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