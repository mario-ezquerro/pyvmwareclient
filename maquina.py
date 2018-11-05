#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Mario Ezquerr <mario.ezquerro@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer
#    in this position and unchanged.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR(S) ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR(S) BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import logging.config
from tools import vm
from tools import alarm
from pyVmomi import vim


class Maquina():
    """
    When read a VM data fron Vcenter or esxi, we need initialice the data
    for when read all data

    :param vm: objet de type Vim
    :param logger: objet with file logger when initilice if no the value None.
    :return:

    """
    def __init__(self, vm, logger=None):

        self.vm = vm
        
        self.summary = vm.summary
        self.resource_pool=''
        self.folder = self.vm.parent.name
        self.listado_folders = ''
        self.name = self.summary.config.name
        self.path = self.summary.config.vmPathName
        self.guest = self.summary.config.guestFullName
        self.anotacion = ''
        self.state = self.summary.runtime.powerState
        self.dirmacs = ''
        self.dirip = ''
        self.dns_name = ''
        self.ask_data = ''
        self.uuid = self.summary.config.uuid
        self.sing = ''
        self.logger = logger
        
        try:
            self.resource_pool = self.vm.resourcePool.summary.name
        except:
            self.resource_pool = 'none'

        #print(self.vm.datastore[0].summary)
        #print(self.vm.parent.parent.summary)
        #for datamol in self.vm.datastore:
        #    print(datamol)
        

        if self.folder != None or self.folder != "":
            self.listado_folders = self.vm.parent.name
        else:
            self.listado_folders = 'sin folder'

        
        self.annotation = self.summary.config.annotation
        if self.annotation != None and self.annotation != "":
            self.anotacion = self.summary.config.annotation
        else:
            self.anotacion = ('sin anotacion')


        

        # if logger != None: logger.info("Data: {}--".format(vm.summary))
        # Load the NIC's and locate all ip's
        #print(summary.guest)
        if self.summary.guest != None:
            self.ip = self.summary.guest.ipAddress
            if self.ip is not None and self.ip != "":
                self.macs = ''
                self.ips = ''
                for self.nic in self.vm.guest.net:                         
                    if  hasattr(self.nic.ipConfig, 'ipAddress'):
                        for self.ipAddress in self.nic.ipConfig.ipAddress:
                            self.macs = self.macs + self.nic.macAddress + ' '
                            self.ips = self.ips + self.ipAddress.ipAddress + ' '
                self.dirmacs = self.macs
                self.dirip = self.ips
                #dirip.append(summary.guest.ipAddress)
            else:
                self.dirmacs = 'mac?'
                self.dirip = 'ip?'


        if self.summary.guest.hostName is not None:
            self.dns_name = (self.summary.guest.hostName)
        else:
            self.dns_name = ('no datos')

        """if summary.runtime.question is not None:
                ask_data.append(summary.runtime.question)
            else:
                ask_data.append('no datos')"""


        #if str(alarm.print_triggered_alarms(entity=vm)) == 'None' and  len(str(alarm.get_alarm_refs(entity=vm))) == 2 :
        if len(str(alarm.get_alarm_refs(entity=self.vm))) == 2 :
            self.sing='0'
        else:
            self.sing='ALARMA'