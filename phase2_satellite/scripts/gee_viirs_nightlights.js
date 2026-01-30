// ============================================================
// VIIRS NIGHT LIGHTS ANALYSIS
// Validasi Aktivitas Ekonomi - Tangerang Selatan vs OKU
// Google Earth Engine Script
// ============================================================

// ----- REGION OF INTEREST -----
var tangsel = ee.FeatureCollection('projects/gen-lang-client-0877865783/assets/tangerang_selatan_kelurahan_RBI_polygons');
var oku = ee.FeatureCollection('projects/gen-lang-client-0877865783/assets/oku_kecamatan_RBI_polygons');

// ----- DATE RANGE -----
var startDate = '2025-01-01';
var endDate = '2025-12-31';

// ----- VIIRS STRAY LIGHT CORRECTED NIGHTTIME LIGHTS -----
var viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
  .filterDate(startDate, endDate)
  .select('avg_rad');  // Average radiance

// ----- CREATE ANNUAL COMPOSITE -----
var nightLights = viirs.mean();

// Clip to both regions
var nightLightsTangsel = nightLights.clip(tangsel);
var nightLightsOku = nightLights.clip(oku);

// ----- VISUALIZATION -----
var nightLightsVis = {
  min: 0,
  max: 60,
  palette: ['000000', '0000FF', '00FFFF', 'FFFF00', 'FF0000', 'FFFFFF']
};

Map.centerObject(tangsel, 11);
Map.addLayer(nightLightsTangsel, nightLightsVis, 'Night Lights - Tangsel');
Map.addLayer(tangsel.style({color: 'cyan', fillColor: '00000000', width: 2}), {}, 'Tangsel Boundary');

Map.addLayer(nightLightsOku, nightLightsVis, 'Night Lights - OKU', false);
Map.addLayer(oku.style({color: 'yellow', fillColor: '00000000', width: 2}), {}, 'OKU Boundary', false);

// ----- STATISTICS PER REGION -----
// Tangerang Selatan
var statsTangsel = nightLightsTangsel.reduceRegion({
  reducer: ee.Reducer.mean()
    .combine(ee.Reducer.max(), '', true)
    .combine(ee.Reducer.min(), '', true)
    .combine(ee.Reducer.stdDev(), '', true),
  geometry: tangsel,
  scale: 500,
  maxPixels: 1e13
});

// OKU
var statsOku = nightLightsOku.reduceRegion({
  reducer: ee.Reducer.mean()
    .combine(ee.Reducer.max(), '', true)
    .combine(ee.Reducer.min(), '', true)
    .combine(ee.Reducer.stdDev(), '', true),
  geometry: oku,
  scale: 500,
  maxPixels: 1e13
});

print('=== NIGHT LIGHTS STATISTICS 2025 ===');
print('Tangerang Selatan:', statsTangsel);
print('Ogan Komering Ulu:', statsOku);

// ----- ZONAL STATISTICS PER KELURAHAN/KECAMATAN -----
var tangselWithNL = nightLightsTangsel.reduceRegions({
  collection: tangsel,
  reducer: ee.Reducer.mean().setOutputs(['nl_mean']),
  scale: 500
});

var okuWithNL = nightLightsOku.reduceRegions({
  collection: oku,
  reducer: ee.Reducer.mean().setOutputs(['nl_mean']),
  scale: 500
});

print('Tangsel Kelurahan with Night Lights:', tangselWithNL.limit(5));
print('OKU Kecamatan with Night Lights:', okuWithNL.limit(5));

// ----- TEMPORAL ANALYSIS (2020 vs 2025) -----
var viirs2020 = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
  .filterDate('2020-01-01', '2020-12-31')
  .select('avg_rad')
  .mean();

var viirs2025 = nightLights;

// Calculate absolute change
var nlChange = viirs2025.subtract(viirs2020).rename('nl_change');

// Calculate percentage change: ((2025 - 2020) / 2020) * 100
var nlChangePercent = viirs2025.subtract(viirs2020)
  .divide(viirs2020.where(viirs2020.eq(0), 0.1)) // Avoid division by zero
  .multiply(100)
  .rename('nl_change_percent');

// Clip to regions
var nlChangeTangsel = nlChange.clip(tangsel);
var nlChangeOku = nlChange.clip(oku);
var nlChangePercentTangsel = nlChangePercent.clip(tangsel);
var nlChangePercentOku = nlChangePercent.clip(oku);

// Visualization for absolute change
var changeVis = {
  min: -10,
  max: 10,
  palette: ['FF0000', 'FFFF00', '00FF00']  // Red = decrease, Yellow = no change, Green = increase
};

// Visualization for percentage change
var changePercentVis = {
  min: -50,
  max: 50,
  palette: ['FF0000', 'FFFF00', '00FF00']
};

Map.addLayer(nlChangeTangsel, changeVis, 'NL Change (Absolute) Tangsel 2020-2025', false);
Map.addLayer(nlChangeOku, changeVis, 'NL Change (Absolute) OKU 2020-2025', false);
Map.addLayer(nlChangePercentTangsel, changePercentVis, 'NL Change (%) Tangsel 2020-2025', false);
Map.addLayer(nlChangePercentOku, changePercentVis, 'NL Change (%) OKU 2020-2025', false);

// ----- CHANGE STATISTICS -----
// Absolute change
var changeTangsel = nlChangeTangsel.reduceRegion({
  reducer: ee.Reducer.mean()
    .combine(ee.Reducer.sum(), '', true)
    .combine(ee.Reducer.stdDev(), '', true),
  geometry: tangsel,
  scale: 500,
  maxPixels: 1e13
});

var changeOku = nlChangeOku.reduceRegion({
  reducer: ee.Reducer.mean()
    .combine(ee.Reducer.sum(), '', true)
    .combine(ee.Reducer.stdDev(), '', true),
  geometry: oku,
  scale: 500,
  maxPixels: 1e13
});

// Percentage change
var changePercentTangsel = nlChangePercentTangsel.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: tangsel,
  scale: 500,
  maxPixels: 1e13
});

var changePercentOku = nlChangePercentOku.reduceRegion({
  reducer: ee.Reducer.mean(),
  geometry: oku,
  scale: 500,
  maxPixels: 1e13
});

print('=== NIGHT LIGHTS CHANGE 2020-2025 ===');
print('--- Tangerang Selatan ---');
print('Absolute Change (mean, sum, stdDev):', changeTangsel);
print('Percentage Change (mean %):', changePercentTangsel);
print('');
print('--- Ogan Komering Ulu ---');
print('Absolute Change (mean, sum, stdDev):', changeOku);
print('Percentage Change (mean %):', changePercentOku);

// ----- GROWTH HOTSPOTS ANALYSIS -----
// Identify areas with significant growth (> 5 radiance increase)
var growthHotspotsTangsel = nlChangeTangsel.gt(5).selfMask();
var growthHotspotsOku = nlChangeOku.gt(5).selfMask();

// Identify areas with decline (< -2 radiance decrease)
var declineAreasTangsel = nlChangeTangsel.lt(-2).selfMask();
var declineAreasOku = nlChangeOku.lt(-2).selfMask();

Map.addLayer(growthHotspotsTangsel, {palette: ['00FF00']}, 'Growth Hotspots Tangsel (>5)', false);
Map.addLayer(growthHotspotsOku, {palette: ['00FF00']}, 'Growth Hotspots OKU (>5)', false);
Map.addLayer(declineAreasTangsel, {palette: ['FF0000']}, 'Decline Areas Tangsel (<-2)', false);
Map.addLayer(declineAreasOku, {palette: ['FF0000']}, 'Decline Areas OKU (<-2)', false);

// Count growth/decline pixels
var growthAreaTangsel = growthHotspotsTangsel.multiply(ee.Image.pixelArea()).reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: tangsel,
  scale: 500,
  maxPixels: 1e13
});

var growthAreaOku = growthHotspotsOku.multiply(ee.Image.pixelArea()).reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: oku,
  scale: 500,
  maxPixels: 1e13
});

print('');
print('=== GROWTH HOTSPOTS AREA (sq km) ===');
print('Tangsel growth area:', ee.Number(growthAreaTangsel.get('nl_change')).divide(1e6));
print('OKU growth area:', ee.Number(growthAreaOku.get('nl_change')).divide(1e6));

// ----- ZONAL CHANGE PER ADMIN UNIT -----
var tangselWithChange = nlChangeTangsel.reduceRegions({
  collection: tangsel,
  reducer: ee.Reducer.mean().setOutputs(['nl_change_mean']),
  scale: 500
});

var okuWithChange = nlChangeOku.reduceRegions({
  collection: oku,
  reducer: ee.Reducer.mean().setOutputs(['nl_change_mean']),
  scale: 500
});

print('');
print('=== TOP GROWING AREAS ===');
print('Tangsel (by kelurahan):', tangselWithChange.sort('nl_change_mean', false).limit(5));
print('OKU (by kecamatan):', okuWithChange.sort('nl_change_mean', false).limit(5));

// ----- LEGEND -----
var legend = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '8px 15px'
  }
});

var legendTitle = ui.Label({
  value: 'Night Lights Radiance',
  style: {fontWeight: 'bold', fontSize: '14px', margin: '0 0 8px 0'}
});
legend.add(legendTitle);

var legendColors = ['000000', '0000FF', '00FFFF', 'FFFF00', 'FF0000', 'FFFFFF'];
var legendLabels = ['0 (Dark)', '10', '20', '30', '50', '60+ (Bright)'];

for (var i = 0; i < legendColors.length; i++) {
  var colorBox = ui.Label({
    style: {
      backgroundColor: '#' + legendColors[i],
      padding: '8px',
      margin: '0 8px 4px 0',
      border: '1px solid gray'
    }
  });
  var description = ui.Label({
    value: legendLabels[i],
    style: {margin: '0 0 4px 0'}
  });
  var row = ui.Panel({
    widgets: [colorBox, description],
    layout: ui.Panel.Layout.Flow('horizontal')
  });
  legend.add(row);
}

Map.add(legend);

// ----- EXPORT -----
// Export zonal statistics
Export.table.toDrive({
  collection: tangselWithNL,
  description: 'Tangsel_NightLights_Stats',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'tangsel_nightlights_2025',
  fileFormat: 'CSV'
});

Export.table.toDrive({
  collection: okuWithNL,
  description: 'OKU_NightLights_Stats',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'oku_nightlights_2025',
  fileFormat: 'CSV'
});

// Export raster
Export.image.toDrive({
  image: nightLightsTangsel,
  description: 'Tangsel_NightLights_Raster',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'tangsel_nightlights_2025',
  region: tangsel,
  scale: 500,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

Export.image.toDrive({
  image: nightLightsOku,
  description: 'OKU_NightLights_Raster',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'oku_nightlights_2025',
  region: oku,
  scale: 500,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

// ----- EXPORT CHANGE DATA (2020-2025) -----
// Export change rasters
Export.image.toDrive({
  image: nlChangeTangsel,
  description: 'Tangsel_NL_Change_2020_2025',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'tangsel_nl_change_2020_2025',
  region: tangsel,
  scale: 500,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

Export.image.toDrive({
  image: nlChangeOku,
  description: 'OKU_NL_Change_2020_2025',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'oku_nl_change_2020_2025',
  region: oku,
  scale: 500,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

// Export change statistics per admin unit
Export.table.toDrive({
  collection: tangselWithChange,
  description: 'Tangsel_NL_Change_Stats',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'tangsel_nl_change_stats_2020_2025',
  fileFormat: 'CSV'
});

Export.table.toDrive({
  collection: okuWithChange,
  description: 'OKU_NL_Change_Stats',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'oku_nl_change_stats_2020_2025',
  fileFormat: 'CSV'
});

// Export 2020 baseline for comparison
var viirs2020Tangsel = viirs2020.clip(tangsel);
var viirs2020Oku = viirs2020.clip(oku);

Export.image.toDrive({
  image: viirs2020Tangsel,
  description: 'Tangsel_NightLights_2020',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'tangsel_nightlights_2020',
  region: tangsel,
  scale: 500,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

Export.image.toDrive({
  image: viirs2020Oku,
  description: 'OKU_NightLights_2020',
  folder: 'GEE_VIIRS',
  fileNamePrefix: 'oku_nightlights_2020',
  region: oku,
  scale: 500,
  crs: 'EPSG:4326',
  maxPixels: 1e13
});

print('Script completed! Check Tasks tab for exports.');
print('');
print('=== INTERPRETATION GUIDE ===');
print('Higher radiance = More economic activity, urbanization');
print('Positive change = Growth/Development');
print('Negative change = Decline or power issues');
