# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CZMLBillboardMaker
                                 A QGIS plugin
 Creates Billboards from a point vector layer.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-12-25
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Murat Kendir
        email                : muratkendir@gmail.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import QgsProject, Qgis
import datetime
import webbrowser
import json
import math
from pytz import timezone
import pytz
#Local/ sources
from .Metadata import Metadata
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .CZMLBillboardMaker_dialog import CZMLBillboardMakerDialog
import os.path


class CZMLBillboardMaker:
    """QGIS Plugin Implementation."""

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
            'CZMLBillboardMaker_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&CZML Billboard Maker')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None



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
        return QCoreApplication.translate('CZMLBillboardMaker', message)


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

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/CZMLBillboardMaker/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Points to CZML Billboards'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&CZML Billboard Maker'),
                action)
            self.iface.removeToolBarIcon(action)

    #Get only vector layers with point geometry.
    def getPointVectorLayers(self):
        currentLayers = QgsProject.instance().mapLayers()
        pointLayers = []
        pointLayerNames = []
        for layer in currentLayers:
            if currentLayers.get(layer).type().value == 0 and currentLayers.get(layer).geometryType() == 0:
                pointLayers.append(layer)
                pointLayerNames.append(currentLayers.get(layer).name())
        return pointLayerNames

    #Read layer attributes and populate attribute comboxes with them.
    def populateAttributes(self):
        currentLayers = QgsProject.instance().mapLayers()
        if self.dlg.comboPointLayerNames.currentIndex() != 0:
            for layer in currentLayers:
                if currentLayers.get(layer).name() == self.dlg.comboPointLayerNames.currentText():
                    selectedLayer = currentLayers.get(layer)
                    #print(selectedLayer.attributeAliases())
                    self.dlg.comboBoxId.clear()
                    self.dlg.comboBoxId.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxName.clear()
                    self.dlg.comboBoxName.addItem('Not Selected')
                    self.dlg.comboBoxName.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxDescription.clear()
                    self.dlg.comboBoxDescription.addItem('Not Selected')
                    self.dlg.comboBoxDescription.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxText.clear()
                    self.dlg.comboBoxText.addItem('Not Selected')
                    self.dlg.comboBoxText.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxImage.clear()
                    self.dlg.comboBoxImage.addItem('Not Selected')
                    self.dlg.comboBoxImage.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxModel.clear()
                    self.dlg.comboBoxModel.addItem('Not Selected')
                    self.dlg.comboBoxModel.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxAzimuth.clear()
                    self.dlg.comboBoxAzimuth.addItem('Not Selected')
                    self.dlg.comboBoxAzimuth.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxNode.clear()
                    self.dlg.comboBoxNode.addItem('Not Selected')
                    self.dlg.comboBoxNode.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxHeight.clear()
                    self.dlg.comboBoxHeight.addItem('Not Selected')
                    self.dlg.comboBoxHeight.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxTimeBeginning.clear()
                    self.dlg.comboBoxTimeBeginning.addItem('Not Selected')
                    self.dlg.comboBoxTimeBeginning.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxTimeEnd.clear()
                    self.dlg.comboBoxTimeEnd.addItem('Not Selected')
                    self.dlg.comboBoxTimeEnd.addItems(selectedLayer.attributeAliases())
                    self.dlg.comboBoxTimeZone.clear()
                    self.dlg.comboBoxTimeZone.addItems(pytz.all_timezones)
                    #print(pytz.all_timezones)
                    self.dlg.comboBoxTimeZone.setCurrentText('UTC')
                    
        else:
            print('Please select a valid layer.')

    #Clear All function
    def clearAll(self):
        self.dlg.comboBoxTimeZone.clear()
        self.dlg.comboBoxTimeEnd.clear()
        self.dlg.comboBoxTimeBeginning.clear()
        self.dlg.comboBoxHeight.clear()
        self.dlg.comboBoxImage.clear()
        self.dlg.comboBoxText.clear()
        self.dlg.comboBoxModel.clear()
        self.dlg.comboBoxAzimuth.clear()
        self.dlg.comboBoxNode.clear()
        self.dlg.comboBoxDescription.clear()
        self.dlg.comboBoxName.clear()
        self.dlg.comboBoxId.clear()
        self.dlg.lineEditFileName.clear()
        self.dlg.comboBoxModel.clear()
        self.dlg.comboBoxAzimuth.clear()
        self.dlg.comboBoxNode.clear()

    #Selecting filename for export czml file
    def browseForFileName(self):
        fileName = QFileDialog.getSaveFileName(self.dlg,"Select output file ","", '*.czml')
        fileURL = fileName[0]
        fileExtension = fileURL[-5:] 
        if fileExtension == '.czml' or fileExtension == '.CZML':
            checkedFileURL = fileURL
        else:
            checkedFileURL = fileURL + '.czml'
        self.dlg.lineEditFileName.setText(checkedFileURL)
    
    def browseWebLink(self):
        webbrowser.open('https://github.com/AnalyticalGraphicsInc/czml-writer/wiki/CZML-Guide')

    def checkBillboardType(self):
        if self.dlg.comboBoxBillboardType.currentText() == 'Only Labels':
            #print("Only Labels selected.")
            self.dlg.comboBoxText.setEnabled(1)
            self.dlg.comboBoxImage.setDisabled(1)
            self.dlg.comboBoxModel.setDisabled(1)
            self.dlg.comboBoxAzimuth.setDisabled(1)
            self.dlg.comboBoxNode.setDisabled(1)
            #Set Labels
            self.dlg.labelText.setEnabled(1)
            self.dlg.labelImage.setDisabled(1)
            self.dlg.labelModel.setDisabled(1)
            self.dlg.labelAzimuth.setDisabled(1)
            self.dlg.labelNode.setDisabled(1)
        elif self.dlg.comboBoxBillboardType.currentText() == 'Only Images':
            #print("Only Images selected.")
            self.dlg.comboBoxText.setDisabled(1)
            self.dlg.comboBoxImage.setEnabled(1)
            self.dlg.comboBoxModel.setDisabled(1)
            self.dlg.comboBoxAzimuth.setDisabled(1)
            self.dlg.comboBoxNode.setDisabled(1)
            #Set Labels
            self.dlg.labelText.setDisabled(1)
            self.dlg.labelImage.setEnabled(1)
            self.dlg.labelModel.setDisabled(1)
            self.dlg.labelAzimuth.setDisabled(1)
            self.dlg.labelNode.setDisabled(1)
        elif self.dlg.comboBoxBillboardType.currentText() == 'Only 3D Models':
            self.dlg.comboBoxText.setDisabled(1)
            self.dlg.comboBoxImage.setDisabled(1)
            self.dlg.comboBoxModel.setEnabled(1)
            self.dlg.comboBoxAzimuth.setEnabled(1)
            self.dlg.comboBoxNode.setEnabled(1)
            #Set Labels
            self.dlg.labelText.setDisabled(1)
            self.dlg.labelImage.setDisabled(1)
            self.dlg.labelModel.setEnabled(1)
            self.dlg.labelAzimuth.setEnabled(1)
            self.dlg.labelNode.setEnabled(1)
        else:
            #print("Labels and Images selected.")
            self.dlg.comboBoxText.setEnabled(1)
            self.dlg.comboBoxImage.setEnabled(1)
            self.dlg.comboBoxModel.setDisabled(1)
            self.dlg.comboBoxAzimuth.setDisabled(1)
            self.dlg.comboBoxNode.setDisabled(1)
            #Set Labels
            self.dlg.labelText.setEnabled(1)
            self.dlg.labelImage.setEnabled(1)
            self.dlg.labelModel.setDisabled(1)
            self.dlg.labelAzimuth.setDisabled(1)
            self.dlg.labelNode.setDisabled(1)

    def checkClockButton(self):
        if self.dlg.radioButtonClockConf.isChecked():
            self.dlg.dateTimeEditClockCurrent.setEnabled(1)
            self.dlg.dateTimeEditClockBeginning.setEnabled(1)
            self.dlg.dateTimeEditClockEnd.setEnabled(1)
            self.dlg.lineEditClockMultiplier.setEnabled(1)
            self.dlg.comboBoxClockRange.setEnabled(1)
            self.dlg.comboBoxClockStep.setEnabled(1)
        else:
            self.dlg.dateTimeEditClockCurrent.setDisabled(1)
            self.dlg.dateTimeEditClockBeginning.setDisabled(1)
            self.dlg.dateTimeEditClockEnd.setDisabled(1)
            self.dlg.lineEditClockMultiplier.setDisabled(1)
            self.dlg.comboBoxClockRange.setDisabled(1)
            self.dlg.comboBoxClockStep.setDisabled(1)

    def checkSetupTimeButton(self):
        if self.dlg.radioButtonSetupTime.isChecked():
            self.dlg.comboBoxTimeBeginning.setEnabled(1)
            self.dlg.comboBoxTimeEnd.setEnabled(1)
            self.dlg.comboBoxTimeZone.setEnabled(1)
            #Set Labels
            self.dlg.labelTimeBeginning.setEnabled(1)
            self.dlg.labelTimeEnd.setEnabled(1)
            self.dlg.labelTimeZone.setEnabled(1)
        else:
            self.dlg.comboBoxTimeBeginning.setDisabled(1)
            self.dlg.comboBoxTimeEnd.setDisabled(1)
            self.dlg.comboBoxTimeZone.setDisabled(1)
            #Set Labels
            self.dlg.labelTimeBeginning.setDisabled(1)
            self.dlg.labelTimeEnd.setDisabled(1)
            self.dlg.labelTimeZone.setDisabled(1)

    def run(self):
        """Run method that performs all the real work"""
        
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = CZMLBillboardMakerDialog()
            self.dlg.lineEditFileName.clear()
            self.dlg.pushButtonBrowse.clicked.connect(self.browseForFileName)

            #Clear first point based layers combobox, then populate with point layers.
            self.dlg.comboPointLayerNames.clear()
            #Set a placeholder text for layer combobox
            self.dlg.comboPointLayerNames.addItem('Select a point layer')
            self.dlg.comboPointLayerNames.addItems(self.getPointVectorLayers())
            #self.dlg.comboPointLayerNames.setCurrentText('Select a point layer')
        

        #Only Label / Only Image / Label + Image
        self.dlg.comboBoxBillboardType.currentIndexChanged.connect(self.checkBillboardType) 

        #If Configure Cesium Clock radio button element selected, then activate clock parameters and get them.
        self.dlg.radioButtonClockConf.clicked.connect(self.checkClockButton)

        #If checked time attributes will be activated
        self.dlg.radioButtonSetupTime.clicked.connect(self.checkSetupTimeButton)

        #Populate Attributes Button
        self.dlg.pushButtonPopAttributes.clicked.connect(self.populateAttributes)

        #Clear All Button
        self.dlg.pushButtonClearAll.clicked.connect(self.clearAll)
        
        
        

        #Visit CZML Guide page if command link clicked.
        self.dlg.commandLinkButton.clicked.connect(self.browseWebLink)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            fileURL = self.dlg.lineEditFileName.text()
            
            #Take Selected layer from current QGIS canvas.
            currentLayers = QgsProject.instance().mapLayers()
            if self.dlg.comboPointLayerNames.currentIndex() != 0:
                for layer in currentLayers:
                    if currentLayers.get(layer).name() == self.dlg.comboPointLayerNames.currentText():
                        selectedLayer = currentLayers.get(layer)
            layerName = selectedLayer.name()
            #layerCrs = selectedLayer.sourceCrs()
            #print(layerCrs)

            #Take selected fields from attributes combobox.
            selectedHeightField = self.dlg.comboBoxHeight.currentText()
            selectedIdField = self.dlg.comboBoxId.currentText()
            selectedNameField = self.dlg.comboBoxName.currentText()
            selectedDescriptionField = self.dlg.comboBoxDescription.currentText()
            selectedTextField = self.dlg.comboBoxText.currentText()
            selectedImageField = self.dlg.comboBoxImage.currentText()
            selectedModelField = self.dlg.comboBoxModel.currentText()
            selectedAzimuthField = self.dlg.comboBoxAzimuth.currentText()
            selectedNodeField = self.dlg.comboBoxNode.currentText()
            if self.dlg.radioButtonSetupTime.isChecked():
                selectedTimeBeginningField = self.dlg.comboBoxTimeBeginning.currentText()
                selectedTimeEndField = self.dlg.comboBoxTimeEnd.currentText()
                selectedTimeZone = self.dlg.comboBoxTimeZone.currentText()
                timeZone = timezone(self.dlg.comboBoxTimeZone.currentText())
            #No need to format, used isoformat
            #dateTimeFormat = fmt = '%Y-%m-%dT%H:%M:%S%z'

            #Take CZML Clock time interval options
            if self.dlg.radioButtonClockConf.isChecked():
                #Get Current Date Time
                selectedClockCurrent = self.dlg.dateTimeEditClockCurrent.dateTime()
                selectedClockCurrentLocal = timeZone.localize(selectedClockCurrent.toPyDateTime()).isoformat()
                #Get Beginning Date Time
                selectedClockBeginning = self.dlg.dateTimeEditClockBeginning.dateTime()
                selectedClockBeginningLocal = timeZone.localize(selectedClockBeginning.toPyDateTime()).isoformat()
                #Get End Date Time
                selectedClockEnd = self.dlg.dateTimeEditClockEnd.dateTime()
                selectedClockEndLocal = timeZone.localize(selectedClockEnd.toPyDateTime()).isoformat()
                #GEt other parameters
                selectedClockMultiplier = self.dlg.lineEditClockMultiplier.text()
                selectedClockRange = self.dlg.comboBoxClockRange.currentText()
                selectedClockStep = self.dlg.comboBoxClockStep.currentText()


            exportedFile = open(fileURL, mode='w', encoding='utf-8')

            #BeginningLines old method startes here
            """
            #Writes beginning of CZML document and layer name as document name.
            beginningLines = '[\n    {\n        "version": "1.0" \n        ,"id": "document" \n        ,"name": "'+ layerName +'"'

            #Add CZML Clock parameters if enabled.
            if self.dlg.radioButtonClockConf.isChecked():
                beginningLines = beginningLines + '\n        ,"clock": {\n            "interval": "'
                beginningLines = beginningLines + selectedClockBeginningLocal + '/' + selectedClockEndLocal + '",\n'
                beginningLines = beginningLines + '            "currentTime": "' + selectedClockCurrentLocal + '",\n'
                beginningLines = beginningLines + '            "multiplier": ' + selectedClockMultiplier + ',\n'
                beginningLines = beginningLines + '            "range": "' + selectedClockRange + '",\n'
                beginningLines = beginningLines + '            "step": "' + selectedClockStep + '"\n'
                beginningLines = beginningLines + '        }\n'
                beginningLines = beginningLines + '    }\n'
            else:           
                #Last row of beginning header lines
                beginningLines = beginningLines + '\n    }\n'
            """
            #BeginningLines old method ends here

            #New method of BeginningLines starts here
            
            if self.dlg.radioButtonClockConf.isChecked():
                documentClock = Metadata.Clock(selectedClockCurrentLocal, selectedClockBeginningLocal, selectedClockEndLocal, selectedClockMultiplier, selectedClockRange, selectedClockStep)
                documentMetadata = Metadata("1.0", "document", layerName, documentClock)
                #print( json.dumps(documentMetadata.getMetaDict()) )
            else:
                documentMetadata = Metadata("1.0", "document", layerName)
                #print( documentMetadata.getMetaDict() )

            beginningLines ='[\n' +  json.dumps( documentMetadata.getMetaDict(), indent=4 )
            
            #New method of BeginningLines ends here
            

            featureLines = ''

            for feature in selectedLayer.getFeatures():
                #if time interval selected, datetime attribute selected and localized by selected time zone.
                #beginning and end localized datetime will be added to label and billboard objects.
                if self.dlg.radioButtonSetupTime.isChecked():
                    beginningDateTime =  feature.attribute(selectedTimeBeginningField)
                    endDateTime =  feature.attribute(selectedTimeEndField)
                    pyBeginningDateTime = beginningDateTime.toPyDateTime()
                    pyEndDateTime = endDateTime.toPyDateTime()
                    beginningLocalDateTime = (timeZone.localize(pyBeginningDateTime)).isoformat()
                    endLocalDateTime = (timeZone.localize(pyEndDateTime)).isoformat()
                if self.dlg.comboBoxHeight.currentText() != 'Not Selected':
                    selectedHeight = str(feature.attribute(selectedHeightField))
                else:
                    selectedHeight = '10000'
                positionLines = '\n    ,{\n        "position": {\n            "cartographicDegrees": [\n                "'
                positionLines = positionLines + str(round(feature.geometry().asPoint().x(),7))
                positionLines = positionLines + '" \n                ,"'
                positionLines = positionLines + str(round(feature.geometry().asPoint().y(),7))
                positionLines = positionLines + '" \n                ,'
                positionLines = positionLines + selectedHeight
                positionLines = positionLines + '\n            ]\n        }\n'
                if self.dlg.comboBoxText.isEnabled() and self.dlg.comboBoxText.currentText() != 'Not Selected':
                    labelLines = '        ,"label": {\n            "text": "'
                    labelLines = labelLines + str(feature.attribute(selectedTextField))
                    labelLines = labelLines + '",\n'
                    if self.dlg.radioButtonSetupTime.isChecked():
                        labelLines = labelLines + '            "interval": "'+beginningLocalDateTime+'/'+endLocalDateTime+'",\n'
                    labelLines = labelLines + '            "fillColor": {"rgba": [255,255,255,255]},\n            "scaleByDistance": { "nearFarScalar": [300,5,3000,1] },\n            "disableDepthTestDistance": 9999999999,\n            "outlineWidth": 3,\n            "outlineColor": {"rgba": [0, 0, 0, 255]}, \n            "style": "FILL_AND_OUTLINE", \n            "heightReference": "RELATIVE_TO_GROUND"\n        }\n'
                else:
                    #labelLines = '        ,"commentAboutLabels" : "Skipped"\n'  
                    labelLines = ' '
                if self.dlg.comboBoxImage.isEnabled() and self.dlg.comboBoxImage.currentText() != 'Not Selected':
                    billboardLines = '        ,"billboard": {\n            "image": [\n                {\n                "uri": "'
                    billboardLines = billboardLines + str(feature.attribute(selectedImageField))
                    billboardLines = billboardLines + '"\n'
                    if self.dlg.radioButtonSetupTime.isChecked():
                        billboardLines = billboardLines + '                ,"interval":"'+beginningLocalDateTime+'/'+endLocalDateTime+'"\n'
                    billboardLines = billboardLines + '                }\n            ],\n            "scale": 1.0,\n            "heightReference": "RELATIVE_TO_GROUND",\n            "pixelOffset": {\n                "cartesian2": [0, -50]\n                }\n        }\n'
                else:
                    #billboardLines = '        ,"commentAboutImages" : "Skipped"\n'
                    billboardLines = ''
                idLines = '        ,"id": "'
                idLines = idLines + str(feature.attribute(selectedIdField))
                idLines = idLines + '"\n'
                if self.dlg.comboBoxName.currentText() != 'Not Selected':
                    nameLines = '        ,"name": "'
                    nameLines = nameLines + str(feature.attribute(selectedNameField))
                    nameLines = nameLines + '"\n'
                else:
                    nameLines = ''

                if self.dlg.comboBoxModel.isEnabled() and self.dlg.comboBoxModel.currentText() != 'Not Selected':
                    modelLines = '        ,"model": {\n            "gltf" : "'
                    modelLines = modelLines + str(feature.attribute(selectedModelField))
                    modelLines = modelLines + '"\n'
                    if self.dlg.radioButtonSetupTime.isChecked():
                        modelLines=modelLines + '            ,"interval":"'+beginningLocalDateTime+'/'+endLocalDateTime+'"\n'
                    modelLines=modelLines + '            ,"nodeTransformations": {\n                "'
                    modelLines = modelLines + str(feature.attribute(selectedNodeField))
                    modelLines = modelLines + '": {\n                    "rotation": {\n                        "unitQuaternion": [\n                            0.0, '
                    #Quaternion calculation
                    rotationAngleZ = -math.radians(feature.attribute(selectedAzimuthField))
                    #print(feature.attribute(selectedAzimuthField), " ", rotationAngleZ," <--angle\n")
                    sinRotationAngleHalfZ = math.sin(rotationAngleZ/2)
                    #print(sinRotationAngleHalfZ, " <--y value of quaternion\n")
                    cosRotationAngleHalfZ = math.cos(rotationAngleZ/2)
                    #print(cosRotationAngleHalfZ, " <--w value of quaternion\n\n")
                    modelLines = modelLines + str( sinRotationAngleHalfZ )
                    
                    modelLines = modelLines + ', 0.0 , '
                    modelLines = modelLines + str( cosRotationAngleHalfZ )
                    modelLines = modelLines + '\n                        ]\n                    }\n                }\n            }\n            ,"minimumPixelSize": 24\n            ,"maximumScale": 10000\n        }\n'

                else:
                    modelLines=''

                if self.dlg.comboBoxDescription.currentText() != 'Not Selected':
                    descriptionLines = '        ,"description": "'
                    descriptionLines = descriptionLines + str(feature.attribute(selectedDescriptionField))
                    descriptionLines = descriptionLines + '"\n    }'
                else:
                    descriptionLines = '\n    }'
                #print(feature.attribute(selectedTimeBeginningField).toString('yyyy-MM-ddThh:mm:sszz'))
                #print(feature.attribute(selectedTimeEndField).toString('yyyy-MM-ddThh:mm:ss'))
                #print(selectedTimeZone)
                

                featureLines = featureLines + positionLines + labelLines + billboardLines + idLines + nameLines + modelLines + descriptionLines
                

            wholeDocument = beginningLines + featureLines + '\n]'

            exportedFile.write(wholeDocument)
            exportedFile.close()

            pass
