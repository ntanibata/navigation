#!/usr/bin/python

"""
**************************************************************************
* @licence app begin@
* SPDX-License-Identifier: MPL-2.0
*
* \copyright Copyright (C) 2014, XS Embedded GmbH
*
* \file simulation-dashboard.py
*
* \brief This simple test shows how the route calculation 
*              could be easily tested using a python script
*
* \author Marco Residori <marco.residori@xse.de>
*
* \version 1.0
*
* This Source Code Form is subject to the terms of the
* Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed with
# this file, You can obtain one at http://mozilla.org/MPL/2.0/.
* List of changes:
* <date>, <name>, <description of change>
*
* @licence end@
**************************************************************************
"""


import dbus
import gobject
import dbus.mainloop.glib

#constants as defined in the Navigation API
LATITUDE = 0x00a0
LONGITUDE = 0x00a1
TOTAL_DISTANCE = 0x018f

print '\n--------------------------'
print 'Route Calculation Test'
print '--------------------------\n'

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True) 

#connect to session bus
bus = dbus.SessionBus()

#signal receiver
def catchall_route_calculation_signals_handler(routeHandle, status, percentage):
    print 'Route Calculation: ' + str(int(percentage)) + ' %'
    if int(percentage) == 100:
        #get route overview
        overview = routing_interface.GetRouteOverview(dbus.UInt32(routehandle),dbus.Array([dbus.UInt16(399)]))
        #retrieve distance 
        totalDistance = int(overview[dbus.UInt16(TOTAL_DISTANCE)])
        print 'Total Distance: ' + str(totalDistance) + ' m'
        #check distance
        if totalDistance < 100000 or totalDistance > 150000:
            print '\nTest FAILED\n'
        else:
            print '\nTest PASSED\n'
        loop.quit()

#add signal receiver
bus.add_signal_receiver(catchall_route_calculation_signals_handler, \
                        dbus_interface = "org.genivi.navigationcore.Routing", \
                        signal_name = "RouteCalculationProgressUpdate")

#timeout
def timeout():
    print 'Timeout Expired'
    print '\nTest FAILED\n'
    loop.quit()

session = bus.get_object('org.genivi.navigationcore.Session','/org/genivi/navigationcore')
session_interface = dbus.Interface(session, dbus_interface='org.genivi.navigationcore.Session')

#get session handle
sessionhandle = session_interface.CreateSession(dbus.String("test route calculation"))
print 'Session handle: ' + str(sessionhandle)

routing_obj = bus.get_object('org.genivi.navigationcore.Routing','/org/genivi/navigationcore')
routing_interface = dbus.Interface(routing_obj, dbus_interface='org.genivi.navigationcore.Routing')

#get route handle
routehandle = routing_interface.CreateRoute(dbus.UInt32(sessionhandle)) 
print 'Route handle: ' + str(routehandle)

#route Zuerich->Bern (125Km)
lat1 = 47.3673
lon1 = 8.5500
lat2 = 46.9479
lon2 = 7.4446

print 'Calculating route from \
A(' + str(lat1) + ',' + str(lon1) + ') to \
B(' + str(lat2) + ',' + str(lon2) + ')' 

#set waypoints
routing_interface.SetWaypoints(dbus.UInt32(sessionhandle), \
                               dbus.UInt32(routehandle), \
                               dbus.Boolean(0), \
                               dbus.Array([ \
                                    dbus.Dictionary({dbus.UInt16(LATITUDE):dbus.Double(lat1),dbus.UInt16(LONGITUDE):dbus.Double(lon1)}), \
                                    dbus.Dictionary({dbus.UInt16(LATITUDE):dbus.Double(lat2),dbus.UInt16(LONGITUDE):dbus.Double(lon2)}) \
                               ]) \
                               )

#calculate route
routing_interface.CalculateRoute(dbus.UInt32(sessionhandle),dbus.UInt32(routehandle))

#main loop 
gobject.timeout_add(5000, timeout)
loop = gobject.MainLoop()
loop.run()


