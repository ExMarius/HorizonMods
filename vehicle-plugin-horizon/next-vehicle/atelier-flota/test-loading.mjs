import assert from 'node:assert/strict';
import fs from 'node:fs';
import {LOADING,rampAngle,rampRun,rampRotation,groundHeight,carPose,sequence,loadingEligibility,winchCablePath,daciaTowPoint,WINCH} from './loading-kinematics.js';
import {platforma,ramp,platformWheels} from './design.js';
const near=(a,b,e=1e-8)=>assert.ok(Math.abs(a-b)<e,`${a} != ${b}`);
assert.equal(loadingEligibility(true).allowed,false);
assert.match(loadingEligibility(true).reason,/Decuplează/);
assert.equal(loadingEligibility(false).allowed,true);
near(LOADING.deckTop-LOADING.rampLength*Math.sin(rampRotation(1))-.05*Math.cos(rampRotation(1)),0);
near(LOADING.rampLength*Math.cos(rampRotation(1)),rampRun);
near(rampRotation(0),-Math.PI/2);
near(groundHeight(LOADING.deckEnd),LOADING.deckTop);
near(groundHeight(LOADING.deckEnd+rampRun),0);
near(carPose(LOADING.carStart).y,0);near(carPose(LOADING.carLoaded).y,LOADING.deckTop);
const initial=sequence(0),driving=sequence(LOADING.rampDuration+LOADING.driveDuration/2),done=sequence(99);
near(initial.ramp,0);near(initial.car.z,LOADING.carStart);near(driving.ramp,1);
assert.equal(driving.phase,'moving');assert.ok(driving.car.pitch>0);assert.equal(done.done,true);near(done.car.z,LOADING.carLoaded);near(done.ramp,0);
near(sequence(0,true).car.z,LOADING.carLoaded);near(sequence(99,true).car.z,LOADING.carStart);
// Sample the hinged panel throughout its motion. Its lowest point must stay
// above ground. Travel must only happen with both ramps fully deployed.
for(let i=0;i<=1000;i++){
 const r=rampRotation(i/1000);
 const lowest=LOADING.deckTop+Math.min(0,-LOADING.rampLength*Math.sin(r))-.05*Math.abs(Math.cos(r));
 assert.ok(lowest>=-1e-9,`ramp penetrates ground: ${lowest}`);
}
for(const unloading of [false,true])for(let t=0;t<20;t+=.025){
 const state=sequence(t,unloading);
 if(state.moving)near(state.ramp,1);
}
// A taut cable takes the straight route when clear; otherwise the supported
// roller routes it above the bed. Sample the whole winching motion, including
// the rope radius, not just the endpoints.
assert.equal(winchCablePath({x:0,y:.35,z:7.37}).length,3);
assert.equal(winchCablePath({x:0,y:1.4,z:6}).length,2);
const roller=platforma.find(p=>p[0]==='silver'&&p[1]===0&&p[2]===.93&&p[3]===WINCH.roller.z);
assert.ok(roller,'rear roller must exist at the route guide');
assert.ok(WINCH.roller.y-WINCH.radius>=roller[2]+roller[5]/2,'cable must clear roller top');
for(let t=0;t<=LOADING.rampDuration+LOADING.driveDuration;t+=.01){
 const eye=daciaTowPoint(sequence(t).car),points=winchCablePath(eye);
 assert.deepEqual(points[0],WINCH.outlet);assert.deepEqual(points.at(-1),eye);
 for(let i=0;i<points.length-1;i++)for(let j=0;j<=100;j++){
  const a=points[i],b=points[i+1],f=j/100,z=a.z+(b.z-a.z)*f,y=a.y+(b.y-a.y)*f;
  if(z>=WINCH.outlet.z&&z<=LOADING.deckEnd)assert.ok(y-WINCH.radius>=LOADING.deckTop,`cable intersects deck at t=${t}, z=${z}, y=${y}`);
  assert.ok(y-WINCH.radius>=0,'cable intersects ground');
 }
}
const dacia=JSON.parse(fs.readFileSync(new URL('../assets/user-edits/body_flash_1.json',import.meta.url),'utf8'));
const extent=i=>Math.max(...dacia.elements.map(e=>e.to[i]))-Math.min(...dacia.elements.map(e=>e.from[i]));
const carWidth=extent(0)*1.7/16,carLength=extent(2)*1.7/16,deck=platforma[0];
const bodyFront=-(Math.max(...dacia.elements.map(e=>e.to[2]))-8)*1.7/16;
const bodyRear=-(Math.min(...dacia.elements.map(e=>e.from[2]))-8)*1.7/16;
assert.ok(LOADING.carLoaded+bodyFront>.18,'car front must stop beyond winch fairlead');
assert.ok(LOADING.carLoaded+bodyRear<LOADING.deckEnd-.13,'car rear must clear folded ramps');
assert.ok(carWidth+.3<deck[4],`deck too narrow (${carWidth})`);assert.ok(carLength+.3<deck[6],`deck too short (${carLength})`);
assert.ok(ramp[0][4]>.6);assert.equal(platformWheels.length,4);
for(const x of [-1.03,1.03])assert.ok(Math.abs(Math.abs(x)-1.05)+.16<ramp[0][4]/2,'Dacia tire must fit ramp');
console.log(`Fits: Dacia ${carLength.toFixed(2)}×${carWidth.toFixed(2)}, deck ${deck[6]}×${deck[4]} blocks. Ramp hinge and sequence validated.`);
