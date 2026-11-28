import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
const faces=['east','west','up','down','south','north'],loader=new THREE.TextureLoader(),materials=new Map();
function material(name){if(!materials.has(name)){const map=loader.load('/utb-textures/'+name+'.png');map.colorSpace=THREE.SRGBColorSpace;map.magFilter=THREE.NearestFilter;map.minFilter=THREE.NearestFilter;materials.set(name,new THREE.MeshStandardMaterial({map,side:THREE.DoubleSide,alphaTest:.1,roughness:.8}))}return materials.get(name)}
async function model(name){const r=await fetch('/vehicle-model/'+name+'.json');if(!r.ok)throw Error('Modelul '+name+' nu este disponibil');return r.json()}
// Render exactly the authored Minecraft cuboids and UVs, while batching their
// triangles by texture solely in the browser. No source item JSON is changed.
function build(data,scale){const buckets=new Map();
 for(const e of data.elements){const size=e.to.map((n,i)=>n-e.from[i]),center=e.to.map((n,i)=>(n+e.from[i])/2-8);const geometry=new THREE.BoxGeometry(...size),uv=geometry.attributes.uv;
  const names=faces.map((face,i)=>{const f=e.faces[face];if(!f)return null;const t=data.textures[(f.texture||'').replace(/^#/,'')];if(!t||!t.startsWith('vehicle:item/utb_'))throw Error('Textură vehicul neacceptată: '+t);const [u0,v0,u1,v1]=f.uv||[0,0,16,16],points=[[u0,16-v0],[u1,16-v0],[u0,16-v1],[u1,16-v1]],turns=((f.rotation||0)/90)%4;for(let k=0;k<4;k++){let j=k;for(let n=0;n<turns;n++)j=[1,3,0,2][j];uv.setXY(i*4+k,points[j][0]/16,points[j][1]/16)}return t.slice('vehicle:item/utb_'.length)});
  geometry.translate(...center);if(e.rotation){const pivot=e.rotation.origin.map(x=>x-8),mat=new THREE.Matrix4(),before=new THREE.Matrix4().makeTranslation(...pivot),after=new THREE.Matrix4().makeTranslation(...pivot.map(v=>-v)),angle=THREE.MathUtils.degToRad(e.rotation.angle);if(e.rotation.axis==='x')mat.makeRotationX(angle);else if(e.rotation.axis==='y')mat.makeRotationY(angle);else mat.makeRotationZ(angle);geometry.applyMatrix4(before.multiply(mat).multiply(after))}
  const flat=geometry.toNonIndexed();geometry.dispose();for(let i=0;i<6;i++){if(!names[i])continue;const start=i*6*3,uvStart=i*6*2,part=new THREE.BufferGeometry();part.setAttribute('position',new THREE.BufferAttribute(flat.attributes.position.array.slice(start,start+18),3));part.setAttribute('normal',new THREE.BufferAttribute(flat.attributes.normal.array.slice(start,start+18),3));part.setAttribute('uv',new THREE.BufferAttribute(flat.attributes.uv.array.slice(uvStart,uvStart+12),2));if(!buckets.has(names[i]))buckets.set(names[i],[]);buckets.get(names[i]).push(part)}flat.dispose();
 }
 const root=new THREE.Group();for(const [name,parts] of buckets){const geom=mergeGeometries(parts);for(const part of parts)part.dispose();root.add(new THREE.Mesh(geom,material(name)))}root.scale.setScalar(scale/16);return root;
}
export async function createServerVehiclePreview(){const [tractorBody,frontWheel,rearWheel,trailerBody]=await Promise.all(['utb_650_body','utb_650_wheel_front','utb_650_wheel_rear','tractor_trailer_body'].map(model));const rig=new THREE.Group(),oriented=new THREE.Group();oriented.rotation.y=Math.PI;rig.add(oriented);
 const body=build(trailerBody,2);body.position.y=.5;oriented.add(body);const wheels=[];
 function wheel(parent,data,x,y,z,side){const pivot=new THREE.Group();pivot.position.set(x,y,z);parent.add(pivot);const m=build(data,1);if(side>0)m.rotation.y=Math.PI;pivot.add(m);wheels.push(pivot)}
 for(const side of [-1,1])wheel(oriented,frontWheel,side*1,.43125,0,side);
 const tractor=new THREE.Group();tractor.position.z=3.93;oriented.add(tractor);const bodyTractor=build(tractorBody,2);bodyTractor.position.y=.5;tractor.add(bodyTractor);
 for(const side of [-1,1]){wheel(tractor,frontWheel,side*11.25/16,6.9/16,13.68/16,side);wheel(tractor,rearWheel,side*14.65/16,12.4/16,-25.2/16,side)}
 const grain=new THREE.Mesh(new THREE.BoxGeometry(1.6,.03,2.05),new THREE.MeshStandardMaterial({color:'#d2b36a'}));grain.position.set(0,.59,0);grain.visible=false;oriented.add(grain);rig.userData.grain=grain;rig.userData.wheels=wheels;rig.userData.bed={halfX:.82,halfZ:1.04,floor:.575,top:1.25};return rig;
}
