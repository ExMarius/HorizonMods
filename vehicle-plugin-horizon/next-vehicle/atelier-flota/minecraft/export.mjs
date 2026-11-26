/** Translate the hand-authored blocks to separate vanilla item models.
 * Geometry is not generated from a shape algorithm: source placements are in
 * ../design.js. Vanilla rotations are limited; see the conversion report. */
import {mkdirSync,writeFileSync} from 'node:fs';
import {deflateSync} from 'node:zlib';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {cab,platforma,atelier,palette} from '../design.js';
const here=dirname(fileURLToPath(import.meta.url));
const out=resolve(process.argv[2]||join(here,'assets'));
const scale=4, unit=16/scale;
const modelDir=join(out,'models/item'),itemDir=join(out,'items'),textureDir=join(out,'textures/item');
for(const d of [modelDir,itemDir,textureDir])mkdirSync(d,{recursive:true});
const names=Object.keys(palette),textures=Object.fromEntries(names.map(n=>[n,`vehicle:item/horizon_service_${n.toLowerCase()}`]));
const report=[];
function vec(x,y,z){return [8+x*unit,8+y*unit,8+z*unit].map(n=>+n.toFixed(5))}
function cuboid(p,index,part){
 const [mat,x,y,z,w,h,d,rx=0]=p;
 if(!textures[mat]||![x,y,z,w,h,d,rx].every(Number.isFinite)||w<=0||h<=0||d<=0)throw Error('Invalid authored part '+part+' '+index);
 const e={name:`${part}_${index}`,from:vec(x-w/2,y-h/2,z-d/2),to:vec(x+w/2,y+h/2,z+d/2),
 faces:Object.fromEntries(['north','south','east','west','up','down'].map(face=>[face,{uv:[0,0,16,16],texture:'#'+mat}]))};
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
const steering=[
 ['black',-.43,1.49,-1.49,.34,.045,.045],['black',-.43,1.15,-1.49,.34,.045,.045],
 ['black',-.59,1.32,-1.49,.045,.34,.045],['black',-.27,1.32,-1.49,.045,.34,.045],
 ['black',-.43,1.20,-1.57,.05,.25,.05]
];
// Wheel model is centred at its axle for an independent display spin.
const wheel=[
 ['rubber',0,0,0,.33,.90,.34],['rubber',0,0,0,.33,.34,.90],
 ['rubber',0,0,0,.33,.90,.34,Math.PI/4],['rubber',0,0,0,.33,.90,.34,-Math.PI/4],
 ['rim',-.18,0,0,.04,.52,.52],['rim',.18,0,0,.04,.52,.52],
 ['steel',-.205,0,0,.05,.18,.18],['steel',.205,0,0,.05,.18,.18]
];
const models={horizon_service_cab:cab,horizon_service_flatbed:platforma,horizon_service_workshop:atelier,horizon_service_steering:steering,horizon_service_wheel:wheel};
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
