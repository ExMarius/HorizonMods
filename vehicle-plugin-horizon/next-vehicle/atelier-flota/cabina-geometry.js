/* Shared authored transforms for the approved cab concept and item exporter. */
export const cabLength=.78, cabRear=-.40, rearShift=.70;
export const cabZ=z=>cabRear+(z-cabRear)*cabLength+.10;
const frontAxleZ=cabZ(-2.05);
export function compactCabPart(part){
 const [kind,x,y,z]=part, compact=[...part];
 compact[3]=cabZ(z);compact[6]*=cabLength;
 // Shorter upper cabin, retaining the lower pillar joins.
 if(y>=2.70) compact[2]-=.12;
 if(kind==='white' && Math.abs(x)===1.24 && y===2.04 && (z===-2.39 || z===-.40)) {
  compact[2]-=.06; compact[5]-=.12;
 }
 // Backrests and headrests meet the rear bulkhead rather than floating away.
 if(kind==='seat' && (y===1.38 || y===1.87)) compact[3]+=.12;
 if(kind==='white' && Math.abs(x)===1.31 && y===1.13 && z===-2.05) {
  compact[3]=frontAxleZ;compact[6]=part[6];
 }
 if(kind==='white' && Math.abs(x)===1.31 && y===.84 && z===-2.65) {
  compact[3]=frontAxleZ-.60;compact[6]=part[6];
 }
 if(kind==='white' && Math.abs(x)===1.31 && y===.84 && z===-1.44) {
  compact[3]=frontAxleZ+.61;compact[6]=part[6];
 }
 const door=kind==='white' && Math.abs(x)===1.30 && y===1.00 && z===-.925;
 const step=Math.abs(x)>=1.20 && y<=.52 && z===-.95;
 if(door||step){
  const back=compact[3]+compact[6]/2;
  const front=Math.max(compact[3]-compact[6]/2,frontAxleZ+.56);
  compact[3]=(front+back)/2;compact[6]=back-front;
 }
 return compact;
}
export function revisedRearPart(part){
 const [kind,x,y,z]=part;
 const axle=kind==='chassis' && x===0 && y===.35 && z===3.92;
 const trim=kind==='dark' && Math.abs(x)===1.39 && [3.92,3.43,4.41].includes(z);
 const mudflap=kind==='dark' && Math.abs(x)===1.20 && y===.35 && z===4.49;
 if(!axle&&!trim&&!mudflap)return part;
 const revised=[...part];revised[3]-=rearShift;return revised;
}
