# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MakeOSMRoutableNetwork
                                 A QGIS plugin
 Make OSM Routable Network
                             -------------------
        begin                : 2017-08-25
        copyright            : (C) 2017 by Isaac Boates
        email                : iboates@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MakeOSMRoutableNetwork class from file MakeOSMRoutableNetwork.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .make_osm_routable_network import MakeOSMRoutableNetwork
    return MakeOSMRoutableNetwork(iface)
