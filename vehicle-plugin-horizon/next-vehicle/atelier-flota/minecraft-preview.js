import * as T from 'three';
import {wheels} from './design.js';
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
  const name=e.faces.up.texture.slice(1), mesh=new T.Mesh(new T.BoxGeometry(...size),materials[name]);
  mesh.castShadow=name!=='glass';mesh.receiveShadow=true;
  if(e.rotation){const pivot=new T.Group(),p=e.rotation.origin.map(n=>n-8);pivot.position.set(...p);mesh.position.set(...center.map((n,i)=>n-p[i]));pivot.rotation[e.rotation.axis]=T.MathUtils.degToRad(e.rotation.angle);pivot.add(mesh);wrapper.add(pivot)}
  else{mesh.position.set(...center);wrapper.add(mesh)}
 }
 return wrapper;
}
export async function buildMinecraftPreview(kind,materials){
 const body=kind==='platforma'?'flatbed':'workshop';
 const [cab,back,steering,wheel]=await Promise.all(['cab',body,'steering','wheel'].map(fetchModel));
 const vehicle=new T.Group();vehicle.add(geometryFromModel(cab,materials),geometryFromModel(back,materials),geometryFromModel(steering,materials));
 for(const [x,y,z] of wheels){const part=geometryFromModel(wheel,materials);part.position.set(x,y,z);vehicle.add(part)}
 vehicle.position.y=.005;return vehicle;
}
