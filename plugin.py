# Plugin to control Proscenic Vacuum
#
# Author: AJV
#
# OFF:               AA55A55A0DFDE20906000100030000000000
# RUN:               AA55A55A0DFDE20906000100020000000100
# DOCK:              AA55A55A0FFDE20906000100010000000000
#
# MODE_AUTO:         AA55A55A09FDE20906000100020500000000
# MODE_AREA:         AA55A55A0AFDE20906000100020400000000
# MODE_EDGE:         AA55A55A0BFDE20906000100020300000000
# MODE_ZIGZAG:       AA55A55A0CFDE20906000100020200000000
#
# MOVE_BACKWARD:     AA55A55A0BFDE20906000100030000020000
# MOVE_FORWARD:      AA55A55A0CFDE20906000100030000010000
# MOVE_LEFT:         AA55A55A0AFDE20906000100030000030000
# MOVE_RIGHT:        AA55A55A09FDE20906000100030000040000
# MOVE_STOP:         AA55A55A08FDE20906000100030000050000
#
# VOICE_OFF:         AA55A55A0BFDE20906000100040000000001
# VOICE_ON:          AA55A55A0AFDE20906000100040000000002
#
# WIND_HIGH:         AA55A55A0AFDE20906000100030003000000
# WIND_NORMAL:       AA55A55A0BFDE20906000100030002000000
# WIND_OFF:          AA55A55A0CFDE20906000100030001000000
#
# QUERY_ORDER:       AA55A55A28FDD20700000100
# QUERY_STATE:       AA55A55A17FDE10900000100
#
# Messge XML Format is:
#
# <MESSAGE>
#   <HEADER MsgType="MSG_TRANSIT_SHAS_REQ" MsgSeq="1" From="02000000000000000" To="01801930aea421f164" Keep="1"/>
#   <BODY>
#       FRSQU5TSVRfSU5GTz48Q09NTUFORD5ST0JPVF9DTUQ8L0NPTU1BTkQ+PFJUVT5BQTU1QTU1QTI4RkREMjA3MDAwMDAxMDA8L1JUVT48L1RSQU5TSVRfSU5GTz4=
#   </BODY>
# </MESSAGE>
#
# BODY is b64encoded, decode it we have:
#
# <MESSAGE>
#   <HEADER MsgType="MSG_TRANSIT_SHAS_REQ" MsgSeq="1" From="02000000000000000" To="01801930aea421f164" Keep="1"/>
#   <BODY>
#       <TRANSIT_INFO>
#            <COMMAND>ROBOT_CMD</COMMAND>
#            <RTU>AA55A55A98FCE3090B0001000600010003026402000000</RTU>
#            <NAME>Robot Aspirador</NAME>
#            <TYPE>/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff/xff</TYPE>
#            <UID>5CCF7FD109CC</UID>
#            <WIFIVER>1.0.36</WIFIVER>
#            <MCUVER>999.9.9(000)</MCUVER>
#        </TRANSIT_INFO>
#   </BODY>
# </MESSAGE>
#
# RTU parameter contains information about battery level and state of robot. I cannot decode al information, but
#
# Examples of RTU parameter
# RUN:
# MODE AUTO     AA55A55A|D1|FCE3090B|0001|0001|0102|0003|02|2E|02|000000
# MODE EDGE     AA55A55A|BE|FCE3090B|0001|0001|0303|0003|02|3E|02|000000
# MODE AREA     AA55A55A|C1|FCE3090B|0001|0001|0402|0003|02|3B|02|000000

# OFF:          AA55A55A|D2|FCE3090B|0001|0002|0001|0003|02|2E|02|000000
# RECHARGE:     AA55A55A|CF|FCE3090B|0001|0004|0102|0003|02|2D|02|000000
# CHARGING:     AA55A55A|D0|FCE3090B|0001|0005|0001|0003|02|2D|02|000000
# FULL:         AA55A55A|98|FCE3090B|0001|0006|0001|0003|02|64|02|000000

                  
# Means:        xxxxxxxx|xx|xxxxxxxx|xxxx|stat|mode|xxxx|xx|bl|xx|xxxxxx 
#
# stat: robot estate. (1) Run, (2) Off, (4) looking for base, (5) charging in base, (6) full recharge in base
# mode: Stop (0001), Auto (0102), Edge (0303), Area (0402). Zig Zag don't works in my robot.
# bl: is de batery level in hexadecimal %.
# 
#   


"""
<plugin key="Proscenic790T" name="Proscenic Cleaner 790T" author="AJV" version="1.0.0" externallink="">
    <description>
        <h2>Proscenic vacuum</h2><br/>
        Python plugin to control your Proscenic Robot Cleaner 790T
    </description>
</plugin>
"""
import Domoticz

import xml.etree.cElementTree as ET
import re
 
from base64 import *
from socket import *
from time import sleep

class BasePlugin:
    enabled = True

    __HEARTBEATS2MIN = 3    # onHeartBeat procedure is called every 10 seconds, so 6 times per minute
    __MINUTES = 1           # or use a parameter. This will execute your command line in onHeartBeat, every minute

    __BufferTX = 0
    __BufferRX = 0
    __MsgSeq = 0
    
    __name =''
    __uid = ''
    __wifiver = ''
    __mcuver = ''
    
    __control = 0
    __mode = 0
    __move = 0
    __levelBatt = 0
    
    controlUnit = 1
    modeUnit = 2
    batteryUnit = 3
    moveUnit = 4
    
    iconRobot = 'Proscenic790TRobot'
    iconBattFull = 'Proscenic790TBattFull'
    iconBattOk = 'Proscenic790TBattOk'
    iconBattLow = 'Proscenic790TBattLow'
    iconBattEmpty = 'Proscenic790TBattEmpty'
    
    controlOptions = {
        "LevelActions": "||",
        "LevelNames": "Off|Run|Dock",
        "LevelOffHidden": "false",
        "SelectorStyle": "0"
    }

    modeOptions = {
        "LevelActions": "||||",
        "LevelNames": "Off|Auto|Area|Edge|Zigzag",
        "LevelOffHidden": "false",
        "SelectorStyle": "0"
    }
    
    moveOptions = {
        "LevelActions": "|||",
        "LevelNames": "Off|For|Back|Left|Right",
        "LevelOffHidden": "true",
        "SelectorStyle": "0"
    }

    control = {
        0:  "AA55A55A0DFDE20906000100030000000000", #OFF
        10: "AA55A55A0DFDE20906000100020000000100", #RUN
        20: "AA55A55A0FFDE20906000100010000000000" #DOCK
    }

    mode = {
        0:  "AA55A55A0DFDE20906000100030000000000", #STOP
        10: "AA55A55A09FDE20906000100020500000000", #AUTO
        20: "AA55A55A0AFDE20906000100020400000000", #AREA
        30: "AA55A55A0BFDE20906000100020300000000", #EDGE
        40: "AA55A55A0CFDE20906000100020200000000" #ZIGZAG
    }

    query = {
        10: "AA55A55A28FDD20700000100", #QUERY_ORDER       
        20: "AA55A55A17FDE10900000100", #QUERY_STATE
    }
    
    move = {
        0:  "AA55A55A08FDE20906000100030000050000", #MOVE_STOP
        10: "AA55A55A0CFDE20906000100030000010000", #MOVE_FORWARD
        20: "AA55A55A0BFDE20906000100030000020000", #MOVE_BACKWARD
        30: "AA55A55A0AFDE20906000100030000030000", #MOVE_LEFT
        40: "AA55A55A09FDE20906000100030000040000", #MOVE_RIGHT
    }

    def __init__(self):
        self.port = 10684
        return

    def onStart(self):
        Domoticz.Debugging(0)
        
        self.__runAgain = self.__HEARTBEATS2MIN * self.__MINUTES
        
        # Load Icons
        if self.iconRobot not in Images: 
            Domoticz.Image('790t_robot_icons.zip').Create()
        
        if self.iconBattFull not in Images: 
            Domoticz.Image('790t_batt_full_icons.zip').Create()
            
        if self.iconBattOk not in Images: 
            Domoticz.Image('790t_batt_ok_icons.zip').Create()      

        if self.iconBattLow not in Images: 
            Domoticz.Image('790t_batt_low_icons.zip').Create()  

        if self.iconBattEmpty not in Images: 
            Domoticz.Image('790t_batt_empty_icons.zip').Create()                
        
        # Create Devices
        if self.controlUnit not in Devices:
            Domoticz.Device(Name='Control', Unit=self.controlUnit, TypeName='Selector Switch', Image=Images[self.iconRobot].ID, Options=self.controlOptions).Create()

        if self.modeUnit not in Devices:
            Domoticz.Device(Name='Mode', Unit=self.modeUnit, TypeName='Selector Switch', Image=Images[self.iconRobot].ID, Options=self.modeOptions).Create()
        
        if self.batteryUnit not in Devices:
            Domoticz.Device(Name='Battery', Unit=self.batteryUnit, TypeName="Custom", Image=Images[self.iconBattFull].ID, Options={"Custom": "1;%"}).Create()

        if self.moveUnit not in Devices:
            Domoticz.Device(Name='Move', Unit=self.moveUnit, TypeName='Selector Switch', Image=Images[self.iconRobot].ID, Options=self.moveOptions).Create()

        
    def onStop(self):
        pass

    def onConnect(self, Connection, Status, Description):
        pass

    def onMessage(self, Connection, Data):
        pass
    
    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        
        if self.controlUnit == Unit:
            if Level == 10:
                Domoticz.Log("RUN")
            elif Level == 20:
                Domoticz.Log("DOCK")
            else:
                Domoticz.Log("OFF")
                
            # Send Command
            if self.apiRequest(Level, self.control):
                self.__control = Level
                UpdateDevice(self.controlUnit, self.__control)
                                  
        elif self.modeUnit == Unit:
            if Level == 10:
                Domoticz.Log("AUTO")
            elif Level == 20:
                Domoticz.Log("AREA")
            elif Level == 30:
                Domoticz.Log("EDGE")
            elif Level == 40:
                Domoticz.Log("ZIGZAG")
            else:
                Domoticz.Log("STOP")
            
            # Send 
            if self.apiRequest(Level, self.mode):
                self.__mode = Level
                UpdateDevice(self.modeUnit, self.__mode)
            
            
        elif self.moveUnit == Unit:
            if Level == 10:
                Domoticz.Log("FOR")
            elif Level == 20:
                Domoticz.Log("BACK")
            elif Level == 30:
                Domoticz.Log("LEFT")
            elif Level == 40:
                Domoticz.Log("RIGHT")
            else:
                Domoticz.Log("STOP")
            
            # Send Command
            self.apiRequest(Level, self.move)
            UpdateDevice(self.moveUnit, Level)
            sleep(0.25)
            Level=0
            self.apiRequest(Level, self.move)
            UpdateDevice(self.moveUnit, Level)
            
    def generateMessageBody(self, command, action):
        transitInfo = ET.Element('TRANSIT_INFO')
        ET.SubElement(transitInfo, 'COMMAND').text = 'ROBOT_CMD'
        ET.SubElement(transitInfo, 'RTU').text = action[command]
        return ET.tostring(transitInfo)

    def apiRequest(self, command, action):

        cs = socket(AF_INET, SOCK_DGRAM)
        cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        cs.settimeout(0.5)
        self.__MsgSeq += 1

        message = ET.Element("MESSAGE", Version="1.0")
        ET.SubElement(message, "HEADER", MsgType="MSG_TRANSIT_SHAS_REQ", MsgSeq=str(self.__MsgSeq), From="020000000000000000", To="01801930aea421f164", Keep="1")
        ET.SubElement(message, "BODY").text = b64encode(self.generateMessageBody(command, action)).decode('ascii')

        self.__BufferTX = ET.tostring(message, encoding='utf8', method='xml')
        
        retries = 5
        while retries > 0:
            try:
                # Send command
                cs.sendto(self.__BufferTX, ('255.255.255.255', self.port))
                
                # Read response
                self.__BufferRX = cs.recv(1024)
                
                break;

            except Exception as e:
                Domoticz.Error('API Request Exception [%s]' % str(e))
                retries -= 1
                sleep(0.25)
        
        # Succesfully message sended        
        if retries > 0:
        
            message = ET.fromstring(self.__BufferTX)
            body = ''.join(chr(b) for b in b64decode(message.find('BODY').text) if 32 <= b < 128)
            Domoticz.Log(body) 
            message = ET.fromstring(self.__BufferRX)
            body = ''.join(chr(b) for b in b64decode(message.find('BODY').text) if 32 <= b < 128)
            
            # Replace TYPE content to avoid errors
            body = re.sub('<TYPE>?(.*?)</TYPE>', '<TYPE>xff</TYPE>', body,  flags=re.DOTALL)
            Domoticz.Log(body) 
            
            # after query status recived, parse body parameter
            if (action == self.query) and (command == 20):
                
                frame = ET.fromstring(body)
                    
                rtu = frame.find('RTU').text
                self.__name = frame.find('NAME').text
                self.__uid = frame.find('UID').text
                self.__wifiver = frame.find('WIFIVER').text
                self.__mcuver = frame.find('MCUVER').text
                
                # Parse Battery Level: 
                self.__levelBatt = int(rtu[36:-8], 16)
                UpdateDevice(self.batteryUnit, self.__levelBatt, self.__levelBatt)
                
                if self.__levelBatt >= 75:
                    icon = self.iconBattFull
                elif self.__levelBatt >= 50:
                    icon = self.iconBattOk
                elif self.__levelBatt >= 25:
                    icon = self.iconBattLow
                else:
                    icon = self.iconBattEmpty
                UpdateIcon(self.batteryUnit, Images[icon].ID)
                
                # Parse Robot State:
                self.__state = int(rtu[23:-20], 10)
                if self.__state == 1:
                    UpdateDevice(self.controlUnit, 10, self.__levelBatt)
                elif self.__state == 2:
                    UpdateDevice(self.controlUnit, 0, self.__levelBatt)
                elif self.__state == 4:
                    UpdateDevice(self.controlUnit, 20, self.__levelBatt)
                elif self.__state == 5:
                    UpdateDevice(self.controlUnit, 20, self.__levelBatt)
                elif self.__state == 6:
                    UpdateDevice(self.controlUnit, 20, self.__levelBatt)
              
                # Parse Mode State:
                self.__mode = int(rtu[27:-18], 10)
                if self.__mode == 0:
                    UpdateDevice(self.modeUnit, 0, self.__levelBatt)
                elif self.__mode == 1:
                    UpdateDevice(self.modeUnit, 10, self.__levelBatt)
                elif self.__mode == 3:
                    UpdateDevice(self.modeUnit, 30, self.__levelBatt)
                elif self.__mode == 4:
                    UpdateDevice(self.modeUnit, 20, self.__levelBatt)
                    
                # Update move control
                UpdateDevice(self.moveUnit, 0, self.__levelBatt)                
          
            return True
        else:
            return False

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        pass

    def onDisconnect(self, Connection):
        pass

    def onHeartbeat(self):
        
        Domoticz.Debug("onHeartbeat called")
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            self.__runAgain = self.__HEARTBEATS2MIN * self.__MINUTES
            # Execute your command
            Domoticz.Log("QUERY STATUS")
            self.apiRequest(20, self.query)
        else:
            Domoticz.Debug("onHeartbeat called, run again in " + str(self.__runAgain) + " heartbeats.")
        
        return True

def UpdateDevice(Unit, sValue, BatteryLevel=255, AlwaysUpdate=False):
    if Unit not in Devices: return
    nValue = (0 if sValue == 0 else 1)
    if Devices[Unit].nValue != nValue\
        or Devices[Unit].sValue != sValue\
        or Devices[Unit].BatteryLevel != BatteryLevel\
        or AlwaysUpdate == True:

        Devices[Unit].Update(nValue, str(sValue), BatteryLevel=BatteryLevel)
        
        Domoticz.Debug("Update %s: nValue %s - sValue %s - BatteryLevel %s" % (
            Devices[Unit].Name,
            nValue,
            sValue,
            BatteryLevel
        ))

def UpdateIcon(Unit, iconID):
    if Unit not in Devices: return
    d = Devices[Unit]
    if d.Image != iconID: d.Update(d.nValue, d.sValue, Image=iconID)

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
