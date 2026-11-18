import fs from 'node:fs';
import path from 'node:path';
import * as topojson from '../../web/node_modules/topojson-client/src/index.js';

const world50Path = path.resolve('s:/Projekte/WHSMAP/web/node_modules/world-atlas/countries-50m.json');
const topo = JSON.parse(fs.readFileSync(world50Path, 'utf-8'));
const fc = topojson.feature(topo, topo.objects.countries);

const outPath = path.resolve('s:/Projekte/WHSMAP/pipeline/.cache/world_atlas_50m_raw.geojson');
fs.mkdirSync(path.dirname(outPath), { recursive: true });
fs.writeFileSync(outPath, JSON.stringify(fc));
console.log(`Extracted ${fc.features.length} real Natural Earth 50m country polygons to ${outPath}`);
