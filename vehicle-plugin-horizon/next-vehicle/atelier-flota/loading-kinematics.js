/** Geometry and timing for the browser demonstration only (not gameplay). */
export const LOADING={deckTop:.86,deckEnd:5.35,rampLength:2.48,wheelbase:3.30,
 carStart:9.8,carLoaded:2.60,rampDuration:2.8,driveDuration:7,holdDuration:1};
export const rampAngle=Math.asin(LOADING.deckTop/LOADING.rampLength);
export const rampRun=Math.sqrt(LOADING.rampLength**2-LOADING.deckTop**2);
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
