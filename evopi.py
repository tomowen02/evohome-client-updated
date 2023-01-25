#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author     = "Chris Lambourne"
@copyright  = "Copyright 2017, EvoPi"
@credits    = ["Andrew Stock"]
@license    = "MIT"
@version    = "1.0.1"
@email      = "chris@cat4data.com"
@status     = "Production"
"""
#Imports
import evoconfig
from evohomeclient2 import EvohomeClient
import time
import http.server
from datetime import datetime, timedelta
import socket, errno

#Variables
HOST_PORT = 'http://{0}:{1}/'.format(evoconfig.url, str(evoconfig.port))
EVOPI_URL = '{0}evopi'.format(HOST_PORT)
ACCESS_URL = ''
myDevices = ''
client = ''
loc = '{0}myschedules.json'.format(evoconfig.srt)
dCount = 0
sf = None

def startWebserver():

    #create a webserver to serve the data to
    server_class = http.server.HTTPServer
    httpd = server_class((evoconfig.url, evoconfig.port), MyHandler)
    print(time.asctime(), "Server Starts - %s:%s" % (evoconfig.url, evoconfig.port))

    try:
        httpd.serve_forever()
    except socket.error as e:
        if isinstance(e.args, tuple):
            print("errno is %d" % e[0])
            if e[0] == errno.EPIPE:
               # remote peer disconnected
               print("Detected remote disconnect")
            else:
               # determine and handle different error
               pass
        else:
            print("socket error ", e)
        httpd.server_close()
        startWebserver()
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (evoconfig.url, evoconfig.port))


class MyHandler(http.server.BaseHTTPRequestHandler):
    
    def do_HEAD(s):
        
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

    def do_GET(s):
        
        #store instance (this) as global var
        global sf
        sf = s
        
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        
        #Connect to evohome
        
        #URL Parameter commands
        if s.path == '/evopi':
            global ACCESS_URL
            ACCESS_URL ='http://{0}/'.format(s.headers.get('Host'))
            evoConnect()
            getDash()
            
        if s.path.startswith('/get_temp_json'):
            getTempJson()

        if s.path.startswith('/set_temp'):            
            setTemp()

        if s.path.startswith('/cancel_temp_override'):
            cancelTempOverride()
            
        if s.path.startswith('/set_hot_water'):
            setHotWater()
        
        if s.path.startswith('/set_status_normal'):
            setStatusNormal()
            
        if s.path.startswith('/set_status_custom'):
            setStatusCustom()

        if s.path.startswith('/set_status_eco'):
            setStatusEco()

        if s.path.startswith('/set_status_away'):
            setStatusAway()

        if s.path.startswith('/set_status_dayoff'):
            setStatusDayOff()
            
        if s.path.startswith('/set_status_heatingoff'):
            setStatusHeatingOff()
            
        if s.path.startswith('/backup'):
            backup()

        if s.path.startswith('/restore'):
            restore()
        
        if s.path.startswith('/reconnect'):
            evoConnect()
            
        if s.path.startswith('/restart'):
            evoConnect()

        if s.path.startswith('/reset'):
            evoConnect()
            
#Connect to evohome                  
def evoConnect(locationIndex=0):                
    
    global client
    global dCount
    fmt = "%d/%m/%Y %H:%M"
    
    print('Establishing connection to evohome ...')    
    print('{0} - EvoPi is online @ {1}'.format((datetime.now()).strftime(fmt), EVOPI_URL))

    client = EvohomeClient (evoconfig.usr, evoconfig.pw, debug=True)

    #Get the number of devices    
    dCount = 0
    client.locations = [client.locations[locationIndex]] #!TEMP TESTING
    for device in client.temperatures ():
        dCount += 1
        #print device

#    print 'System ID: {0}, Model Type: {1}, System Mode: {2}, Hot Water Mode: {3}, Hot Water State: {4}, Active Faults: {5}'.format(systemId,modelType,currentmode,dhwMode,dhwState,next(iter(activeFaults or []), None))
#    print '\nFull Installation: {0}'.format(fi)
           
#get device temperatures (returns webpage)
def getDash(): 
    
    #Colours
    page_bkgd   = '#2f3030'
    toprow_bkgd = '#6d6d6d'
    dig_text    = '#ccc'
    mode_text   = '#37ff00'
    
    status = client.locations[0].status()
    tcs = status['gateways'][0]['temperatureControlSystems'][0]
    mode = tcs['systemModeStatus']['mode']
    zones = tcs['zones']
    #activeFaults = tcs['activeFaults']
    dhw = tcs['dhw']
    dhwMode = dhw['stateStatus']['mode']
    dhwState = dhw['stateStatus']['state']  

    #print status
    
    table = ['<html >'
             '<head>'
             '<meta http-equiv="refresh" content="300">'
             '<script src="http://code.jquery.com/jquery-latest.js"></script>'
             '<title>EvoPi</title>'
             '<link href="https://fonts.googleapis.com/css?family=Orbitron" rel="stylesheet" type="text/css">'
             '<link href="https://fonts.googleapis.com/css?family=Bungee" rel="stylesheet">'
             '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">'
             '<style>']   
    
    css = (  'body {'
             '  background-color: ' + page_bkgd + ';'
             '}'
             ''
             'table {'
             '  font-family:Century Gothic;'
             '  height:100%;'
             '  width:100%;'
             '  table-layout:fixed;'
#             '  background-color:' + page_bkgd + ';'
             '  border-collapse: separate;'
             '  border-spacing: 20px 10px;'
             '}'
             ''
             '.rounded {'
             '  position: relative;'
             '  border: 0px solid transparent;'
             '  border-radius: 16px;'
             '  padding: 0px;'
             '  box-shadow: 10px 10px 10px black,'
             '   inset 0 10px 10px 1px rgba(255,255,255,0.6),'
             '   inset 0 -10px 30px rgba(0,0,0,0.6),'
             '   inset 10px 0 30px rgba(0,0,0,0.6),'
             '   inset -10px 0 30px rgba(0,0,0,0.6);'
             '}'
             ''
             '.room {'
             '  width: 100%;'
             '  height:0;'
             '  padding-bottom: 50%;'
             '  font-size:1.2vw;'
             '  font-weight:bold;'
             '  font-family: Orbitron;'
             '  word-break:keep-all;'
             '  color: rgba(0,0,0, 0.5);'
             '  text-shadow: 0px 1px 10px rgba(0,0,0,1);'
             '  margin-bottom: 0%;'
             '  -webkit-background-clip: text;'
             '  -moz-background-clip: text;'
             '  background: none;'
             '  background-clip: text;'
             '  border:none;'
             '  background-repeat:no-repeat;'
             '  border: none;'
             '  cursor:pointer;'
             '  overflow: hidden;'
             '  outline:none;'
            #'  border:1px solid black;'
             '}'
             ''
             '.temp {'
             '  height:auto;'
             '  font-size:1.6vw;'
             '  margin: 0 !important;'
             '  color:' + dig_text + ';'
             '  font-family:Orbitron;'
             '  text-shadow: 4px 4px 8px #000000;'
             #' border:1px solid white;'
             '}'
             ''
             '.setpoint {'
             '  height:auto;'
             '  margin: 0 !important;'
             '  font-size:1.6vw;'
             '  color:' + dig_text + ';'
             '  font-family:Orbitron;'
             '  text-shadow: 4px 4px 8px #000000;'
            #'  border:1px solid red;'
             '}'
             ''
             '.button {'
             '  position:absolute;'
             '  margin:auto;'
             '  font-size:4vw;'
             '  top:0;'
             '  left:0;'
             '  bottom:0;'
             '  right:0;'
             '  width:70%;'
             '  color: rgba(0,0,0, 0.5);'
             '  -webkit-background-clip: text;'
             '  -moz-background-clip: text;'
             '  background: none;'
             '  background-clip: text;'
             '  border:none;'
             '  background-repeat:no-repeat;'
             '  border: none;'
             '  cursor:pointer;'
             '  overflow: hidden;'
             '  outline:none;'
            #'  border:1px solid red;'
             '}'
             ''
             '.container {'
             '  position:relative;'
             '  vertical-align:middle;'
             '  text-align: center;'
            #'  border:1px solid yellow;'
             '}'
             ''
             '.screen {'
             '  width: 71%;'
             '  height:0;'
             '  padding-bottom: 60%;'
             '  margin:auto;'
             '  border-radius: 10px;'
             '  border: 2px solid #000000;'
             '  text-align: center;'             
             '  background-color:#383838;'
             '  -webkit-box-shadow: inset 0px 6px 16px 5px rgba(0,0,0,1);'
             '  -moz-box-shadow: inset 0px 6px 16px 5px rgba(0,0,0,1);'
             '  box-shadow: inset 0px 6px 16px 5px rgba(0,0,0,1),'
             '    0px 5px 5px rgba(255,255,255,0.5),'
             '    0px -5px 5px rgba(0,0,0,0.5),'
             '    5px 0px 5px rgba(0,0,0,0.5),'
             '    -5px 0px 5px rgba(0,0,0,0.5);'
             '}'
             ''
             '.screen_text {'
             '  height:auto;'
             '  margin: 0 !important;'
             '  font-size:0.6vw;'
             '  color:#adadad;'
             '  bottom:0;'
             '  font-family:Orbitron;'
             '  text-shadow: 4px 4px 8px #000000;'
            #' border:1px solid red;'
             '}'
             ''
             '.separator {'
             '   height: 2px;'
             '   border:none;'
             '   background-color: transparent;'
             '   background-image: '
             '      linear-gradient(90deg, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0)),'
             '      linear-gradient(90deg, rgba(255,255, 255,0), rgba(255, 255, 255, 1), rgba(255,255,255,0));'
             '   box-shadow: rgba(255,255,255,0.8) 0 0 20px;'
             '   background-repeat: no-repeat;'
             '   background-position: 0 0, 0 1px;'
             '   background-size: 100% 1px;'
            #'  border:1px solid blue;'
             '}'
             ''
             '.flex_container {'
             '  display:flex;'
             '}'
             ''
             '.toprow {'
             '   background-color: ' + toprow_bkgd + ';'
             '   height: 1%;'
             '}'
             ''
             '.flexbox1{'
            #'   border:1px solid green;'
             '  flex-grow: 1;'
             '  text-align: center;'
             '}'
             ''
             '.appTitle{'  
             '  width: 20%;'
             '  text-align: center;'
             '  margin: auto;'
             '  font-size:7vh;'
             '  text-shadow: 0 8px 6px ' + toprow_bkgd +',0 0 0 #000, 0 1px 2px rgba(255,255,255,0.8),0 -3px 8px rgba(0,0,0,0.5),0 0 5px rgba(0,0,0,0.5),0 0 5px rgba(0,0,0,0.5);'
             '  color: rgba(0,0,0, 0.5);'
             '  -webkit-background-clip: text;'
             '  -moz-background-clip: text;'
             '  background-clip: text;'
             '  font-weight: bold;'
#             '  border:1px solid orange;'
             '}'
             ''
             '.engraved {'
             '  text-shadow: 0 8px 6px ' + toprow_bkgd +',0 0 0 #000, 0 1px 5px rgba(255,255,255,0.8), 0 -1px 5px rgba(0,0,0,0.5);'
             '}'
             ''
             '.toprow_button {'
             '  background: none;'
             '  margin: 8% 0 8% 0;'
             '  font-size:5vh;'
             '  color: rgba(0,0,0, 0.5);'
             '  text-shadow: 0 5px 5px ' + toprow_bkgd + ', 0 0 0 #000;'
             '  -webkit-background-clip: text;'
             '  -moz-background-clip: text;'
             '  background-clip: text;'
             '  border:none;'
             '  background-repeat:no-repeat;'
             '  border: none;'
             '  cursor:pointer;'
             '  overflow: hidden;'
             '  outline:none;'
            #'   border:1px solid red;'
             '}'
             ''
             '.modeBtn {'
             '  height:10%;'
             '}'
             '.buttontext{'
             '  background: none;'
             '  font-family:Orbitron;'
             '  margin: 8% 0 0 0;'
             '  color: ' + page_bkgd + ';'
             '  font-size:0.7vw;'
             '  font-weight: bold;'
            #'  border:1px solid blue;'
             '}'
             ''
             '.ledRedOff {'
             '  display: block;'
             '  margin: 0 auto;'
             '  width: 24px;'
             '  height: 24px;'
             '  background-color: #470000;'
             '  border-radius: 50%;'
             '  box-shadow: '
             '    inset #000 0 -1px 15px, '
             '    rgba(0, 0, 0, 0.5) 0 -3px 5px,'
             '    rgba(0, 0, 0, 0.5) -3px 0 5px,'
             '    rgba(0, 0, 0, 0.5) 3px 0 5px,'
             '    rgba(255, 255, 255, 0.5) 0 3px 5px;'
             '}'
             ''
             '.ledRedOn {'
             '  display: none;'
             '  margin: 0 auto;'
             '  width: 24px;'
             '  height: 24px;'
             '  background-color: #F00;'
             '  border-radius: 50%;'
             '  box-shadow: '
             '    inset #441313 0 -3px 14px 2px,'
             '    inset rgba(0, 0, 0, 1) 0 0 5px,'
             '    rgba(255, 0, 0, 1) 0 0 50px,'
             '    rgba(0, 0, 0, 0.5) 0 -3px 5px,'
             '    rgba(0, 0, 0, 0.5) -3px 0 5px,'
             '    rgba(0, 0, 0, 0.5) 3px 0 5px,'
             '    rgba(255, 255, 255, 0.5) 0 3px 5px;'
             '}'
             )
    
    #Top row button commands
    sAuto       = '{0}set_status_normal/'.format(HOST_PORT)
    sAway       = '{0}set_status_away/'.format(HOST_PORT)
    sDayOff     = '{0}set_status_dayoff/'.format(HOST_PORT)
    sCustom     = '{0}set_status_custom/'.format(HOST_PORT)
    sEconomy    = '{0}set_status_eco/'.format(HOST_PORT)
    sHeatOff    = '{0}set_status_heatingoff/'.format(HOST_PORT)
    sBackup     = '{0}backup/'.format(HOST_PORT)
    sRestore    = '{0}restore/'.format(HOST_PORT)

    #Add the CSS styling
    table.append(css)
    
    #Generate the HTML
    head = ( '</style>'
             '</head>'
             '<body onload="setMode()">'
             # JavaScript - get/set Set Point temp
             '<script>'
             ''
             # Sets the relevant Mode to green on startup/refresh
             'function setMode() {'
             '  document.getElementById("mode' + mode + '").style.color = "' + mode_text + '";'
             '}'
             # Get a DIV value and update it with a value
             'function setDiv(div,val) {'
             '  var x = document.getElementById(div).innerHTML;'
             '  return (parseFloat(x) + val).toFixed(1);'
             '}'
             ''
             # Turn a device's LED on/off when user changes temp
             'function toggleLedTemp(off,on,temp,setp) {'
             '   var x = document.getElementById(off);'
             '   var y = document.getElementById(on);'
             '   var t = document.getElementById(temp).innerHTML;'
             '   var s = document.getElementById(setp).innerHTML;'
             '   if (parseFloat(t) >= parseFloat(s)) {'
             '       x.style.display = "block";'
             '       y.style.display = "none";'
             '   } else {'
             '           y.style.display = "block";'
             '       x.style.display = "none";'
             '   }'
            '}'
             ''
             # Turn a device's LED off
             'function offLed(off,on) {'
             '   var x = document.getElementById(off);'
             '   var y = document.getElementById(on);'
             '       x.style.display = "block";'
             '   y.style.display = "none";'
            '}'
             ''
             # Turn a device's LED on
             'function onLed(off,on) {'
             '   var x = document.getElementById(off);'
             '   var y = document.getElementById(on);'
             '   x.style.display = "none";'
             '   y.style.display = "block";'
            '}'
             # Reset all top row buttons to default colour
             'function resetTextColour() {'
             '  var ancestor = document.getElementById("topRowFlex");'
             '  var descendents = ancestor.getElementsByTagName("*");'
             '  var i, e, d;'
             '  for (i = 0; i < descendents.length; ++i) {'
             '     e = descendents[i];'
             '     if(e.tagName == "P"){'
             '       e.style.color = "'+ page_bkgd +'";'
             '     }'
             '  }'
             '}'
             # Click handlers for top row buttons       
             '$(document).ready(function() {'
             # Mode: Auto
             '  $("#btnModeAuto").click(function() {'
             '    $("#modeAuto").load("' + sAuto + '");'
             '    resetTextColour();'
             '    document.getElementById("modeAuto").style.color = "'+ mode_text +'";'
             '    return false;'
             '  });'
             # Mode: Away
             '   $("#btnModeAway").click(function() {'
             '    $("#modeAway").load("' + sAway + '");'
             '    resetTextColour();'
             '    document.getElementById("modeAway").style.color = "'+ mode_text +'";'
             '    return false;'
             '  });'
             # Mode: Day Off
             '   $("#btnModeDayOff").click(function() {'
             '    $("#modeDayOff").load("' + sDayOff + '");'
             '    resetTextColour();'
             '    document.getElementById("modeDayOff").style.color = "'+ mode_text +'";'
             '    return false;'
             '  });'
             # Mode: Custom
             '   $("#btnModeCustom").click(function() {'
             '    $("#modeCustom").load("' + sCustom + '");'
             '    resetTextColour();'
             '    document.getElementById("modeCustom").style.color = "'+ mode_text +'";'
             '    return false;'
             '  });'
             # Mode: Economy
             '   $("#btnModeAutoWithEco").click(function() {'
             '    $("#modeAutoWithEco").load("' + sEconomy + '");'
             '    resetTextColour();'
             '    document.getElementById("modeAutoWithEco").style.color = "'+ mode_text +'";'
             '    return false;'
             '  });'
             # Mode: Heating Off
             '   $("#btnModeHeatingOff").click(function() {'
             '    $("#modeHeatingOff").load("' + sHeatOff + '");'
             '    resetTextColour();'
             '    document.getElementById("modeHeatingOff").style.color = "'+ mode_text +'";'
             '    return false;'
             '  });'
             # Command: Backup
             '   $("#btnModeBackup").click(function() {'
             '    $("#modeBackup").load("' + sBackup + '");'
             '    document.getElementById("modeBackup").style.color = "'+ mode_text +'";'
             '    setTimeout(function(){'
             '      document.getElementById("modeBackup").style.color = "'+ page_bkgd +'";'
             '    }, 2000);'
             '    return false;'
             '  });'
             # Command: Restore
             '   $("#btnModeRestore").click(function() {'
             '    $("#modeRestore").load("' + sRestore + '");'
             '    document.getElementById("modeRestore").style.color = "'+ mode_text +'";'
             '    setTimeout(function(){'
             '      document.getElementById("modeRestore").style.color = "'+ page_bkgd +'";'
             '    }, 2000);'
             '    return false;'
             '  });'
             '});'
             '</script>'
             # Table
             '<table>'
             ' <tr class="toprow">'
             '  <td class="rounded" colspan="' + str(dCount) + '">'
             '   <div id="topRowFlex" class="flex_container">'
             # Button 1
             '    <div class="flexbox1">'
             '      <button type="submit" class="toprow_button">'
             '       <i id="btnModeAuto" class="fa fa-clock-o modeBtn"></i>'
             '       <p id="modeAuto" class="buttontext">Auto</p>'
             '      </button>'
             '    </div>'
             # Button 2
             '    <div class="flexbox1">'
             '      <button type="submit" class="toprow_button">'
             '       <i id="btnModeAway" class="fa fa-sign-out modeBtn"></i>'
             '       <p id="modeAway" class="buttontext">Away</p>'
             '      </button>'
             '    </div>'
             # Button 3
             '    <div class="flexbox1">'
             '      <button type="submit" class="toprow_button">'
             '       <i id="btnModeDayOff" class="fa fa-sign-in modeBtn"></i>'
             '       <p id="modeDayOff" class="buttontext">Day Off</p>'
             '      </button>'
             '    </div>'  
             # Button 4
             '    <div class="flexbox1">'
             '      <button type="submit" class="toprow_button">'
             '       <i id="btnModeCustom" class="fa fa-cogs modeBtn"></i>'
             '       <p id="modeCustom" class="buttontext">Custom</p>'
             '      </button>'
             '    </div>'
             # Title
             '     <div class="appTitle">evoPi</div>'
             # Button 5
             '    <div class="flexbox1">'
             '      <button type="submit" class="toprow_button">'
             '       <i id="btnModeAutoWithEco" class="fa fa-gbp modeBtn"></i>'
             '       <p id="modeAutoWithEco" class="buttontext">Economy</p>'
             '      </button>'
             '    </div>'
             # Button 6
             '    <div class="flexbox1">'
             '      <button type="submit" class="toprow_button">'
             '       <i id="btnModeHeatingOff" class="fa fa-power-off modeBtn"></i>'
             '       <p id="modeHeatingOff" class="buttontext">Heating Off</p>'
             '      </button>'
             '    </div>'
             # Button 7
             '    <div class="flexbox1">'
             '      <button type="submit" class="toprow_button">'
             '       <i id="btnModeBackup" class="fa fa-cloud-download modeBtn"></i>'
             '       <p id="modeBackup" class="buttontext">Backup</p>'
             '      </button>'
             '    </div>'
             # Button 8
             '    <div class="flexbox1">'
             '      <button type="submit" class="toprow_button">'
             '       <i id="btnModeRestore" class="fa fa-cloud-upload modeBtn"></i>'
             '       <p id="modeRestore" class="buttontext">Restore</p>'
             '      </button>'
             #
             '    </div>'
             '   </div>'
             '  </td>'
             ' </tr>'
             ' <tr>'
             )
    
    table.append(head)    
    
    devId = 0
        
    #Start loop through devices
    for device in client.temperatures ():
        
        #Get device info
        dName = device['name']
        dTemp = device['temp']
        dSetp = device['setpoint']
        dTherm = device['thermostat']
        dHwsp = 60.0 #hot water setpoint       
        
        #Create vars
        room = ''
        temp = 0
        setp = 0
        oLedOn = ''
        oLedOff = ''
        jsClick = ''
        btnUp = ''
        btnDn = ''
        swPoint = ''
        
        #Led style
        ledHide = 'display: none;'
        ledShow = 'display: block;'
                
        #Heating
        if dTherm == 'EMEA_ZONE':            
            
            room = dName
            temp = dTemp
            setp = dSetp
            btnUp = 'fa fa-arrow-circle-up'
            btnDn = 'fa fa-arrow-circle-down'
            devMode = getMode(zones[devId]['setpointStatus']['setpointMode'])
            
            #Get next switchpoint (schedule)                
            lst = getNextSwitchPoint(devId,dTherm)
            swPoint = '{0} > {1}'.format(lst['TimeOfDay'][:-3],lst['heatSetpoint']) 
            
            #Heating led on
            if temp < setp:
                oLedOn = ledShow
                oLedOff = ledHide
            else:
                oLedOn = ledHide
                oLedOff = ledShow
                
            #Setup the js for the heating      
            jsClick = (
                     '<script>'
                     '$(document).ready(function() {'            
                     '  $("#btnPlus' + rm(room) + '").click(function() {'
                     '    var url = "' + '{0}set_temp/{1}/'.format(ACCESS_URL,pc(room)) + '" + setDiv("txtSetPoint' + rm(room) + '",1);'
                     '    $("#txtSetPoint' + rm(room) + '").load(url);'
                     '    document.getElementById("txtMode' + rm(room) + '").innerHTML = "OVERRIDE";'
                     '    document.getElementById("txtSetPoint' + rm(room) + '").style.color = "#bc3b03";'
                     '    setTimeout(function(){'
                     '      toggleLedTemp("ledOff' + rm(room) + '","ledOn' + rm(room) + '","txtTemp' + rm(room) + '","txtSetPoint' + rm(room) + '");'
                     '      document.getElementById("txtSetPoint' + rm(room) + '").style.color = "' + dig_text + '";'
                     '    }, 2000);'
                     '    return false;'
                     '  });'
                     '  $("#btnMinus' + rm(room) + '").click(function() {'
                     '    var url = "' + '{0}set_temp/{1}/'.format(ACCESS_URL,pc(room)) + '" + setDiv("txtSetPoint' + rm(room) + '",-1);'
                     '    $("#txtSetPoint' + rm(room) + '").load(url);'
                     '    document.getElementById("txtMode' + rm(room) + '").innerHTML = "OVERRIDE";'
                     '    document.getElementById("txtSetPoint' + rm(room) + '").style.color = "#036bbc";'
                     '    setTimeout(function(){'
                     '      toggleLedTemp("ledOff' + rm(room) + '","ledOn' + rm(room) + '","txtTemp' + rm(room) + '","txtSetPoint' + rm(room) + '");'
                     '      document.getElementById("txtSetPoint' + rm(room) + '").style.color = "' + dig_text + '";'
                     '    }, 2000);'
                     '    return false;'
                     '  });' 
                     '});'
                     '</script>'
                     )  
        
            #print jsClick + "\n\n"
        
            #Increment room id
            devId += 1
                
        #Hot water
        else:
            
            room = "Hot Water"
            temp = dTemp
            setp = dHwsp
            btnUp = 'fa fa-power-off'
            btnDn = 'fa fa-clock-o'
            devMode = getMode(dhwMode)
            
            #Get next switchpoint (schedule)                
            lst = getNextSwitchPoint(devId,dTherm)
            swPoint = '{0} > {1}'.format(lst['TimeOfDay'][:-3],lst['DhwState'])
            
            #Hot water led on
            if dhwState == "On":
               oLedOn = ledShow
               oLedOff = ledHide 
            else:
               oLedOn = ledHide
               oLedOff = ledShow
        
            #Setup the js for the hot water      
            jsClick = (
                 '<script>'
                 '$(document).ready(function() {'            
                 '  $("#btnPlus' + rm(room) + '").click(function() {'
                 '    var url = "' + '{0}set_hot_water/boost'.format(ACCESS_URL) + '";'
                 '    $("#txtMode' + rm(room) + '").load(url);'
                 '    setTimeout(function(){'
                 '      onLed("ledOff' + rm(room) + '","ledOn' + rm(room) + '");'
                 '    }, 2000);'
                 '    return false;'
                 '  });'
                 '  $("#btnMinus' + rm(room) + '").click(function() {'
                 '    var url = "' + '{0}set_hot_water/auto'.format(ACCESS_URL) + '";'
                 '    $("#txtMode' + rm(room) + '").load(url);'
                 '    setTimeout(function(){'
                 '      offLed("ledOff' + rm(room) + '","ledOn' + rm(room) + '");'
                 '    }, 2000);'
                 '    return false;'
                 '  });' 
                 '});'
                 '</script>'
                 )  
            #print jsClick + "\n\n"

        #Create device columns
        col = (  '<td class="rounded" style="padding: 0 10px 0 10px; background-color:' + sFont(temp,setp) + '; width:(100/' + str(dCount) + ')%;">'
                 '<iframe name="iframe" style="display:none;"></iframe>'
                 # Led
                 ' <div class="container">'
                 '  <div id="ledOff' + rm(room) + '" style="' + oLedOff + '" class="ledRedOff"></div>'
                 ' </div>'
                 ' <div class="container">'
                 '  <div id="ledOn' + rm(room) + '" style="' + oLedOn + '" class="ledRedOn"></div>'
                 ' </div>'
                 # Room name
                 ' <div class="container">'
                 '  <p class="room" style="text-shadow: 0 8px 6px ' + sFont(temp,setp) +',0 0 0 #000, 0 1px 5px rgba(255,255,255,0.8), 0 -1px 5px rgba(0,0,0,0.5)">' + room + '</p>'
                 ' </div>'
                 # Separator
                 ' <div class="separator"></div>'
                 # Button up
                 ' <div class="container" style="padding-top:50%;padding-bottom:50%;">'
                 '   <button type="submit" class="button" style="text-shadow: 0 8px 6px ' + sFont(temp,setp) +',0 0 0 #000, 0 3px 10px rgba(255,255,255,1), 0 -3px 5px rgba(0,0,0,0.5)";>'
                 '    <i id="btnPlus' + rm(room) + '" class="' + btnUp + '"></i>'
                 '   </button>'
                 ' </div>'
                 # Temp screen
                 ' <div class="container">'
                 '  <div class="screen">'
                 '   <p class="screen_text" style="padding-top:10%;">Temperature</p>'
                 '   <p id="txtTemp' + rm(room) + '" class="temp">' + str(temp) + '</p>'
                 '   <p id="txtMode' + rm(room) + '" class="screen_text">' + str(devMode) + '</p>'
                 '  </div>'
                 ' </div>' 
                 # Button down
                 ' <div class="container" style="padding-top:50%;padding-bottom:50%;">'
                 '   <button type="submit" class="button" style="text-shadow: 0 8px 6px ' + sFont(temp,setp) +',0 0 0 #000, 0 3px 10px rgba(255,255,255,1), 0 -3px 5px rgba(0,0,0,0.5)";>'
                 '    <i id="btnMinus' + rm(room) + '" class="' + btnDn + '"></i>'
                 '   </button>'
                 ' </div>'
                 # Separator
                 ' <div class="separator"></div>'
                 # Set point screen
                 ' <div class="container" style="padding-top:20%">'                 
                 '  <div class="screen">'
                 '   <p class="screen_text" style="padding-top:10%;">Set Point</p>'
                 '   <p id="txtSetPoint' + rm(room) + '" class="setpoint">' + str(setp) + '</p>'
                 '   <p id="txtSwitchPoint' + rm(room) + '" class="screen_text">' + swPoint + '</p>'
                 '  </div>'
                 ' </div>'
                 '</td>')  
        
        
        table.append(col)
        table.append(jsClick)        
        
        #Next device
    
    #Loop complete
    
    table.append('</tr></table></body></html>')    
    sf.wfile.write(''.join(table).encode())

    
def getNextSwitchPoint(devId, devType):
    
    zone = None
    
    if devType == 'EMEA_ZONE': #Heating
        zone = client.locations[0]._gateways[0]._control_systems[0]._zones[devId]    
    else: # Hot water
        zone = client.locations[0]._gateways[0]._control_systems[0].hotwater
    
    #Navigate through the schedule JSON                         
    wkSchedule = zone.schedule()
    today = datetime.now()
    weekday = (today.weekday() + 1) % 7
    timeNow = today.time().strftime("%H:%M:%S")
    daySchedule = wkSchedule['DailySchedules'][weekday]
    switchPoints = daySchedule['Switchpoints']
    swpList = []
    
    #Find the next switchpoint today
    for switchpoint in switchPoints:
        if timeNow < switchpoint['TimeOfDay']:            
            swpList.append(switchpoint)  
            
    try:
        #return the next one today
        return swpList[0]
    except IndexError:
        #return the first one today
        for switchpoint in switchPoints:           
            swpList.append(switchpoint)
        return swpList[0]
    
#Replace heating modes with friendly names
def getMode(m):
    if m == 'FollowSchedule':
        return 'Auto'
    elif m == 'TemporaryOverride':
        return 'Override'
    elif m == 'PermanentOverride':
        return 'Permanent'

#Replace spaces in device name with %20
def pc(dev):
    return dev.replace(' ','%20')

#Remove spaces in device name
def rm(dev):
    return dev.replace(' ','')

#Return column colour for temp
def sFont(temp, setp):
    
    i = temp - setp
    
    if i < - 2.0:
        return '#0054E5'
    elif i == -2.0:
        return '#00A3E1'
    elif i == -1.5:
        return '#00DDC9'
    elif i == -1.0:
        return '#00D977'
    elif i == -0.5:
        return '#00D528'
    elif i == 0.0:
        return '#24D200'
    elif i == 0.5:
        return '#6ECE00'
    elif i == 1.0:
        return '#B5CA00'
    elif i == 1.5:
        return '#C69300'
    elif i == 2.0:
        return '#C24A00'
    elif i > 2.0:
        return '#C24A00'

#Returns the image tag of an image file
def getImageTag(fName):
    uri = open(fName, 'rb').read().encode('base64').replace('\n', '')
    return 'src="data:image/png;base64,{0}"'.format(uri)

#get device temperatures (returns json)
def getTempJson():
    
    global myDevices
    myDevices = ''
    myDevices += '{"devices": ['
    
    for device in client.temperatures ():
        myDevices += str(device) + ','
        
    myDevices = myDevices[:-1] + ']}'
    
    sf.wfile.write(myDevices
                  .replace("'",'"')
                  .replace(': u"',': "')
                  )

def getSetPoint(dev):
    for device in client.temperatures ():
        if device['name'] == dev:
            return device['setpoint']

#set temp of a zone
def setTemp():

    urlStr = (sf.path.replace('?','')).split('/')
    argCount = len(urlStr)
    room = urlStr[2].replace('%20',' ').replace('_',' ')
    temp = urlStr[3]
    zone = client.locations[0]._gateways[0]._control_systems[0].zones[room]

    #example: http://[your-ip-address-and-port]/settemp/Kitchen/23/2017,05,04,21,30

    #includes room, temp and time - boost until time
    if argCount > 4 and urlStr[4]:
        dt = datetime.strptime(urlStr[4], "%Y,%m,%d,%H,%M")
        zone.set_temperature(temp, dt + timedelta(hours=-2)) # is -1 hour
        sf.wfile.write(temp)

    #includes room and temp only - boost 1 hour
    else:
        #Note: honeywell time is +1 hour
        now = datetime.now()
        zone.set_temperature(temp, now  + timedelta(hours=0)) # is +1 hour
        sf.wfile.write(temp)

def cancelTempOverride():
    
    #http://[your-ip-address-and-port]/cancel_temp_override/Kitchen
    urlStr = (sf.path.replace('?','')).split('/')
    room = urlStr[2].replace('%20',' ').replace('_',' ')
    client.cancel_temp_override(room)


#set domestic hot water
def setHotWater():
    
    #example: http://[your-ip-address-and-port]/set_hot_water/on/2017,04,28,23,30/
    
    client_dhw = client._get_single_heating_system().hotwater    
    urlStr = sf.path.split('/')
    argCount = len(urlStr)
    state = urlStr[2]
    
    if state == 'on':
        
        #Hot water on until a set time
        if argCount > 3 and urlStr[3]:
            dt = datetime.strptime(urlStr[3], "%Y,%m,%d,%H,%M")
            client_dhw.set_dhw_on(dt + timedelta(hours=-1))
            sf.wfile.write('Override')
            
        #Hot water on permanent 
        else:
            client_dhw.set_dhw_on() 
            sf.wfile.write('On')
            
    elif state == 'off':
        
        #Hot water off until a set time
        if argCount > 3 and urlStr[3]:
            dt = datetime.strptime(urlStr[3], "%Y,%m,%d,%H,%M")
            #Note: honeywell time is +1 hour, compensate
            client_dhw.set_dhw_off(dt + timedelta(hours=-1))
            sf.wfile.write('Override')
            
        #Hot water off permanent 
        else:
            client_dhw.set_dhw_off() 
            sf.wfile.write('On')
            
    elif state == 'boost':
        
        #example: http://[your-ip-address-and-port]/set_hot_water/boost/2/
        now = datetime.now()     
        
        #Hot water boost by 'n' hours
        if argCount > 3 and urlStr[3]:
            boost = float(urlStr[3])
            client_dhw.set_dhw_on(now  + timedelta(hours=boost))
            sf.wfile.write('Override ' + boost)
            
        #Hot water boost by 1 hour 
        #example: http://[your-ip-address-and-port]/set_hot_water/boost
        else:
            client_dhw.set_dhw_on(now  + timedelta(hours=1))
            sf.wfile.write('Override')
    
    elif state == 'auto':
        
        #example: http://[your-ip-address-and-port]/set_hot_water/auto
        client_dhw.set_dhw_auto()
        sf.wfile.write('Auto')
    
#Use the normal program
def setStatusNormal():
    client.set_status_normal()
    sf.wfile.write('Normal')
    
#Use the custom program
def setStatusCustom():
    client.set_status_custom()
    sf.wfile.write('Custom')

#Reduce all temperatures by 3 degrees
def setStatusEco():
    client.set_status_eco()
    sf.wfile.write('Economy')

#Heating and hot water off
def setStatusAway():
    client.set_status_away()
    sf.wfile.write('Away')

#Use weekend profile
def setStatusDayOff():
    client.set_status_dayoff()
    sf.wfile.write('Day Off')

#Heating off, hot water on
def setStatusHeatingOff():
    client.set_status_heatingoff()
    sf.wfile.write('Heating Off')
    
#backup evohome schedules
def backup():
    
    client.zone_schedules_backup(loc)
    try:
        sf.wfile.write('Success: schedule backed up to: ' + loc)
    except:
        sf.wfile.write('Fail: schedule could not be backed up to: ' + loc)

#restore evohome schedules
def restore():

    client.zone_schedules_restore('/home/pi/Documents/myschedules.json')
    try:
        sf.wfile.write('Success: schedule restored from: ' + loc)
    except:
        sf.wfile.write('Fail: schedule could not be  restored from: ' + loc)

if __name__ == '__main__':
    startWebserver()
