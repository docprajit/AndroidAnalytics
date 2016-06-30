'''
Copyright (C) 2012  Diego Torres Milano
Created on May 5, 2012

@author: diego

Modified example from Diego to suit project purpose.
Usage: python automateInstallationOfApp.py
'''

import sys
import os
import time

try:
    sys.path.append(os.path.join(os.environ['ANDROID_VIEW_CLIENT_HOME'], 'src'))
except:
    pass

from com.dtmilano.android.viewclient import ViewClient

def launchApp():
    package = 'edu.umbc.cs.ebiquity.autoinstallerapp'
    activity = 'edu.umbc.cs.ebiquity.autoinstallerapp.ui.activity.MainActivity'
    component = package + "/" + activity

    device, serialno = ViewClient.connectToDeviceOrExit(serialno='192.168.173.101:5555')
    device.startActivity(component=component)
    time.sleep(3)
    return device, serialno

def getViewClient(device, serialno):
    viewClient = ViewClient(device, serialno)
    return viewClient

def clickOnTopApp(viewClient):
    appListView = viewClient.findViewByIdOrRaise('edu.umbc.cs.ebiquity.autoinstallerapp:id/list')
    visibleAppList = []
    for app in viewClient.findViewsWithAttribute('class', 'android.widget.TextView', root=appListView):
        visibleAppList.append(app.getText())

    firstAppLink = viewClient.findViewWithText(visibleAppList[0])
    firstAppLink.touch()
    return firstAppLink.getText()

def installApp(viewClient):
    installButton = viewClient.findViewWithTextOrRaise('INSTALL')
    installButton.touch()

def acceptInstallApp(viewClient):
    installButton = viewClient.findViewWithTextOrRaise('ACCEPT')
    installButton.touch()

def getApps():
    device, serialno = launchApp()
    app = clickOnTopApp(getViewClient(device, serialno))
    time.sleep(3)
    installApp(getViewClient(device, serialno))
    time.sleep(3)
    acceptInstallApp(getViewClient(device, serialno))
    print app

def main(argv):
    if len(sys.argv) != 1:
        sys.stderr.write('Usage: python automateInstallationOfApp.py\n')
        sys.exit(1)

    startTime = time.time()
    getApps()
    executionTime = str((time.time()-startTime)*1000)
    print executionTime

if __name__ == "__main__":
    sys.exit(main(sys.argv))