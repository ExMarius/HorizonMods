/** Translate the hand-authored blocks to separate vanilla item models.
 * Geometry is not generated from a shape algorithm: source placements are in
 * ../design.js. Vanilla rotations are limited; see the conversion report. */
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
import {deflateSync} from 'node:zlib';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {platforma,atelier,ramp,palette} from '../design.js';
import {body,roof,interior,underbed,steeringPosition,steeringZ,compactCabPiece} from '../cabina-concept-detaliat.js';
import {revisedRearPart} from '../cabina-geometry.js';
const cab=[...body.map(p=>compactCabPiece(p,'body')),...roof.map(p=>compactCabPiece(p,'roof')),...interior.map(p=>compactCabPiece(p,'interior'))];
const compactFlatbed=platforma.filter(([kind,x,y,z])=>!(kind==='amber'&&y===2.73&&z===-1.30) && !(z===2.08 && ((kind==='chassis'&&x===-1.04)||(kind==='steel'&&x===-1.24)||(kind==='dark'&&x===-1.263)))).map(revisedRearPart).concat(underbed);
const here=dirname(fileURLToPath(import.meta.url));
const out=resolve(process.argv[2]||join(here,'assets'));
const scale=4, unit=16/scale;
const modelDir=join(out,'models/item'),itemDir=join(out,'items'),textureDir=join(out,'textures/item');
for(const d of [modelDir,itemDir,textureDir])mkdirSync(d,{recursive:true});
const names=Object.keys(palette),textures=Object.fromEntries(names.map(n=>[n.toLowerCase(),`vehicle:item/horizon_service_${n.toLowerCase()}`]));
const report=[];
function vec(x,y,z){return [8+x*unit,8+y*unit,8+z*unit].map(n=>+n.toFixed(5))}
function cuboid(p,index,part){
 const [mat,x,y,z,w,h,d,rx=0]=p;
 if(!textures[mat.toLowerCase()]||![x,y,z,w,h,d,rx].every(Number.isFinite)||w<=0||h<=0||d<=0)throw Error('Invalid authored part '+part+' '+index);
 const e={name:`${part}_${index}`,from:vec(x-w/2,y-h/2,z-d/2),to:vec(x+w/2,y+h/2,z+d/2),
 faces:Object.fromEntries(['north','south','east','west','up','down'].map(face=>[face,{uv:[0,0,16,16],texture:'#'+mat.toLowerCase()}]))};
 for(let i=0;i<3;i++)if(e.from[i]<-16||e.to[i]>32||e.from[i]>=e.to[i])throw Error('vanilla item bounds exceeded: '+e.name);
 if(rx){
  const degrees=rx*180/Math.PI;
  const snapped=Math.max(-45,Math.min(45,Math.round(degrees/22.5)*22.5));
  report.push({part,index,originalDegrees:+degrees.toFixed(4),vanillaDegrees:snapped});
  if(snapped)e.rotation={origin:vec(x,y,z),axis:'x',angle:snapped};
 }
 return e;
}
// Same detailed steering wheel used by the existing Horizon vehicles, in the
// original X/Y plane. Translate its origin to the driver's wheel position.
const [sx,sy]=steeringPosition,sz=steeringZ;
const steeringSource=JSON.parse(readFileSync(resolve(here,'../../../../content/assets/gokart/models/block/go_kart_steering_wheel.json'),'utf8'));
const steeringModel=structuredClone(steeringSource), rimScale=1.76/6.3, steeringCenter=vec(sx,sy,sz);
for(const part of steeringModel.elements){
 for(const key of ['from','to'])part[key]=part[key].map((v,i)=>+(steeringCenter[i]+(v-8)*rimScale).toFixed(5));
 if(part.rotation){
  part.rotation.origin=part.rotation.origin.map((v,i)=>+(steeringCenter[i]+(v-8)*rimScale).toFixed(5));
  // Small 12 degree details cannot be represented as vanilla item rotations.
  if(Math.abs(part.rotation.angle)===12)delete part.rotation;
 }
}
steeringModel.textures=Object.fromEntries(Object.entries(steeringModel.textures).map(([k,v])=>[k,v.replace('gokart:block/','horizonvehicles:item/')]));
// Fixed shaft joins the rim to the dashboard without entering the driver's seat.
cab.push(['dark',sx,1.43,(sz-1.68)/2,.075,.075,sz+1.68]);
// Wheel model is centred at its axle for an independent display spin.
// Use the same complete Horizon sports wheel used by the Logan. Convert its
// two 67.5 degree pieces to the equivalent vanilla-compatible -22.5 boxes,
// then resize about the axle to preserve the recovery truck wheel envelope.
const sportsSource=JSON.parse(readFileSync(resolve(here,'../../../../content/assets/gokart/models/block/wheel_sports.json'),'utf8'));
const sportsWheel=structuredClone(sportsSource);
for(const [i,j] of [[6,7],[7,6]]) {
 for(const k of ['from','to']) sportsWheel.elements[i][k].splice(1,2,...sportsSource.elements[j][k].slice(1,3));
 sportsWheel.elements[i].faces=structuredClone(sportsSource.elements[j].faces);
 sportsWheel.elements[i].rotation.angle=-22.5;
}
for(const part of sportsWheel.elements){
 for(const key of ['from','to'])part[key]=part[key].map((v,i)=>+(8+(v-8)*(i===0?1.32/5.56:3.6/8)).toFixed(5));
 if(part.rotation)part.rotation.origin=part.rotation.origin.map((v,i)=>+(8+(v-8)*(i===0?1.32/5.56:3.6/8)).toFixed(5));
}
sportsWheel.textures=Object.fromEntries(Object.entries(sportsWheel.textures).map(([k,v])=>[k,v.replace('gokart:block/','horizonvehicles:item/')]));
// Unit-length cable at the item origin; the Paper rig stretches it along local Y.
const cable=[['silver',0,0,0,.036,1,.036]];
const models={horizon_service_cab:cab,horizon_service_flatbed:compactFlatbed,horizon_service_workshop:atelier,horizon_service_ramp:ramp,horizon_service_cable:cable};
for(const [name,pieces] of Object.entries(models)){
 const body={textures,elements:pieces.map((p,i)=>cuboid(p,i,name))};
 writeFileSync(join(modelDir,name+'.json'),JSON.stringify(body,null,2)+'\n');
 writeFileSync(join(itemDir,name+'.json'),JSON.stringify({model:{type:'minecraft:model',model:'vehicle:item/'+name}},null,2)+'\n');
}
writeFileSync(join(modelDir,'horizon_service_steering.json'),JSON.stringify(steeringModel,null,2)+'\n');
writeFileSync(join(itemDir,'horizon_service_steering.json'),JSON.stringify({model:{type:'minecraft:model',model:'vehicle:item/horizon_service_steering'}},null,2)+'\n');
writeFileSync(join(modelDir,'horizon_service_wheel.json'),JSON.stringify(sportsWheel,null,2)+'\n');
writeFileSync(join(itemDir,'horizon_service_wheel.json'),JSON.stringify({model:{type:'minecraft:model',model:'vehicle:item/horizon_service_wheel'}},null,2)+'\n');
// Minimal RGBA PNG, retaining an actual alpha channel for the glass texture.
function crc32(buf){let c=0xffffffff;for(const x of buf){c^=x;for(let i=0;i<8;i++)c=(c>>>1)^((c&1)?0xedb88320:0)}return (c^0xffffffff)>>>0}
function chunk(type,data){const t=Buffer.from(type),len=Buffer.alloc(4),crc=Buffer.alloc(4);len.writeUInt32BE(data.length);crc.writeUInt32BE(crc32(Buffer.concat([t,data])));return Buffer.concat([len,t,data,crc])}
function png(hex,alpha=255){const ihdr=Buffer.alloc(13);ihdr.writeUInt32BE(1,0);ihdr.writeUInt32BE(1,4);ihdr[8]=8;ihdr[9]=6;const rgba=Buffer.from(hex.slice(1),'hex');return Buffer.concat([Buffer.from('89504e470d0a1a0a','hex'),chunk('IHDR',ihdr),chunk('IDAT',deflateSync(Buffer.from([0,...rgba,alpha]))),chunk('IEND',Buffer.alloc(0))])}
for(const [name,color] of Object.entries(palette))writeFileSync(join(textureDir,'horizon_service_'+name.toLowerCase()+'.png'),png(color,name==='glass'?90:255));
writeFileSync(join(out,'conversion-report.json'),JSON.stringify({itemDisplayScale:scale,models:Object.fromEntries(Object.entries(models).map(([name,p])=>[name,p.length])),rotationApproximations:report,notes:['Wheel uses the existing Horizon sports wheel model; steering uses the Horizon steering model.','Glass alpha must be verified in the target Minecraft client.','Placement requires in-game validation.']},null,2)+'\n');
console.log('Converted',Object.keys(models).length,'separate model assets to',out);
