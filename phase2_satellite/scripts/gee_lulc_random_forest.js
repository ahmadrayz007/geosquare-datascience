// ============================================================
// LAND USE LAND COVER (LULC) CLASSIFICATION USING RANDOM FOREST
// Google Earth Engine Script
// ============================================================

// ----- REGION OF INTEREST -----
var roi1 = ee.FeatureCollection('projects/gen-lang-client-0877865783/assets/tangerang_selatan_kelurahan_RBI_polygons');
var roi2 = ee.FeatureCollection('projects/gen-lang-client-0877865783/assets/oku_kecamatan_RBI_polygons');
var roi = roi1.merge(roi2);

// ----- TRAINING POINTS -----
var tangselPoints = ee.FeatureCollection('projects/gen-lang-client-0877865783/assets/tangsel_points');
var okuPoints = ee.FeatureCollection('projects/gen-lang-client-0877865783/assets/oku_points');
var trainingPoints = tangselPoints.merge(okuPoints);

// ----- CLASS DEFINITIONS -----
// 1: Water (#419bdf)
// 2: Trees (#397d49)
// 4: Flooded Vegetation (#7a87c6)
// 5: Crops (#e49635)
// 7: Built Area (#c4281b)
// 8: Bare Ground (#a59b8f)
// 11: Rangeland (#e3e2c3)

var classNames = ee.Dictionary({
  '1': 'Water',
  '2': 'Trees',
  '4': 'Flooded Vegetation',
  '5': 'Crops',
  '7': 'Built Area',
  '8': 'Bare Ground',
  '11': 'Rangeland'
});

var classPalette = [
  '#419bdf',  // 1: Water
  '#397d49',  // 2: Trees
  '#7a87c6',  // 4: Flooded Vegetation
  '#e49635',  // 5: Crops
  '#c4281b',  // 7: Built Area
  '#a59b8f',  // 8: Bare Ground
  '#e3e2c3'   // 11: Rangeland
];

var classValues = [1, 2, 4, 5, 7, 8, 11];
var classLabels = ['Water', 'Trees', 'Flooded Vegetation', 'Crops', 'Built Area', 'Bare Ground', 'Rangeland'];

// ----- DATE RANGE -----
var startDate = '2025-01-01';
var endDate = '2025-12-31';

// ----- SENTINEL-2 IMAGE COLLECTION -----
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(roi)
  .filterDate(startDate, endDate)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));

// ----- CLOUD MASKING FUNCTION -----
function maskS2Clouds(image) {
  var scl = image.select('SCL');
  var mask = scl.neq(3)  // Cloud shadows
    .and(scl.neq(8))     // Clouds medium probability
    .and(scl.neq(9))     // Clouds high probability
    .and(scl.neq(10));   // Cirrus
  return image.updateMask(mask);
}

// ----- CALCULATE INDICES -----
function addIndices(image) {
  // NDVI - Normalized Difference Vegetation Index
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');

  // NDWI - Normalized Difference Water Index
  var ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI');

  // NDBI - Normalized Difference Built-up Index
  var ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI');

  // SAVI - Soil Adjusted Vegetation Index
  var savi = image.expression(
    '((NIR - RED) / (NIR + RED + 0.5)) * 1.5', {
      'NIR': image.select('B8'),
      'RED': image.select('B4')
    }).rename('SAVI');

  // EVI - Enhanced Vegetation Index
  var evi = image.expression(
    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
      'NIR': image.select('B8'),
      'RED': image.select('B4'),
      'BLUE': image.select('B2')
    }).rename('EVI');

  // BSI - Bare Soil Index
  var bsi = image.expression(
    '((SWIR1 + RED) - (NIR + BLUE)) / ((SWIR1 + RED) + (NIR + BLUE))', {
      'SWIR1': image.select('B11'),
      'RED': image.select('B4'),
      'NIR': image.select('B8'),
      'BLUE': image.select('B2')
    }).rename('BSI');

  return image.addBands([ndvi, ndwi, ndbi, savi, evi, bsi]);
}

// ----- CREATE COMPOSITE -----
var composite = s2
  .map(maskS2Clouds)
  .map(addIndices)
  .median()
  .clip(roi);

// ----- SELECT BANDS FOR CLASSIFICATION -----
var bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12',
             'NDVI', 'NDWI', 'NDBI', 'SAVI', 'EVI', 'BSI'];

// ----- SAMPLE TRAINING DATA -----
var training = composite.select(bands).sampleRegions({
  collection: trainingPoints,
  properties: ['class_id'],
  scale: 10
});

// ----- SPLIT DATA (80% TRAINING, 20% VALIDATION) -----
var withRandom = training.randomColumn('random');
var trainSet = withRandom.filter(ee.Filter.lt('random', 0.8));
var testSet = withRandom.filter(ee.Filter.gte('random', 0.8));

print('Training samples:', trainSet.size());
print('Validation samples:', testSet.size());

// ----- TRAIN RANDOM FOREST CLASSIFIER -----
var classifier = ee.Classifier.smileRandomForest({
  numberOfTrees: 100,
  variablesPerSplit: null,  // sqrt of number of variables
  minLeafPopulation: 1,
  bagFraction: 0.5,
  seed: 42
}).train({
  features: trainSet,
  classProperty: 'class_id',
  inputProperties: bands
});

// ----- CLASSIFY IMAGE -----
var classified = composite.select(bands).classify(classifier);

// ----- ACCURACY ASSESSMENT -----
var trainAccuracy = classifier.confusionMatrix();
print('Training Confusion Matrix:', trainAccuracy);
print('Training Overall Accuracy:', trainAccuracy.accuracy());
print('Training Kappa:', trainAccuracy.kappa());

var validated = testSet.classify(classifier);
var testAccuracy = validated.errorMatrix('class_id', 'classification');
print('Validation Confusion Matrix:', testAccuracy);
print('Validation Overall Accuracy:', testAccuracy.accuracy());
print('Validation Kappa:', testAccuracy.kappa());
print('Validation Producers Accuracy:', testAccuracy.producersAccuracy());
print('Validation Consumers Accuracy:', testAccuracy.consumersAccuracy());

// ----- VARIABLE IMPORTANCE -----
var importance = ee.Dictionary(classifier.explain()).get('importance');
print('Variable Importance:', importance);

// ----- VISUALIZATION -----
// True Color Composite
Map.centerObject(roi, 10);
Map.addLayer(composite, {bands: ['B4', 'B3', 'B2'], min: 0, max: 3000}, 'Sentinel-2 RGB', false);

// False Color Composite (Vegetation)
Map.addLayer(composite, {bands: ['B8', 'B4', 'B3'], min: 0, max: 4000}, 'Sentinel-2 False Color', false);

// NDVI
Map.addLayer(composite.select('NDVI'), {min: -1, max: 1, palette: ['red', 'yellow', 'green']}, 'NDVI', false);

// Classification Result
Map.addLayer(classified, {min: 1, max: 11, palette: classPalette}, 'LULC Classification');

// Training Points with class colors
Map.addLayer(trainingPoints.filter(ee.Filter.eq('class_id', 1)).style({color: '#419bdf', pointSize: 5}), {}, 'Points: Water', false);
Map.addLayer(trainingPoints.filter(ee.Filter.eq('class_id', 2)).style({color: '#397d49', pointSize: 5}), {}, 'Points: Trees', false);
Map.addLayer(trainingPoints.filter(ee.Filter.eq('class_id', 4)).style({color: '#7a87c6', pointSize: 5}), {}, 'Points: Flooded Vegetation', false);
Map.addLayer(trainingPoints.filter(ee.Filter.eq('class_id', 5)).style({color: '#e49635', pointSize: 5}), {}, 'Points: Crops', false);
Map.addLayer(trainingPoints.filter(ee.Filter.eq('class_id', 7)).style({color: '#c4281b', pointSize: 5}), {}, 'Points: Built Area', false);
Map.addLayer(trainingPoints.filter(ee.Filter.eq('class_id', 8)).style({color: '#a59b8f', pointSize: 5}), {}, 'Points: Bare Ground', false);
Map.addLayer(trainingPoints.filter(ee.Filter.eq('class_id', 11)).style({color: '#e3e2c3', pointSize: 5}), {}, 'Points: Rangeland', false);

// ROI Boundary
Map.addLayer(roi.style({color: 'red', fillColor: '00000000', width: 2}), {}, 'ROI Boundary');

// ----- LEGEND -----
var legend = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '8px 15px'
  }
});

var legendTitle = ui.Label({
  value: 'LULC Classes',
  style: {fontWeight: 'bold', fontSize: '16px', margin: '0 0 8px 0'}
});
legend.add(legendTitle);

for (var i = 0; i < classValues.length; i++) {
  var colorBox = ui.Label({
    style: {
      backgroundColor: classPalette[i],
      padding: '8px',
      margin: '0 8px 4px 0'
    }
  });
  var description = ui.Label({
    value: classLabels[i],
    style: {margin: '0 0 4px 0'}
  });
  var row = ui.Panel({
    widgets: [colorBox, description],
    layout: ui.Panel.Layout.Flow('horizontal')
  });
  legend.add(row);
}

Map.add(legend);

// ----- CALCULATE AREA PER CLASS -----
var areaImage = ee.Image.pixelArea().addBands(classified);

var areaByClass = areaImage.reduceRegion({
  reducer: ee.Reducer.sum().group({
    groupField: 1,
    groupName: 'class_id'
  }),
  geometry: roi,
  scale: 10,
  maxPixels: 1e13
});

print('Area by Class (sq meters):', areaByClass);

// ----- EXPORT CLASSIFIED IMAGE -----
Export.image.toDrive({
  image: classified,
  description: 'LULC_Classification_2025',
  folder: 'GEE_LULC',
  fileNamePrefix: 'LULC_RandomForest_2025',
  region: roi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

// ----- EXPORT TO ASSET -----
Export.image.toAsset({
  image: classified,
  description: 'LULC_Classification_Asset_2024',
  assetId: 'projects/gen-lang-client-0877865783/assets/LULC_RandomForest_2025',
  region: roi,
  scale: 10,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

// ----- EXPORT ACCURACY METRICS -----
var accuracyFeature = ee.Feature(null, {
  'training_accuracy': trainAccuracy.accuracy(),
  'training_kappa': trainAccuracy.kappa(),
  'validation_accuracy': testAccuracy.accuracy(),
  'validation_kappa': testAccuracy.kappa()
});

Export.table.toDrive({
  collection: ee.FeatureCollection([accuracyFeature]),
  description: 'LULC_Accuracy_Metrics',
  folder: 'GEE_LULC',
  fileNamePrefix: 'accuracy_metrics',
  fileFormat: 'CSV'
});

print('Script completed! Check the Tasks tab to run exports.');
