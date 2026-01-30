// ============================================================
// CLIP BIOPAMA OIL PALM DATASET TO OKU REGION
// Google Earth Engine Script
// ============================================================

// ----- REGION OF INTEREST (OKU only) -----
var roi = ee.FeatureCollection('projects/gen-lang-client-0877865783/assets/oku_kecamatan_RBI_polygons');

// ----- BIOPAMA GLOBAL OIL PALM DATASET -----
var dataset = ee.ImageCollection('BIOPAMA/GlobalOilPalm/v1');

// Select the classification band
var opClass = dataset.select('classification');

// Mosaic all granules into a single image
var mosaic = opClass.mosaic();

// Clip to ROI
var clipped = mosaic.clip(roi);

// ----- OIL PALM CLASSES -----
// 1: Industrial closed-canopy oil palm plantations (RED)
// 2: Smallholder closed-canopy oil palm plantations (MAGENTA)
// 3: Other land covers (GRAY)

// ----- VISUALIZATION -----
var classificationVis = {
  min: 1,
  max: 3,
  palette: ['ff0000', 'ef00ff', '696969']
};

// Create mask for transparency (hide "other" class)
var mask = clipped.neq(3);
mask = mask.where(mask.eq(0), 0.6);

Map.centerObject(roi, 10);
Map.addLayer(roi.style({color: 'yellow', fillColor: '00000000', width: 2}), {}, 'OKU Boundary');
Map.addLayer(clipped.updateMask(mask), classificationVis, 'Oil Palm Classification', true);

// ----- LEGEND -----
var legend = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '8px 15px'
  }
});

var legendTitle = ui.Label({
  value: 'Oil Palm Classes (BIOPAMA)',
  style: {fontWeight: 'bold', fontSize: '16px', margin: '0 0 8px 0'}
});
legend.add(legendTitle);

var classes = [
  {color: '#ff0000', label: '1: Industrial Oil Palm'},
  {color: '#ef00ff', label: '2: Smallholder Oil Palm'},
  {color: '#696969', label: '3: Other Land Cover'}
];

classes.forEach(function(c) {
  var colorBox = ui.Label({
    style: {
      backgroundColor: c.color,
      padding: '8px',
      margin: '0 8px 4px 0'
    }
  });
  var description = ui.Label({
    value: c.label,
    style: {margin: '0 0 4px 0'}
  });
  var row = ui.Panel({
    widgets: [colorBox, description],
    layout: ui.Panel.Layout.Flow('horizontal')
  });
  legend.add(row);
});

Map.add(legend);

// ----- EXPORT CLIPPED IMAGE -----
Export.image.toDrive({
  image: clipped,
  description: 'OKU_OilPalm_BIOPAMA',
  folder: 'GEE_LULC',
  fileNamePrefix: 'oku_oilpalm_biopama',
  region: roi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

Export.image.toAsset({
  image: clipped,
  description: 'OKU_OilPalm_BIOPAMA_Asset',
  assetId: 'projects/gen-lang-client-0877865783/assets/oku_oilpalm_biopama',
  region: roi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

print('Script completed! Check Tasks tab to export clipped oil palm data.');
