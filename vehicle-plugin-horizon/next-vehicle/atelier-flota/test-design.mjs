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
const windows=cab.filter(p=>p[0]==='glass');
assert.equal(windows.length,4,'front, rear and both side windows must be present');
assert.ok(cab.filter(p=>p[0]==='seat').length>=6,'seats should be visible through windows');
const cabRoof=cab.find(p=>p[0]==='white' && p[1]===0 && p[3]===-1.18 && p[4]===2.05);
assert.ok(cabRoof && cabRoof[2]-cabRoof[5]/2>=2.5,'cab roof must provide extra headroom');
// Check at the centre of every pane, slightly inside the cabin, for an opaque
// wall (interior fixtures deeper inside must not be mistaken for window infill).
for(const point of [[0,1.68,-1.78],[-.90,1.68,-1.18],[.90,1.68,-1.18],[0,1.69,-.53]]){
 const [x,y,z]=point;
 assert.ok(!cab.some(p=>p[0]!=='glass'&&Math.abs(x-p[1])<p[4]/2&&Math.abs(y-p[2])<p[5]/2&&Math.abs(z-p[3])<p[6]/2),'opaque panel blocks a window centre');
}
for(const [x,y,z,scale] of platformWheels.slice(2)){
 assert.ok(Math.abs(y-.45*scale)<1e-8,'rear tyre must touch ground');
 assert.ok(y+.45*scale<=.70+1e-8,'rear tyre must remain below deck');
}
for(const [x,y,z,scale] of wheels.slice(2)){
 assert.ok(Math.abs(y-.45*scale)<1e-8,'workshop rear tyre must touch ground');
 assert.ok(y+.45*scale<=.64+1e-8,'rear tyre must remain below body floor');
}
// Check cylinders against axis-aligned body boxes, allowing only the axle to
// enter a tyre. This catches rails, guards and fender trim protruding into it;
// rotated pieces still require visual inspection.
for(const [name,parts,centres] of [['platforma',[...cab,...platforma],platformWheels],['atelier',[...cab,...atelier],wheels]]){
 for(const [x,y,z,scale] of centres){
  const radius=.45*scale,halfWidth=.165*scale;
  for(const part of parts){
   const [material,px,py,pz,w,h,d,rotation=0]=part;
   if(rotation||Math.abs(px-x)>=w/2+halfWidth)continue;
   const dy=Math.max(0,Math.abs(y-py)-h/2),dz=Math.max(0,Math.abs(z-pz)-d/2);
   if(dy*dy+dz*dz>=(radius-.005)**2)continue;
   const axle=material==='chassis'&&px===0&&Math.abs(py-y)<1e-9&&Math.abs(pz-z)<1e-9&&h<=.16&&d<=.14;
   assert.ok(axle,`${name}: wheel at ${x},${z} intersects ${JSON.stringify(part)}`);
  }
 }
}
assert.equal(wheels.length,4);assert.equal(platformWheels.length,4);
assert.notDeepEqual(platforma,atelier);
console.log('Window openings, interior, wheel clearances and separate bodies validated.');
