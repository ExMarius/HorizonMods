import assert from 'node:assert/strict';
import {cab,platforma,atelier,ramp,palette,wheels,platformWheels} from './design.js';
for(const [name,parts] of Object.entries({cab,platforma,atelier,ramp})){
 assert.ok(parts.length>=(name==='ramp'?7:20),`${name}: insufficient authored elements`);
 for(const p of parts){
  assert.ok(palette[p[0]],`${name}: unknown material ${p[0]}`);
  assert.ok(p.slice(1).every(Number.isFinite),`${name}: non-finite element`);
  assert.ok(p[4]>0&&p[5]>0&&p[6]>0,`${name}: invalid dimensions`);
 }
}
assert.equal(cab.filter(p=>p[0]==='glass').length,0,'cab must not have windows');
// The opaque shells cover the front, side and rear above the doors.
for(const [x,z] of [[0,-1.84],[-.96,-1.15],[.96,-1.15],[0,-.47]]){
 assert.ok(cab.some(p=>p[0]==='white'&&p[1]===x&&p[3]===z&&p[5]>=1),'missing closed cab panel');
}
for(const [x,y,z,scale] of platformWheels.slice(2)){
 assert.ok(Math.abs(y-.45*scale)<1e-8,'rear tyre must touch ground');
 assert.ok(y+.45*scale<=.70+1e-8,'rear tyre must remain below deck');
}
for(const [x,y,z,scale] of wheels.slice(2)){
 assert.ok(Math.abs(y-.45*scale)<1e-8,'workshop rear tyre must touch ground');
 assert.ok(y+.45*scale<=.64+1e-8,'rear tyre must remain below body floor');
}
assert.equal(wheels.length,4);assert.equal(platformWheels.length,4);
assert.notDeepEqual(platforma,atelier);
console.log('Opaque cab, wheel clearances and separate bodies validated.');
