import * as T from 'three';
import {wheels,platformWheels} from './design.js';
import {rampRotation,LOADING} from './loading-kinematics.js';
const cache=new Map();
async function fetchModel(name){
 if(!cache.has(name)){
  const response=await fetch('/minecraft/models/item/horizon_service_'+name+'.json');
  if(!response.ok)throw new Error('Modelul '+name+' nu poate fi citit');
  cache.set(name,await response.json());
 }
 return cache.get(name);
}
function geometryFromModel(data,materials){
 const wrapper=new T.Group();wrapper.scale.setScalar(4/16);
 for(const e of data.elements){
  const size=e.to.map((v,i)=>v-e.from[i]),center=e.to.map((v,i)=>(v+e.from[i])/2-8);
  const name=e.faces.up.texture.slice(1), key=Object.keys(materials).find(n=>n.toLowerCase()===name);
  if(!key)throw new Error('Unknown material '+name);
  const mesh=new T.Mesh(new T.BoxGeometry(...size),materials[key]);
  mesh.castShadow=name!=='glass';mesh.receiveShadow=true;
  if(e.rotation){const pivot=new T.Group(),p=e.rotation.origin.map(n=>n-8);pivot.position.set(...p);mesh.position.set(...center.map((n,i)=>n-p[i]));pivot.rotation[e.rotation.axis]=T.MathUtils.degToRad(e.rotation.angle);pivot.add(mesh);wrapper.add(pivot)}
  else{mesh.position.set(...center);wrapper.add(mesh)}
 }
 return wrapper;
}
export async function buildMinecraftPreview(kind,materials){
 const body=kind==='platforma'?'flatbed':'workshop';
 const [cab,back,steering,wheel,ramp]=await Promise.all(['cab',body,'steering','wheel','ramp'].map(fetchModel));
 const vehicle=new T.Group();vehicle.add(geometryFromModel(cab,materials),geometryFromModel(back,materials),geometryFromModel(steering,materials));
 for(const [x,y,z,scale] of (kind==='platforma'?platformWheels:wheels)){const part=geometryFromModel(wheel,materials);part.position.set(x,y,z);part.scale.multiplyScalar(scale);vehicle.add(part)}
 if(kind==='platforma')for(const side of [-1,1]){const hinge=new T.Group();hinge.name='ramp';hinge.position.set(side*1.05,LOADING.deckTop,LOADING.deckEnd);hinge.rotation.x=rampRotation(0);hinge.add(geometryFromModel(ramp,materials));vehicle.add(hinge)}
 vehicle.position.y=.005;return vehicle;
}
