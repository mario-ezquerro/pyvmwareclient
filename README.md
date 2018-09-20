# pyvmwareclient [![GitHub license](https://img.shields.io/github/license/wbugbofh/pyvmwareclient.svg)](https://github.com/wbugbofh/pyvmwareclient/blob/master/LICENSE) [![HitCount](http://hits.dwyl.io/wbugbofh/wbugbofh/pyvmwareclient.svg)](http://hits.dwyl.io/wbugbofh/wbugbofh/pyvmwareclient)


Download the code, install the 'requirements.txt' and then you use:"python3.5 app.py" to work with the ultimate version.
```bash
$ pip install -r requirements.txt
$ python app.py
```

Similar the old vmwareclient, vmware client that connect to esxi or vcenterVMware 5.0, 5.5 6.0 & 6.5 , uses the python APIs.

Works in linux using putty (If also the putty in linux) and the Remminia to connect with RDP. And work in Windows the putty is necesary to with the path and work MacOs too

What programs do yo need in your path?

|**Linux**        |**Windows**       |**MacOs**            |
|:----------------|:-----------------|:--------------------|
|putty            |putty             |shell (on system)    |
|remminia         |mstsc (As sistem) |mstsc (By Microsoft) |
|vmrc or vmplayer |vmrc or vmplayer  |vmrc or vmplayer     |

You need the path in your system to work the three client application ,Linux (Remminia, putty, vrmc or vmplayer) in Windows (putty, Terminal server client and vrmc or vmplayer) in Macos(Terminarl server Windows, and vrmc or vmplayer)

Note: The vmplayer it instaler with vmware-workstation, vmware does not allow simultaneos installation of vrmc and  vmplayer)

## Available Options for a VM:

  01. Snapshot make and display delete, delete all and Revert
  02. Connection ssh using putty to VM Unix/Linux
  03. Connection RDP using client Remminia(linux) or Windows Client (Windows MacOS)
  04. Connection VRMC add to menu.
  05. Connection console wiht HTML Client
  06. Power on and power off VM
  07. Reset hard y soft VM
  08. Reboot a VM
  09. Change or Add Notes
  10. Display tecnical Info about VM
  11. Display Info about host (when connection vcenter)
  12. Display Grafic about data host
  13. Display Grafic about data VM
  14. Save and Load the data VM in csv file format
  15. Show event an error in a VM
  16. Search with name or ir or mac table

## Example of  screenshots the are made with wx-windows

At start you must put your user and domain an name of esxi or vcenter:

![Image user an password window](/images/user_pass.png)

Then you can see the "LOAD" of datacente data:

![Image window lading data](/images/loading_data.png)

The list of VM that are in your system:

![Window list VM](/images/list_vm.png)

And you can make a lot of commands in your VM (this image is not the ultimate menu options:

![Exampe window Menu (not the update version)](/images/menu.png)
