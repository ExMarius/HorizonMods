/** Geometry and timing for the browser demonstration only (not gameplay). */
export const LOADING={deckTop:.86,deckEnd:5.35,rampLength:2.48,wheelbase:3.30,
 carStart:9.8,carLoaded:2.64,rampDuration:2.8,driveDuration:7,holdDuration:1};
// The underside at the free tip must touch, never penetrate, the ground.
const rampHalfThickness=.05;
export const rampAngle=Math.asin(LOADING.deckTop/Math.hypot(LOADING.rampLength,rampHalfThickness))
 - Math.atan2(rampHalfThickness,LOADING.rampLength);
export const rampRun=LOADING.rampLength*Math.cos(rampAngle);
export function groundHeight(z){
 if(z<=LOADING.deckEnd)return LOADING.deckTop;
 if(z>=LOADING.deckEnd+rampRun)return 0;
 return LOADING.deckTop*(LOADING.deckEnd+rampRun-z)/rampRun;
}
/** Front faces -Z. The suspension is simplified to a rigid two-axle body. */
export function carPose(z){
 const front=groundHeight(z-LOADING.wheelbase/2),rear=groundHeight(z+LOADING.wheelbase/2);
 return {z,y:(front+rear)/2,pitch:Math.atan2(front-rear,LOADING.wheelbase),front,rear};
}
const clamp=n=>Math.max(0,Math.min(1,n));
const ease=n=>{const t=clamp(n);return t*t*(3-2*t)};
/** Closed ramps stand upright at the rear, clear of the loaded car. */
export function rampRotation(deployed){return -Math.PI/2+(Math.PI/2+rampAngle)*ease(deployed)}
export function sequence(seconds,unload=false){
 const {rampDuration,driveDuration,holdDuration,carStart,carLoaded}=LOADING;
 const phase=clamp((seconds-rampDuration)/driveDuration);
 const travel=ease(phase),first=unload?carLoaded:carStart,last=unload?carStart:carLoaded;
 const closeStart=rampDuration+driveDuration+holdDuration;
 const open=ease(seconds/rampDuration)*(1-ease((seconds-closeStart)/rampDuration));
 const total=closeStart+rampDuration;
 return {ramp:open,car:carPose(first+(last-first)*travel),moving:phase>0&&phase<1,
         done:seconds>=total,phase:seconds<rampDuration?'ramps':seconds<rampDuration+driveDuration?'moving':seconds<closeStart?'settling':seconds<total?'closing':'done'};
}

/** Preview rule only; real gameplay must inspect the server's coupling state. */
export function loadingEligibility(hasAttachedTrailer){
 return hasAttachedTrailer ? {allowed:false,reason:'Decuplează remorca sau utilajul înainte de încărcare.'} : {allowed:true,reason:''};
}

/** Preview-only fairlead path. A roller at the bed's rear supports the cable
 * from below only when the direct tension line would cut through the bed.
 * Coordinates are world-space, front is -Z. */
export const WINCH={outlet:{x:0,y:1.06,z:.18},roller:{x:0,y:.99,z:5.40},radius:.018};
export function winchCablePath(attachment){
 const {outlet,roller}=WINCH;
 if(![attachment.x,attachment.y,attachment.z].every(Number.isFinite))throw Error('Invalid winch attachment');
 const points=[outlet];
 if(attachment.z>roller.z){
  const f=(roller.z-outlet.z)/(attachment.z-outlet.z);
  const directY=outlet.y+(attachment.y-outlet.y)*f;
  if(directY<roller.y)points.push(roller);
 }
 points.push(attachment);
 return points;
}
/** Shared preview tow-eye location, not an in-game attachment. */
export const DACIA_TOW_EYE={x:0,y:.35,z:-2.43};
/** Same rigid-body transform as the 3D Dacia's tow-eye object. */
export function daciaTowPoint(pose){
 const {y,z}=DACIA_TOW_EYE,c=Math.cos(pose.pitch),s=Math.sin(pose.pitch);
 return {x:0,y:pose.y+.005+y*c-z*s,z:pose.z+y*s+z*c};
}
