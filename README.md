# pyvmwareclient [![GitHub license](https://img.shields.io/github/license/wbugbofh/pyvmwareclient.svg)](https://github.com/wbugbofh/pyvmwareclient/blob/master/LICENSE) [![HitCount](http://hits.dwyl.io/wbugbofh/wbugbofh/pyvmwareclient.svg)](http://hits.dwyl.io/wbugbofh/wbugbofh/pyvmwareclient)


Download the code, install the 'requirements.txt' and then you use:"python3.5 app.py" to work with the ultimate version.
```bash
$ pip install -r requirements.txt
$ python app.py
```

Similar the old client vmwareclient, vmware client that connect to esxi or vcenterVMware 5.0, 5.5 6.0, 6.5  and 6.7 , uses the python APIs.

Works in linux using putty (yes, there is  the putty in linux) and the Remminia to connect with RDP. And work in Windows, the putty is necesary to add the path and work MacOs too.

What programs do yo need in your commputer path?

|**Linux**        |**Windows**       |**MacOs**            |
|:----------------|:-----------------|:--------------------|
|putty            |putty             |shell (on system)    |
|remminia         |mstsc (on system) |mstsc (By Microsoft) |
|vmrc or vmplayer |vmrc or vmplayer  |vmrc or vmplayer     |

You need the path in your system to work the three client application ,Linux (Remminia, putty, vrmc or vmplayer) in Windows (putty, Terminal server client and vrmc or vmplayer) in Macos(Terminarl server Windows, and vrmc or vmplayer)

Note: The vmplayer it instaler with vmware-workstation, vmware does not allow simultaneos installation of vrmc and  vmplayer)

## Available Options for a VM:

  01. Snapshot make and display delete, delete all and Revert
  02. Connection ssh using putty to VM Unix/Linux
  03. Connection RDP using client Remminia(linux) or Windows RDP Client (Windows MacOS)
  04. Connection VRMC add to menu.
  05. Connection console wiht HTML Client
  06. Connection http y https VM with ip (if vmtools is instaled to locate ip VM)
  07. Power on and power off VM
  08. Reset hard y soft VM
  09. Reboot a VM
  10. Change or Add Notes
  11. Display tecnical Info about VM
  12. Display Info about host (when connection vcenter)
  13. Display Grafic about data host
  14. Display Grafic about data VM
  15. Save and Load the data VM in csv file format
  16. Show event an error in a VM
  17. Search with name or ip or mac table

## Example of screenshots the are made with wx-windows

At start you must put your user and domain an name of esxi or vcenter, (The captured images may not present all the options, but they are not the last version of the program):

![Image user an password window](https://github.com/wbugbofh/pyvmwareclient/blob/master/images/user_pass.png)

Then you can see the "LOAD" of datacente data:

![Image window lading data](https://github.com/wbugbofh/pyvmwareclient/blob/master/images/loading_data.png)

The list of VM that are in your system:

![Window list VM](https://github.com/wbugbofh/pyvmwareclient/blob/master/images/list_vm.png)

And you can make a lot of commands in your VM (this image is not the ultimate menu options:

![Exampe window Menu (not the update version)](https://github.com/wbugbofh/pyvmwareclient/blob/master/images/menu.png)

You can  look the grafic about VM with this:

![Exampe window Menu (not the update version)](https://github.com/wbugbofh/pyvmwareclient/blob/master/images/grafic_vm.png)
