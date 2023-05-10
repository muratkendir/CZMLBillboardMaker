def getCesiumPreview(wholeDocument):
  string1 = '<!DOCTYPE html>\
<html lang="en">\
<head>\
  <meta charset="utf-8">\
  <script src="https://cesium.com/downloads/cesiumjs/releases/1.100/Build/Cesium/Cesium.js"></script>\
  <link href="https://cesium.com/downloads/cesiumjs/releases/1.100/Build/Cesium/Widgets/widgets.css" rel="stylesheet">\
</head>\
<body>\
  <div id="cesiumContainer"></div>\
  <script>\
    const viewer = new Cesium.Viewer(\'cesiumContainer\', {\
      imageryProvider : new Cesium.OpenStreetMapImageryProvider({ url : \'https://a.tile.openstreetmap.org/\' }),\
      fullscreenButton:true });\
    czmlObject = ' + wholeDocument + ';'
  string2 = 'var dataSourcePromise = Cesium.CzmlDataSource.load(czmlObject);\
    viewer.dataSources.add(dataSourcePromise);\
    viewer.zoomTo(dataSourcePromise);'
  string3 = '  </script>\
 </div>\
</body>\
</html>'
  return string1+string2+string3