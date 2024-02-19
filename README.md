# Proscenic 790T Robot Cleaner - Domoticz python plugin

## Installing
After copy files into plugin folder, you must restart your Domoticz Server.
Your Robot will automatically be added into Hardware panel. Loking for it into Type of devices list.
Then you must add the new hardware, and go to Devices panel in order to put controls into Dashboard.

If you have doubts, please consult the official guide: https://www.domoticz.com/wiki/Using_Python_plugins#Installing_a_plugin

## Issues
In my Robot 790T ZigZag mode doesn't works. Don't worry about it.
Robot Code errors are not available. May be next version.

## Requirements
Your Robot need to be connected to the same network than Domoticz. If you don't know how to put the robot in the same network, follow this steps:
- Put the robot into "CONN" mode
- In your phone or PC, you must connect with "Proscenic_XXXX" SSID access point. 
- To know the IP of Robot you can use an App such as Fing or ScanIP. The IP can be similar to 192.168.4.1
- Now connect with your Web browser to this IP.
- You would see a web page where you can introduce your 2,4GHz SSID home wifi and your password.
- After that the Robot would must be connected to your home network.

## Thanks to
This plugin is inspired by these repos:
* https://github.com/mrin/domoticz-mirobot-plugin
* https://github.com/markomannux/pyproscenic
* https://github.com/oskarn97/fhem-Proscenic
* https://github.com/trandbert37/DomoticzProscenicVacuum
* https://github.com/999LV/BatteryLevel

and Home Assistant Community
* https://community.home-assistant.io/t/proscenic-790t-integration/82969
