# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MakeOSMRoutableNetwork
                                 A QGIS plugin
 Make OSM Routable Network
                              -------------------
        begin                : 2017-08-25
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Isaac Boates
        email                : iboates@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Need this because Python 2 automatically imports version 1 from the Qt python API, but we need to force it to use version 2
import sip
sip.setapi('QDate', 2)
sip.setapi('QDateTime', 2)
sip.setapi('QString', 2)
sip.setapi('QTextStream', 2)
sip.setapi('QTime', 2)
sip.setapi('QUrl', 2)
sip.setapi('QVariant', 2)

from PyQt4 import QtGui, QtCore, QtSql
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QComboBox, QListWidget, QListWidgetItem, QFileDialog
from PyQt4.QtSql import QSqlDatabase
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsPoint
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from make_osm_routable_network_dialog import MakeOSMRoutableNetworkDialog
import os.path
import urllib
import bz2
import subprocess
import psycopg2
from psycopg2 import connect as dbconnect, sql
from os import remove
import sys
import webbrowser


class MakeOSMRoutableNetwork:
    """QGIS Plugin Implementation."""

    # Lists of constant subregion names

    REGIONS = {
        "Africa": {
            "None": {"None": ["None"]},
            "Algeria": {"None": ["None"]},
            "Angola": {"None": ["None"]},
            "Benin": {"None": ["None"]},
            "Botswana": {"None": ["None"]},
            "Burkina Faso": {"None": ["None"]},
            "Burundi": {"None": ["None"]},
            "Cameroon": {"None": ["None"]},
            "Canary Islands": {"None": ["None"]},
            "Cape Verde": {"None": ["None"]},
            "Central African Republic": {"None": ["None"]},
            "Chad": {"None": ["None"]},
            "Comores": {"None": ["None"]},
            "Congo (Republic/Brazzaville)": {"None": ["None"]}, # EXCEPTION
            "Congo (Democratic Republic/Kinshasa)": {"None": ["None"]}, # EXCEPTION
            "Djibouti": {"None": ["None"]},
            "Egypt": {"None": ["None"]},
            "Equatorial Guinea": {"None": ["None"]},
            "Eritrea": {"None": ["None"]},
            "Ethiopia": {"None": ["None"]},
            "Gabon": {"None": ["None"]},
            "Ghana": {"None": ["None"]},
            "Guinea": {"None": ["None"]},
            "Guinea-Bissau": {"None": ["None"]},
            "Ivory Coast": {"None": ["None"]},
            "Kenya": {"None": ["None"]},
            "Lesotho": {"None": ["None"]},
            "Liberia": {"None": ["None"]},
            "Libya": {"None": ["None"]},
            "Madagascar": {"None": ["None"]},
            "Malawi": {"None": ["None"]},
            "Mali": {"None": ["None"]},
            "Mauritania": {"None": ["None"]},
            "Mauritius": {"None": ["None"]},
            "Morocco": {"None": ["None"]},
            "Mozambique": {"None": ["None"]},
            "Namibia": {"None": ["None"]},
            "Niger": {"None": ["None"]},
            "Nigeria": {"None": ["None"]},
            "Rwanda": {"None": ["None"]},
            "Saint Helena, Ascension, and Tristan da Cunha": {"None": ["None"]},
            "Sao Tome and Principe": {"None": ["None"]},
            "Senegal and Gambia": {"None": ["None"]},
            "Seychelles": {"None": ["None"]},
            "Sierra Leone": {"None": ["None"]},
            "Somalia": {"None": ["None"]},
            "South Africa": {"None": ["None"]},
            "South Sudan": {"None": ["None"]},
            "Sudan": {"None": ["None"]},
            "Swaziland": {"None": ["None"]},
            "Tanzania": {"None": ["None"]},
            "Togo": {"None": ["None"]},
            "Tunisia": {"None": ["None"]},
            "Uganda": {"None": ["None"]},
            "Zambia": {"None": ["None"]},
            "Zimbabwe": {"None": ["None"]},
            "South Africa (includes Lesotho)": {"None": ["None"]},
        },
        "Antarctica": {
            "None": {"None": ["None"]}
        },
        "Asia": {
            "None": {"None": ["None"]},
            "Afghanistan": {"None": ["None"]},
            "Azerbaijan": {"None": ["None"]},
            "Bangladesh": {"None": ["None"]},
            "Cambodia": {"None": ["None"]},
            "China": {"None": ["None"]},
            "GCC States": {"None": ["None"]},
            "India": {"None": ["None"]},
            "Indonesia": {"None": ["None"]},
            "Iran": {"None": ["None"]},
            "Iraq": {"None": ["None"]},
            "Israel and Palestine": {"None": ["None"]},
            "Japan": {"None": ["None"]},
            "Jordan": {"None": ["None"]},
            "Kazakhstan": {"None": ["None"]},
            "Kyrgyzstan": {"None": ["None"]},
            "Lebanon": {"None": ["None"]},
            "Malaysia, Singapore, and Brunei": {"None": ["None"]},  # EXCEPTION
            "Maldives": {"None": ["None"]},
            "Mongolia": {"None": ["None"]},
            "Myanmar (a.k.a. Burma)": {"None": ["None"]},  # EXCEPTION
            "Nepal": {"None": ["None"]},
            "North Korea": {"None": ["None"]},
            "Pakistan": {"None": ["None"]},
            "Philippines": {"None": ["None"]},
            "South Korea": {"None": ["None"]},
            "Sri Lanka": {"None": ["None"]},
            "Syria": {"None": ["None"]},
            "Taiwan": {"None": ["None"]},
            "Tajikistan": {"None": ["None"]},
            "Thailand": {"None": ["None"]},
            "Turkmenistan": {"None": ["None"]},
            "Uzbekistan": {"None": ["None"]},
            "Vietnam": {"None": ["None"]},
            "Yemen": {"None": ["None"]},
        },
        "Australia and Oceania": {
            "None": {"None": ["None"]},
            "Australia": {"None": ["None"]},
            "Fiji": {"None": ["None"]},
            "New Caledonia": {"None": ["None"]},
            "New Zealand": {"None": ["None"]},
        },
        "Central America": {
            "None": {"None": ["None"]},
            "Belize": {"None": ["None"]},
            "Cuba": {"None": ["None"]},
            "Guatemala": {"None": ["None"]},
            "Haiti and Dominican Republic": {"None": ["None"]},  # EXCEPTION
            "Nicaragua": {"None": ["None"]},
        },
        "Europe": {
            "None": {"None": ["None"]},
            "Albania": {"None": ["None"]},
            "Andorra": {"None": ["None"]},
            "Austria": {"None": ["None"]},
            "Azores": {"None": ["None"]},
            "Belarus": {"None": ["None"]},
            "Belgium": {"None": ["None"]},
            "Bosnia-Herzegovina": {"None": ["None"]},
            "Bulgaria": {"None": ["None"]},
            "Croatia": {"None": ["None"]},
            "Cyprus": {"None": ["None"]},
            "Czech Republic": {"None": ["None"]},
            "Denmark": {"None": ["None"]},
            "Estonia": {"None": ["None"]},
            "Faroe Islands": {"None": ["None"]},
            "Finland": {"None": ["None"]},
            "France": {
                "None": ["None"],
                "Alsace": ["None"],
                "Aquitaine": ["None"],
                "Auvergne": ["None"],
                "Basse-Normandie": ["None"],
                "Bourgogne": ["None"],
                "Bretagne": ["None"],
                "Centre": ["None"],
                "Champagne Ardenne": ["None"],
                "Corse": ["None"],
                "Franche Comte": ["None"],
                "Guadeloupe": ["None"],
                "Guyane": ["None"],
                "Haute-Normandie": ["None"],
                "Ile-de-France": ["None"],
                "Languedoc-Roussillon": ["None"],
                "Limousin": ["None"],
                "Lorraine": ["None"],
                "Martinique": ["None"],
                "Mayotte": ["None"],
                "Midi-Pyrenees": ["None"],
                "Nord-Pas-de-Calais": ["None"],
                "Pays de la Loire": ["None"],
                "Picardie": ["None"],
                "Poitou-Charentes": ["None"],
                "Provence Alpes-Cote-d'Azur": ["None"],
                "Reunion": ["None"],
                "Rhone-Alpes": ["None"]
            },
            "Georgia": {"None": ["None"]},
            "Germany": {
                "None": ["None"],
                "Baden-Wuerttemberg": [
                    "None",
                    "Regierungsbezirk Freiburg", # EXCEPTION
                    "Regierungsbezirk Karlsruhe", # EXCEPTION
                    "Regierungsbezirk Stuttgart", # EXCEPTION
                    "Regierungsbezirk Tuebingen", # EXCEPTION
                ],
                "Bayern": [
                    "None",
                    "Mittelfranken",
                    "Niederbayern",
                    "Oberbayern",
                    "Oberfranken",
                    "Oberpfalz",
                    "Schwaben",
                    "Unterfranken",
                ],
                "Berlin": ["None"],
                "Brandbenburg (mit Berlin)": ["None"],
                "Bremen": ["None"],
                "Hamburg": ["None"],
                "Hessen": ["None"],
                "Mecklenburg-Vorpommern": ["None"],
                "Niedersachsen": ["None"],
                "Nordrhein-Westfalen": [
                    "None",
                    "Regierungsbezirk Arnsberg", # EXCEPTION
                    "Regierungsbezirk Detmold",  # EXCEPTION
                    "Regierungsbezirk Duesseldorf",  # EXCEPTION
                    "Regierungsbezirk Koeln",  # EXCEPTION
                    "Regierungsbezirk Muenster",  # EXCEPTION
                ],
                "Rheinland-Pfalz": ["None"],
                "Saarland": ["None"],
                "Sachsen": ["None"],
                "Sachsen-Anhalt": ["None"],
                "Schleswig-Holstein": ["None"],
                "Thueringen": ["None"],
            },
            "Great Britain": {
                "None": ["None"],
                "England": [
                    "None",
                    "Berkshire",
                    "Buckinghamshire",
                    "Cambridgeshire",
                    "Cheshire",
                    "Cornwall",
                    "Cumbria",
                    "Derbyshire",
                    "Devon",
                    "Dorset",
                    "East Sussex",
                    "East Yorkshire with Hull",
                    "Essex",
                    "Gloucestershire",
                    "Greater London",
                    "Greater Manchester",
                    "Hampshire",
                    "Herefordshire",
                    "Hertfordshire",
                    "Isle of Wight",
                    "Kent",
                    "Lancashire",
                    "Leicestershire",
                    "Norfolk",
                    "North Yorkshire",
                    "Northumberland",
                    "Nottinghamshire",
                    "Oxfordshire",
                    "Shropshire",
                    "Somerset",
                    "South Yorkshire",
                    "Staffordshire",
                    "Suffolk",
                    "Surrey",
                    "West Midlands",
                    "West Sussex",
                    "West Yorkshire",
                    "Wiltshire",
                    "worcestershire",
                ],
                "Scotland": ["None"],
                "Wales": ["None"],
            },
            "Greece": {"None": ["None"]},
            "Hungary": {"None": ["None"]},
            "Iceland": {"None": ["None"]},
            "Ireland and Northern Ireland": {"None": ["None"]},
            "Isle of Man": {"None": ["None"]},
            "Italy": {
                "None": ["None"],
                "Centro": ["None"],
                "Isole": ["None"],
                "Nord-Est": ["None"],
                "Nord-Ovest": ["None"],
                "Sud": ["None"],
            },
            "Kosovo": {"None": ["None"]},
            "Latvia": {"None": ["None"]},
            "Liechtenstein": {"None": ["None"]},
            "Lithuania": {"None": ["None"]},
            "Luxembourg": {"None": ["None"]},
            "Macedonia": {"None": ["None"]},
            "Malta": {"None": ["None"]},
            "Moldova": {"None": ["None"]},
            "Monaco": {"None": ["None"]},
            "Montenegro": {"None": ["None"]},
            "Netherlands": {"None": ["None"]},
            "Norway": {"None": ["None"]},
            "Poland": {
                "None": ["None"],
                "Lower Silesian Voivodeship": ["None"], # EXCEPTION
                "Kuyavian-Pomeranian Voivodeship": ["None"], # EXCEPTION
                "Łódź Voivodeship": ["None"], # EXCEPTION
                "Lublin Voivodeship": ["None"], # EXCEPTION
                "Lubusz Voivodeship": ["None"], # EXCEPTION
                "Lesser Poland Voivodeship": ["None"], # EXCEPTION
                "Mazovian Voivodeship": ["None"], # EXCEPTION
                "Opole Voivodeship": ["None"], # EXCEPTION # EXCEPTION
                "Subcarpathian Voivodeship": ["None"], # EXCEPTION
                "Podlaskie Voivodeship": ["None"], # EXCEPTION
                "Pomeranian Voivodeship": ["None"], # EXCEPTION
                "Silesian Voivodeship": ["None"], # EXCEPTION
                "Świętokrzyskie Voivodeship": ["None"], # EXCEPTION
                "Warmian-Masurian Voivodeship": ["None"], # EXCEPTION
                "Greater Poland Voivodeship": ["None"], # EXCEPTION
                "West Pomeranian Voivodeship": ["None"], # EXCEPTION
            },
            "Portugal": {"None": ["None"]},
            "Romania": {"None": ["None"]},
            "Serbia": {"None": ["None"]},
            "Slovakia": {"None": ["None"]},
            "Slovenia": {"None": ["None"]},
            "Spain": {"None": ["None"]},
            "Sweden": {"None": ["None"]},
            "Switzerland": {"None": ["None"]},
            "Turkey": {"None": ["None"]},
            "Ukraine": {"None": ["None"]},
            "Alps": {"None": ["None"]},
            "British Isles": {"None": ["None"]},
            "Germany, Austria, Switzerland": {"None": ["None"]},
        },
        "North America": {
            "None": {"None": ["None"]},
            "Canada": {
                "None": ["None"],
                "Alberta": ["None"],
                "British Columbia": ["None"],
                "Manitoba": ["None"],
                "New Brunswick": ["None"],
                "Newfoundland and Labrador": ["None"],
                "Northwest Territories": ["None"],
                "Nova Scotia": ["None"],
                "Nunavut": ["None"],
                "Ontario": ["None"],
                "Prince Edward Island": ["None"],
                "Quebec": ["None"],
                "Saskatchewan": ["None"],
                "Yukon": ["None"],
            },
            "None": {"None": ["None"]},
            "Greenland": {"None": ["None"]},
            "Mexico": {"None": ["None"]},
            "Alabama": {"None": ["None"]},
            "Alaska": {"None": ["None"]},
            "Arizona": {"None": ["None"]},
            "Arkansas": {"None": ["None"]},
            "California": {"None": ["None"]},
            "Colorado": {"None": ["None"]},
            "Connecticut": {"None": ["None"]},
            "Delaware": {"None": ["None"]},
            "District of Columbia": {"None": ["None"]},
            "Florida": {"None": ["None"]},
            "Georgia": {"None": ["None"]},
            "Hawaii": {"None": ["None"]},
            "Idaho": {"None": ["None"]},
            "Illinois": {"None": ["None"]},
            "Indiana": {"None": ["None"]},
            "Iowa": {"None": ["None"]},
            "Kansas": {"None": ["None"]},
            "Kentucky": {"None": ["None"]},
            "Louisiana": {"None": ["None"]},
            "Maine": {"None": ["None"]},
            "Maryland": {"None": ["None"]},
            "Massachusetts": {"None": ["None"]},
            "Michigan": {"None": ["None"]},
            "Minnesota": {"None": ["None"]},
            "Mississippi": {"None": ["None"]},
            "Missouri": {"None": ["None"]},
            "Montana": {"None": ["None"]},
            "Nebraska": {"None": ["None"]},
            "Nevada": {"None": ["None"]},
            "New Hampshire": {"None": ["None"]},
            "New Jersey": {"None": ["None"]},
            "New Mexico": {"None": ["None"]},
            "New York": {"None": ["None"]},
            "North Carolina": {"None": ["None"]},
            "North Dakota": {"None": ["None"]},
            "Ohio": {"None": ["None"]},
            "Oklahoma": {"None": ["None"]},
            "Oregon": {"None": ["None"]},
            "Pennsylvania": {"None": ["None"]},
            "Rhode Island": {"None": ["None"]},
            "South Carolina": {"None": ["None"]},
            "South Dakota": {"None": ["None"]},
            "Tennessee": {"None": ["None"]},
            "Texas": {"None": ["None"]},
            "US Midwest": {"None": ["None"]},
            "US Northeast": {"None": ["None"]},
            "US Pacific": {"None": ["None"]},
            "US South": {"None": ["None"]},
            "US West": {"None": ["None"]},
            "Utah": {"None": ["None"]},
            "Vermont": {"None": ["None"]},
            "Virginia": {"None": ["None"]},
            "Washington": {"None": ["None"]},
            "West Virginia": {"None": ["None"]},
            "Wisconsin": {"None": ["None"]},
            "Wyoming": {"None": ["None"]},
        },
        "Russia": {
            "None": {"None": ["None"]},
            "Central Federal District": {"None": ["None"]}, # EXCEPTION
            "Crimean Federal District": {"None": ["None"]}, # EXCEPTION
            "Far Eastern Federal District": {"None": ["None"]}, # EXCEPTION
            "North Caucasus Federal District": {"None": ["None"]}, # EXCEPTION
            "Northwestern Federal District": {"None": ["None"]}, # EXCEPTION
            "Siberian Federal District": {"None": ["None"]}, # EXCEPTION
            "South Federal District": {"None": ["None"]}, # EXCEPTION
            "Ural Federal District": {"None": ["None"]}, # EXCEPTION
            "Volga Federal District": {"None": ["None"]}, # EXCEPTION
            "Kaliningrad Federal District": {"None": ["None"]},
        },
        "South America": {
            "None": {"None": ["None"]},
            "Argentina": {"None": ["None"]},
            "Bolivia": {"None": ["None"]},
            "Brazil": {"None": ["None"]},
            "Chile": {"None": ["None"]},
            "Colombia": {"None": ["None"]},
            "Ecuador": {"None": ["None"]},
            "Paraguay": {"None": ["None"]},
            "Peru": {"None": ["None"]},
            "Suriname": {"None": ["None"]},
            "Uruguay": {"None": ["None"]},
        }
    }
    EXCEPTIONS = {
        "Congo (Republic/Brazzaville)": "congo-brazzaville",
        "Congo (Democratic Republic/Kinshasa)": "congo-demoratic-republic",
        "Malaysia, Singapore, and Brunei": "malaysia-signapore-brunei",
        "Myanmar (a.k.a. Burma)": "myanmar",
        "Haiti and Dominican Republic": "haiti-and-domrep",
        "Regierungsbezirk Freiburg": "freiburg-regbez",
        "Regierungsbezirk Karlsruhe": "karlsruhe-regbez",
        "Regierungsbezirk Stuttgart": "stuttgart-regbez",
        "Regierungsbezirk Tuebingen": "tuebingen-regbez",
        "Regierungsbezirk Arnsberg": "arnsberg-regbez",
        "Regierungsbezirk Detmold": "detmold-regbez",
        "Regierungsbezirk Duesseldorf": "duesseldorf-regbez",
        "Regierungsbezirk Koeln": "koeln-regbez",
        "Regierungsbezirk Muenster": "muenster-regbez",
        "Lower Silesian Voivodeship": "dolnoslaskie",
        "Kuyavian-Pomeranian Voivodeship": "kujawsko-pomorskie",
        "Łódź Voivodeship": "lodzkie",
        "Lublin Voivodeship": "lubelskie",
        "Lubusz Voivodeship": "lubuskie",
        "Lesser Poland Voivodeship": "malopolskie",
        "Mazovian Voivodeship": "mazowieckie",
        "Opole Voivodeship": "opolskie",
        "Subcarpathian Voivodeship": "podkarpackie",
        "Podlaskie Voivodeship": "podlaskie",
        "Pomeranian Voivodeship": "pomorskie",
        "Silesian Voivodeship": "slaskie",
        "Świętokrzyskie Voivodeship": "swietokrzyskie",
        "Warmian-Masurian Voivodeship": "warminsko-mazurskie",
        "Greater Poland Voivodeship": "wielkopolskie",
        "West Pomeranian Voivodeship": "zachodniopomorskie",
        "Central Federal District": "central-fed-district",
        "Crimean Federal District": "crimean-fed-district",
        "Far Eastern Federal District": "far-eastern-fed-district",
        "North Caucasus Federal District": "north-caucasus-fed-district",
        "Northwestern Federal District": "northwestern-fed-district",
        "Siberian Federal District": "siberian-fed-district",
        "South Federal District": "south-fed-district",
        "Ural Federal District": "ural-fed-district",
        "Volga Federal District": "volga-fed-district",
    }


    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MakeOSMRoutableNetwork_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Make OSM Routable Network')
        self.toolbar = self.iface.addToolBar(u'MakeOSMRoutableNetwork')
        self.toolbar.setObjectName(u'MakeOSMRoutableNetwork')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MakeOSMRoutableNetwork', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = MakeOSMRoutableNetworkDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MakeOSMRoutableNetwork/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Make OSM Routable Network'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # Set up initial GUI state
        self.set_initial_state()

        # Toggle bounding box
        self._bounding_box_toggle = False
        self.dlg.bounding_box_checkBox.setChecked(False)
        self.dlg.bounding_box_checkBox.clicked.connect(self.toggle_bounding_box)

        # Toggle schema
        self._schema_toggle = False
        self.dlg.schema_checkBox.setChecked(False)
        self.dlg.schema_checkBox.clicked.connect(self.toggle_schema)

        # Toggle prefix
        self._prefix_toggle = False
        self.dlg.prefix_checkBox.setChecked(False)
        self.dlg.prefix_checkBox.clicked.connect(self.toggle_prefix)

        # Toggle suffix
        self._suffix_toggle = False
        self.dlg.suffix_checkBox.setChecked(False)
        self.dlg.suffix_checkBox.clicked.connect(self.toggle_suffix)

        # Check that all dependencies are installed & up to date.
        self.check_dependencies()

        # Make the working folder if it doesn't exist.
        os.chdir(self.plugin_dir)
        if not os.path.isdir("data"):
            os.mkdir("data")

        # Toggle between local file and Geofabrik region
        self._file_source_toggle = "file"
        self.dlg.local_file_radioButton.clicked.connect(self.select_local_osm)
        self.dlg.geofabrik_region_radioButton.clicked.connect(self.select_geofabrik_region)

        # Set up file chooser
        self.dlg.local_file_pushButton.clicked.connect(self.open_file_chooser)

        # Make "Current Extent" button generate the current extent in their respective lineEdits
        self.dlg.extent_pushButton.clicked.connect(self.add_current_extent)

        # Toggle between existing db and new db
        self.dlg.existing_db_radioButton.clicked.connect(self.select_existing_db)
        self.dlg.new_db_radioButton.clicked.connect(self.select_new_db)

        # Change region1 based on region
        self.dlg.region0_comboBox.currentIndexChanged[str].connect(self.update_region1)

        # Change region2 based on region1
        self.dlg.region1_comboBox.currentIndexChanged[str].connect(self.update_region2)

        # Change region3 based on region2
        self.dlg.region2_comboBox.currentIndexChanged[str].connect(self.update_region3)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Make OSM Routable Network'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed

        if result:

            # Get credentials if a pre-existing connection from QGIS was selected
            if self.dlg.existing_db_radioButton.isChecked():
                db_name = self.dlg.db_listWidget.currentItem().text()
                db_credentials = self.get_db_credentials(db_name)

            # Define credentials from dialog and create database if new connection was selected
            elif self.dlg.new_db_radioButton.isChecked():
                db_credentials = {
                    "name": self.dlg.new_db_name_lineEdit.text(),
                    "service": self.dlg.new_db_service_lineEdit.text(),
                    "host": self.dlg.new_db_host_lineEdit.text(),
                    "port": self.dlg.new_db_port_lineEdit.text(),
                    "dbname": self.dlg.new_db_database_lineEdit.text(),
                    "user": self.dlg.new_db_username_lineEdit.text(),
                    "password": self.dlg.new_db_password_lineEdit.text()
                }
                self.make_database(db_credentials["dbname"], db_credentials["host"], db_credentials["port"],
                                   db_credentials["user"], db_credentials["password"])

                # Add the connection to QGIS
                settings = QSettings()
                settings.setValue("PostgreSQL/connections/{0}/allowGeometrylessTables".format(db_credentials["dbname"]), "false")
                settings.setValue("PostgreSQL/connections/{0}/authcfg".format(db_credentials["dbname"]), "")
                settings.setValue("PostgreSQL/connections/{0}/database".format(db_credentials["dbname"]), "upwork")
                settings.setValue("PostgreSQL/connections/{0}/dontResolveType".format(db_credentials["dbname"]), "false")
                settings.setValue("PostgreSQL/connections/{0}/estimatedMetadata".format(db_credentials["dbname"]), "false")
                settings.setValue("PostgreSQL/connections/{0}/geometryColumnsOnly".format(db_credentials["dbname"]), "false")
                settings.setValue("PostgreSQL/connections/{0}/host".format(db_credentials["dbname"]), db_credentials["host"])
                settings.setValue("PostgreSQL/connections/{0}/password".format(db_credentials["dbname"]), db_credentials["password"])
                settings.setValue("PostgreSQL/connections/{0}/port".format(db_credentials["dbname"]), db_credentials["port"])
                settings.setValue("PostgreSQL/connections/{0}/publicOnly".format(db_credentials["dbname"]), "false")
                settings.setValue("PostgreSQL/connections/{0}/savePassword".format(db_credentials["dbname"]), "false")
                settings.setValue("PostgreSQL/connections/{0}/saveUsername".format(db_credentials["dbname"]), "false")
                settings.setValue("PostgreSQL/connections/{0}/service".format(db_credentials["dbname"]), db_credentials["service"])
                settings.setValue("PostgreSQL/connections/{0}/sslmode".format(db_credentials["dbname"]), "1")
                settings.setValue("PostgreSQL/connections/{0}/username".format(db_credentials["dbname"]), db_credentials["user"])
                QCoreApplication.processEvents() # refresh browser panel

            # Check for postgis & pgrouting extensions, add them in they are not there
            self.make_extensions(db_credentials["dbname"], db_credentials["host"], db_credentials["port"],
                                 db_credentials["user"], db_credentials["password"])

            # Establish file names & download if necessary
            if self.dlg.local_file_radioButton.isChecked():
                # Just use whatever text is in the local file lineEdit
                routing_data_file = self.dlg.local_file_lineEdit.text()
            else:
                # Download & extract the selected region
                region0 = self.dlg.region0_comboBox.currentText()
                region1 = self.dlg.region1_comboBox.currentText()
                region2 = self.dlg.region2_comboBox.currentText()
                region3 = self.dlg.region3_comboBox.currentText()
                self.download_routing_data(region0, region1, region2, region3)
                routing_data_file = "data/routing_data.osm"
    
            # Apply the bounding box if specified
            if self.dlg.bounding_box_checkBox.isChecked():
    
                top = self.dlg.bounding_box_top_lineEdit.text()
                left = self.dlg.bounding_box_left_lineEdit.text()
                right = self.dlg.bounding_box_right_lineEdit.text()
                bottom = self.dlg.bounding_box_bottom_lineEdit.text()

                osmosis_parameters = [
                    "osmosis/bin/osmosis",
                    "--read-xml", routing_data_file,
                    "--bounding-box",
                    "top={0}".format(top), "left={0}".format(left), "right={0}".format(right), "bottom={0}".format(bottom),
                    "--write-xml", "data/routing_data_bb.osm",
                ]
    
                routing_data_file = "data/routing_data_bb.osm"
    
                osmosis_process = subprocess.Popen(osmosis_parameters, stdout=subprocess.PIPE)
                for line in iter(osmosis_process.stdout.readline, ''):
                    sys.stdout.write(line)
    
            # Set map config
            if self.dlg.mapconfig_std_radioButton.isChecked():
                map_config = "map_configs/mapconfig.xml"
            elif self.dlg.mapconfig_cars_radioButton.isChecked():
                map_config = "map_configs/mapconfig_for_cars.xml"
            elif self.dlg.mapconfig_bicycles_radioButton.isChecked():
                map_config = "map_configs/mapconfig_for_bicycles.xml"

            # Set up other osm2pgrouting parameters
            if self.dlg.schema_checkBox.isChecked():
                schema = self.dlg.schema_lineEdit.text()
            else:
                schema = "public"
    
            osm2pgrouting_parameters = [
                "osm2pgrouting",
                "--file", routing_data_file,
                "--conf", map_config,
                "--schema", schema,
                "--dbname", db_credentials["dbname"],
                "--host", db_credentials["host"],
                "--username", db_credentials["user"],
                "--password", db_credentials["password"],
            ]
            if self.dlg.overwrite_checkBox.isChecked():
                osm2pgrouting_parameters.append("--clean")
            if self.dlg.nodes_checkBox.isChecked():
                osm2pgrouting_parameters.append("--addnodes")
            if self.dlg.prefix_checkBox.isChecked():
                osm2pgrouting_parameters.extend(["--prefix", self.dlg.prefix_lineEdit.text().lower()])
            if self.dlg.prefix_checkBox.isChecked():
                osm2pgrouting_parameters.extend(["--suffix", self.dlg.suffix_lineEdit.text().lower()])

                for p in osm2pgrouting_parameters:
                    print(p, type(p))
    
            osm2pgrouting_process = subprocess.Popen(osm2pgrouting_parameters, stdout=subprocess.PIPE)
            for line in iter(osm2pgrouting_process.stdout.readline, ''):
                sys.stdout.write(line)

            try:
                remove("data/routing_data.osm.bz2")
            except OSError:
                pass
            try:
                remove("data/routing_data.osm")
            except OSError:
                pass
            try:
                remove("data/routing_data_bb.osm")
            except OSError:
                pass

        print("FINISHED")


    def check_dependencies(self):

        # Check that osm2pgrouting is installed
        sp = subprocess.Popen(["which", "osm2pgrouting"], stdout=subprocess.PIPE)
        response = [line for line in iter(sp.stdout.readline, '')]
        if not response:
            choice = QtGui.QMessageBox.critical(self.dlg, "No osm2pgrouting!",
                                                "This plugin requires osm2pgrouting to be installed. Please install it to proceed. Would you like to go to the osm2pgrouting repository? (Will open in separate browser window.",
                                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if choice == QtGui.QMessageBox.Yes:
                webbrowser.open_new("https://github.com/pgRouting/osm2pgrouting")
            self.dlg.done()

        # Check that psycopg is at least version 2.7
        digit1 = psycopg2.__version__.split(".")[0]
        digit2 = psycopg2.__version__.split(".")[1]
        if not digit1 >= 2 and digit2 >= 7:
            error = QtGui.QMessageBox.critical(self.dlg, "psycopg2 out of date!!",
                                               "This plugin requires that the psycopg2 python package be at least version 2.7.  Your version appears to be version {0}.{1}.  Please update psycopg2 and try again.".format(digit1, digit2),
                                               QtGui.QMessageBox.Ok)
            if error == QtGui.QMessageBox.Ok:
                self.dlg.done()

        return None


    def set_initial_state(self):

        # Database connections
        qs = QSettings()

        k_list = [k for k in sorted(qs.allKeys()) if k[:10] == "PostgreSQL" and k[-8:] == "database"]
        for k in k_list:
            item = QListWidgetItem(k.split("/")[2])
            self.dlg.db_listWidget.addItem(item)

        # Regions & Subregions
        regions = sorted([region for region in self.REGIONS.iterkeys()])
        self.dlg.region0_comboBox.addItems(regions)
        self.dlg.region0_comboBox.setDisabled(True)

        subregions = sorted([subregion for subregion in self.REGIONS["Africa"].iterkeys()])
        self.dlg.region1_comboBox.addItems(subregions)
        self.dlg.region1_comboBox.setCurrentIndex(self.dlg.region1_comboBox.findText("None"))
        self.dlg.region1_comboBox.setDisabled(True)

        subregions = sorted(subregion for subregion in self.REGIONS["Africa"]["None"].iterkeys())
        self.dlg.region2_comboBox.addItems(subregions)
        self.dlg.region2_comboBox.setDisabled(True)

        subregions = sorted(self.REGIONS["Africa"]["None"]["None"])
        self.dlg.region3_comboBox.addItems(subregions)
        self.dlg.region3_comboBox.setDisabled(True)

        # Radio buttons
        self.dlg.local_file_radioButton.setChecked(True)
        self.dlg.existing_db_radioButton.setChecked(True)
        self.dlg.mapconfig_std_radioButton.setChecked(True)

        # Bounding Box
        self.dlg.bounding_box_checkBox.setChecked(False)
        self.dlg.extent_pushButton.setDisabled(True)
        self.dlg.bounding_box_top_lineEdit.setDisabled(True)
        self.dlg.bounding_box_left_lineEdit.setDisabled(True)
        self.dlg.bounding_box_right_lineEdit.setDisabled(True)
        self.dlg.bounding_box_bottom_lineEdit.setDisabled(True)

        # Schema
        self.dlg.bounding_box_checkBox.setChecked(False)
        self.dlg.schema_lineEdit.setDisabled(True)

        # Prefix
        self.dlg.prefix_checkBox.setChecked(False)
        self.dlg.prefix_lineEdit.setDisabled(True)

        # Suffix
        self.dlg.suffix_checkBox.setChecked(False)
        self.dlg.suffix_lineEdit.setDisabled(True)

        # Database
        self.dlg.overwrite_checkBox.setDisabled(False)
        self.dlg.db_listWidget.setDisabled(False)
        self.dlg.new_db_name_lineEdit.setDisabled(True)
        self.dlg.new_db_service_lineEdit.setDisabled(True)
        self.dlg.new_db_host_lineEdit.setDisabled(True)
        self.dlg.new_db_port_lineEdit.setDisabled(True)
        self.dlg.new_db_database_lineEdit.setDisabled(True)
        self.dlg.new_db_username_lineEdit.setDisabled(True)
        self.dlg.new_db_password_lineEdit.setDisabled(True)

        return None


    def select_local_osm(self):

        self.dlg.local_file_pushButton.setDisabled(False)
        self.dlg.local_file_lineEdit.setDisabled(False)
        self.dlg.region0_comboBox.setDisabled(True)
        self.dlg.region1_comboBox.setDisabled(True)
        self.dlg.region2_comboBox.setDisabled(True)
        self.dlg.region3_comboBox.setDisabled(True)

        return None


    def select_geofabrik_region(self):

        self.dlg.local_file_pushButton.setDisabled(True)
        self.dlg.local_file_lineEdit.setDisabled(True)
        self.dlg.region0_comboBox.setDisabled(False)
        self.dlg.region1_comboBox.setDisabled(False)
        self.dlg.region2_comboBox.setDisabled(False)
        self.dlg.region3_comboBox.setDisabled(False)

        return None


    def open_file_chooser(self):

        filename = QFileDialog.getOpenFileName(self.dlg, "Select .osm file", "", "*.osm")
        if filename:
            self.dlg.local_file_lineEdit.setText(filename)

        return None


    def toggle_bounding_box(self):

        if self._bounding_box_toggle:
            self.dlg.extent_pushButton.setDisabled(True)
            self.dlg.bounding_box_top_lineEdit.setDisabled(True)
            self.dlg.bounding_box_left_lineEdit.setDisabled(True)
            self.dlg.bounding_box_right_lineEdit.setDisabled(True)
            self.dlg.bounding_box_bottom_lineEdit.setDisabled(True)
        else:
            self.dlg.extent_pushButton.setDisabled(False)
            self.dlg.bounding_box_top_lineEdit.setDisabled(False)
            self.dlg.bounding_box_left_lineEdit.setDisabled(False)
            self.dlg.bounding_box_right_lineEdit.setDisabled(False)
            self.dlg.bounding_box_bottom_lineEdit.setDisabled(False)

        self._bounding_box_toggle = not self._bounding_box_toggle

        return None


    def toggle_schema(self):

        if self._schema_toggle:
            self.dlg.schema_lineEdit.setDisabled(True)
        else:
            self.dlg.schema_lineEdit.setDisabled(False)

        self._schema_toggle = not self._schema_toggle

        return None


    def toggle_prefix(self):

        if self._prefix_toggle:
            self.dlg.prefix_lineEdit.setDisabled(True)
        else:
            self.dlg.prefix_lineEdit.setDisabled(False)

        self._prefix_toggle = not self._prefix_toggle

        return None


    def toggle_suffix(self):

        if self._suffix_toggle:
            self.dlg.suffix_lineEdit.setDisabled(True)
        else:
            self.dlg.suffix_lineEdit.setDisabled(False)

        self._suffix_toggle = not self._suffix_toggle

        return None


    def select_existing_db(self):

        self.dlg.overwrite_checkBox.setDisabled(False)
        self.dlg.db_listWidget.setDisabled(False)
        self.dlg.new_db_name_lineEdit.setDisabled(True)
        self.dlg.new_db_service_lineEdit.setDisabled(True)
        self.dlg.new_db_host_lineEdit.setDisabled(True)
        self.dlg.new_db_port_lineEdit.setDisabled(True)
        self.dlg.new_db_database_lineEdit.setDisabled(True)
        self.dlg.new_db_username_lineEdit.setDisabled(True)
        self.dlg.new_db_password_lineEdit.setDisabled(True)

        return None


    def select_new_db(self):

        self.dlg.overwrite_checkBox.setDisabled(True)
        self.dlg.db_listWidget.setDisabled(True)
        self.dlg.new_db_name_lineEdit.setDisabled(False)
        self.dlg.new_db_service_lineEdit.setDisabled(False)
        self.dlg.new_db_host_lineEdit.setDisabled(False)
        self.dlg.new_db_port_lineEdit.setDisabled(False)
        self.dlg.new_db_database_lineEdit.setDisabled(False)
        self.dlg.new_db_username_lineEdit.setDisabled(False)
        self.dlg.new_db_password_lineEdit.setDisabled(False)

        return None


    @QtCore.pyqtSlot(str)
    def update_region1(self, index):

        self.dlg.region1_comboBox.clear()

        subregions = sorted([subregion for subregion in self.REGIONS[index].iterkeys()])
        subregions.remove("None")
        subregions.insert(0, "None")
        self.dlg.region1_comboBox.addItems(subregions)

        return None


    @QtCore.pyqtSlot(str)
    def update_region2(self, index):

        self.dlg.region2_comboBox.clear()

        current_region = self.dlg.region0_comboBox.currentText()

        # some weird bug occurs here because it tries to select an empty index momentarily, but it doesn't seem to
        # actually break anything, so this try/except block just supresses the error.
        try:
            subregions = sorted([subregion for subregion in self.REGIONS[current_region][index].iterkeys()])
            subregions.remove("None")
            subregions.insert(0, "None")
            self.dlg.region2_comboBox.addItems(subregions)
        except:
            pass

        return None


    @QtCore.pyqtSlot(str)
    def update_region3(self, index):

        self.dlg.region3_comboBox.clear()

        current_region = self.dlg.region0_comboBox.currentText()
        current_region1 = self.dlg.region1_comboBox.currentText()

        # some weird bug occurs here because it tries to select an empty index momentarily, but it doesn't seem to
        # actually break anything, so this try/except block just supresses the error.
        try:
            subregions = self.REGIONS[current_region][current_region1][index]
            subregions.remove("None")
            subregions.insert(0, "None")
            self.dlg.region3_comboBox.addItems(subregions)
        except:
            pass

        return None


    def format_region_name(self, name):

        if name in [k for k in self.EXCEPTIONS.iterkeys()]:
            name = self.EXCEPTIONS[name]
        else:
            name = name.replace(" ", "-").replace("'", "-").lower()

        return name


    def add_current_extent(self):

        # Get current CRS and set up a CRS transformer for the current CRS and WGS84 (EPSG: 4326)
        canvas = self.iface.mapCanvas()
        current_crs = canvas.mapRenderer().destinationCrs().authid()
        source_crs = QgsCoordinateReferenceSystem(current_crs)
        target_crs = QgsCoordinateReferenceSystem(4326)
        transformer = QgsCoordinateTransform(source_crs, target_crs)

        # Get current extent and transform to WGS84
        extent = self.iface.mapCanvas().extent()
        bottom_left_point = QgsPoint(extent.xMinimum(), extent.yMinimum())
        top_right_point = QgsPoint(extent.xMaximum(), extent.yMaximum())
        bottom_left_point_transformed = transformer.transform(bottom_left_point)
        top_right_point_transformed = transformer.transform(top_right_point)

        # Extract extent boundaries
        top = top_right_point_transformed.y()
        left = bottom_left_point_transformed.x()
        right = top_right_point_transformed.x()
        bottom = bottom_left_point_transformed.y()

        # Populate extent lineEdits
        self.dlg.bounding_box_top_lineEdit.setText(str(top))
        self.dlg.bounding_box_left_lineEdit.setText(str(left))
        self.dlg.bounding_box_right_lineEdit.setText(str(right))
        self.dlg.bounding_box_bottom_lineEdit.setText(str(bottom))

        return None


    def make_download_url(self, region, region1, region2, region3):

        region = self.format_region_name(region)
        region1 = self.format_region_name(region1)
        region2 = self.format_region_name(region2)
        region3 = self.format_region_name(region3)

        download_url = "http://download.geofabrik.de/{0}".format(region)
        if region1 != "none":
            download_url += "/{0}".format(region1)
            if region2 != "none":
                download_url += "/{0}".format(region2)
                if region3 != "none":
                    download_url += "/{0}".format(region3)
        download_url += "-latest.osm.bz2"
        print(download_url)

        return download_url


    def download_routing_data(self, region, region1, region2, region3):

        download_url = self.make_download_url(region, region1, region2, region3)
        download_bz2 = "data/routing_data.osm.bz2"

        urllib.urlretrieve(download_url, download_bz2)
        bz2_file = bz2.BZ2File(download_bz2)
        data = bz2_file.read()
        open("data/routing_data.osm", "wb").write(data)

        return None


    def get_db_credentials(self, db_name):

        db_credentials = {
            "dbname": db_name
        }
        qs = QSettings()
        k_list = [k for k in sorted(qs.allKeys()) if k[:10] == "PostgreSQL" and k.split("/")[2] == db_name]
        for k in k_list:
            if k.split("/")[-1] == "host":
                db_credentials["host"] = qs.value(k)
            elif k.split("/")[-1] == "port":
                db_credentials["port"] = qs.value(k)
            elif k.split("/")[-1] == "username":
                db_credentials["user"] = qs.value(k)
            elif k.split("/")[-1] == "password":
                db_credentials["password"] = qs.value(k)

        return db_credentials


    def make_database(self, dbname, host, port, user, password):

        conn_string = "dbname=postgres host={0} port={1} user={2} password={3}".format(host, port, user, password)
        conn = dbconnect(conn_string)
        conn.autocommit = True
        cur = conn.cursor()
        query = sql.SQL("""

                    CREATE DATABASE {};

        """).format(sql.Identifier(dbname))
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()

        return None


    def make_extensions(self, dbname, host, port, user, password):

        conn_string = "dbname={0} host={1} port={2} user={3} password={4}".format(dbname, host, port, user, password)
        conn = dbconnect(conn_string)
        cur = conn.cursor()
        query = sql.SQL("""
        
            CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA {};
            CREATE EXTENSION IF NOT EXISTS pgrouting WITH SCHEMA {};
        
        """).format(sql.Identifier(dbname))
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()

        return None


    def make_database_connection(self, name, dbname, host, port, user, password):

        db = QSqlDatabase.addDatabase(name)
        db.setHostName(host)
        db.setDatabaseName(dbname)
        db.setPort(int(port))
        db.setUserName(user)
        db.setPassword(password)

        return None