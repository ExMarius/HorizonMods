/** Translate the hand-authored blocks to separate vanilla item models.
 * Geometry is not generated from a shape algorithm: source placements are in
 * ../design.js. Vanilla rotations are limited; see the conversion report. */
import {mkdirSync,writeFileSync} from 'node:fs';
import {deflateSync} from 'node:zlib';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {platforma,atelier,ramp,palette} from '../design.js';
import {cabinaNoua,steeringPosition} from '../cabina-noua.js';
import {cabZ,compactCabPart,revisedRearPart} from '../cabina-geometry.js';
const cab=cabinaNoua.map(compactCabPart);
const compactFlatbed=platforma.map(revisedRearPart);
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
// Four-sided steering rim, steering column and a cuboid octagonal tire are
// independent displays. These are explicit replacement pieces for preview
// torus/cylinder meshes, which vanilla item cuboids cannot represent.
const [sx,sy,szOriginal]=steeringPosition,sz=cabZ(szOriginal);
const steering=[
 ['black',sx,sy+.20,sz,.40,.05,.05],['black',sx,sy-.20,sz,.40,.05,.05],
 ['black',sx-.18,sy,sz,.05,.40,.05],['black',sx+.18,sy,sz,.05,.40,.05],
 ['dark',sx,sy,sz,.05,.33,.04],['dark',sx,sy,sz,.33,.05,.04],
 ['silver',sx,sy,sz,.10,.10,.05]
];
// Steering column is fixed to the dashboard, not part of the spinning rim.
cab.push(['dark',-.62,1.40,cabZ(-2.08),.08,.25,.08]);
// Wheel model is centred at its axle for an independent display spin.
// Build a stepped round tyre from non-overlapping bands. Each layer touches
// the next rather than sharing coplanar intersecting faces during rotation.
const wheel=[];
for (const [y,h,d] of [[-.385,.13,.46],[-.255,.13,.70],[-.125,.13,.84],[0,.12,.90],[.125,.13,.84],[.255,.13,.70],[.385,.13,.46]]) {
 wheel.push(['rubber',0,y,0,.33,h,d]);
}
for (const side of [-1,1]) {
 // Separate stepped hub layers sit entirely outside the tyre sidewall.
 for(const [y,h,d] of [[-.225,.10,.28],[-.125,.10,.42],[-.025,.10,.50],[.075,.10,.46],[.175,.10,.36],[.25,.05,.20]])
  wheel.push(['rim',side*.174,y,0,.018,h,d]);
 wheel.push(['dark',side*.188,0,0,.01,.24,.24]);
 wheel.push(['silver',side*.199,0,0,.012,.14,.14]);
}
// Unit-length cable at the item origin; the Paper rig stretches it along local Y.
const cable=[['silver',0,0,0,.036,1,.036]];
const models={horizon_service_cab:cab,horizon_service_flatbed:compactFlatbed,horizon_service_workshop:atelier,horizon_service_steering:steering,horizon_service_wheel:wheel,horizon_service_ramp:ramp,horizon_service_cable:cable};
for(const [name,pieces] of Object.entries(models)){
 const body={textures,elements:pieces.map((p,i)=>cuboid(p,i,name))};
 writeFileSync(join(modelDir,name+'.json'),JSON.stringify(body,null,2)+'\n');
 writeFileSync(join(itemDir,name+'.json'),JSON.stringify({model:{type:'minecraft:model',model:'vehicle:item/'+name}},null,2)+'\n');
}
// Minimal RGBA PNG, retaining an actual alpha channel for the glass texture.
function crc32(buf){let c=0xffffffff;for(const x of buf){c^=x;for(let i=0;i<8;i++)c=(c>>>1)^((c&1)?0xedb88320:0)}return (c^0xffffffff)>>>0}
function chunk(type,data){const t=Buffer.from(type),len=Buffer.alloc(4),crc=Buffer.alloc(4);len.writeUInt32BE(data.length);crc.writeUInt32BE(crc32(Buffer.concat([t,data])));return Buffer.concat([len,t,data,crc])}
function png(hex,alpha=255){const ihdr=Buffer.alloc(13);ihdr.writeUInt32BE(1,0);ihdr.writeUInt32BE(1,4);ihdr[8]=8;ihdr[9]=6;const rgba=Buffer.from(hex.slice(1),'hex');return Buffer.concat([Buffer.from('89504e470d0a1a0a','hex'),chunk('IHDR',ihdr),chunk('IDAT',deflateSync(Buffer.from([0,...rgba,alpha]))),chunk('IEND',Buffer.alloc(0))])}
for(const [name,color] of Object.entries(palette))writeFileSync(join(textureDir,'horizon_service_'+name.toLowerCase()+'.png'),png(color,name==='glass'?90:255));
writeFileSync(join(out,'conversion-report.json'),JSON.stringify({itemDisplayScale:scale,models:Object.fromEntries(Object.entries(models).map(([name,p])=>[name,p.length])),rotationApproximations:report,notes:['Vanilla item cuboids replace browser torus/cylinder wheels and steering.','Glass alpha must be verified in the target Minecraft client.','Pieces require explicit placement in a future vehicle rig; not installed.']},null,2)+'\n');
console.log('Converted',Object.keys(models).length,'separate model assets to',out);
