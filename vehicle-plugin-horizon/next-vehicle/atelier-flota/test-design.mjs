import assert from 'node:assert/strict';
import {cab,platforma,atelier,palette,wheels} from './design.js';
for(const [name,parts] of Object.entries({cab,platforma,atelier})){
 assert.ok(parts.length>20,`${name}: insufficient authored elements`);
 for(const p of parts){
  assert.ok(palette[p[0]],`${name}: unknown material ${p[0]}`);
  assert.ok(p.slice(1).every(Number.isFinite),`${name}: non-finite element`);
  assert.ok(p[4]>0&&p[5]>0&&p[6]>0,`${name}: invalid dimensions`);
 }
}
assert.ok(cab.filter(p=>p[0]==='glass').length>=4,'cab needs front, side and rear glass');
assert.ok(cab.filter(p=>p[0]==='seat').length>=6,'cab needs seats and backs');
assert.equal(wheels.length,4);
assert.notDeepEqual(platforma,atelier);
console.log('Authored parts, windows, seats and separate bodies validated.');
