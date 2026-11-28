import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// These are existing project assets, rendered as authored cuboids and textures.
// The wheel placement and browser display are previews, not a Minecraft renderer.
const entries={
 ambulance:{title:'Ambulanță românească',description:'Caroserie medicală cu geamuri, cabină, targă și compartiment pentru pacient.',idea:'Model existent în proiect · adaptarea la server nu este făcută.',index:'01'},
 smurd:{title:'Ambulanță SMURD',description:'Variantă roșie de intervenție, cu interior medical, geamuri și inscripții SMURD.',idea:'Model existent în proiect · adaptarea la server nu este făcută.',index:'02'},
 fire_truck:{title:'Autospecială de pompieri',description:'Autospecială roșie cu cabină vitrată, girofar, compartimente și marcaje pentru intervenții.',idea:'Model existent în proiect · adaptarea la server nu este făcută.',index:'03'}
};
const holder=document.querySelector('#scene'),status=document.querySelector('#loading');
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;holder.appendChild(renderer.domElement);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(38,1,.05,100),controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.enablePan=false;controls.minDistance=2;controls.maxDistance=15;controls.maxPolarAngle=Math.PI*.49;
scene.add(new THREE.HemisphereLight(0xf6fff2,0x829278,2));const sun=new THREE.DirectionalLight(0xffffff,2);sun.position.set(5,10,7);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-6;sun.shadow.camera.right=6;sun.shadow.camera.top=6;sun.shadow.camera.bottom=-6;sun.shadow.normalBias=.03;scene.add(sun);
const platform=new THREE.Mesh(new THREE.CylinderGeometry(2.65,2.65,.10,96),new THREE.MeshStandardMaterial({color:0xeaf0e1,roughness:1}));platform.position.y=-.055;platform.receiveShadow=true;scene.add(platform);
const ring=new THREE.Mesh(new THREE.RingGeometry(2.31,2.32,100),new THREE.MeshBasicMaterial({color:0xc2d3b5,side:THREE.DoubleSide}));ring.rotation.x=-Math.PI/2;ring.position.y=.002;scene.add(ring);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(200,200),new THREE.ShadowMaterial({opacity:.16}));floor.rotation.x=-Math.PI/2;floor.position.y=-.11;floor.receiveShadow=true;scene.add(floor);
const textures=new THREE.TextureLoader(),materials=new Map(),modelCache=new Map();let current=null,request=0;
const invisible=new THREE.MeshBasicMaterial({visible:false});
function material(ref){
 if(!ref||!ref.startsWith('gokart:block/'))return invisible;
 if(!materials.has(ref)){
  const name=ref.split('/').pop(),map=textures.load('/textures/'+name+'.png');map.colorSpace=THREE.SRGBColorSpace;map.magFilter=THREE.NearestFilter;map.minFilter=THREE.NearestFilter;
  materials.set(ref,new THREE.MeshStandardMaterial({map,roughness:.75,transparent:true,alphaTest:.1,side:THREE.DoubleSide}));
 }
 return materials.get(ref);
}
async function model(name){if(!modelCache.has(name)){const r=await fetch('/models/'+name+'.json');if(!r.ok)throw Error(name+' nu a putut fi încărcat');modelCache.set(name,await r.json())}return modelCache.get(name)}
function addModel(data,offsetY=0){
 const group=new THREE.Group(),faces=['east','west','up','down','south','north'];
 for(const e of data.elements){
  const size=e.to.map((v,i)=>v-e.from[i]),center=e.to.map((v,i)=>(v+e.from[i])/2-(i===1?offsetY:8));
  const geometry=new THREE.BoxGeometry(...size),uv=geometry.attributes.uv;
  const faceMaterials=faces.map((face,i)=>{
   const definition=e.faces[face]; if(!definition)return invisible;
   const [u0,v0,u1,v1]=definition.uv||[0,0,16,16];
   // Face UVs have top-left origin in Minecraft; Three.js uses bottom-left.
   const points=[[u0,16-v0],[u1,16-v0],[u0,16-v1],[u1,16-v1]];
   const turns=((definition.rotation||0)/90)%4;
   for(let k=0;k<4;k++){let j=k;for(let n=0;n<turns;n++)j=[1,3,0,2][j];uv.setXY(i*4+k,points[j][0]/16,points[j][1]/16)}
   const key=(definition.texture||'').slice(1);return material(data.textures[key]);
  });
  uv.needsUpdate=true;const mesh=new THREE.Mesh(geometry,faceMaterials);mesh.castShadow=true;mesh.receiveShadow=true;
  if(e.rotation){
   const p=e.rotation.origin.map((v,i)=>v-(i===1?offsetY:8)),pivot=new THREE.Group();pivot.position.set(...p);mesh.position.set(...center.map((v,i)=>v-p[i]));pivot.rotation[e.rotation.axis]=THREE.MathUtils.degToRad(e.rotation.angle);pivot.add(mesh);group.add(pivot);
  }else{mesh.position.set(...center);group.add(mesh)}
 }
 group.scale.setScalar(1/16);return group;
}
function disposeGeometries(object){object.traverse(o=>{if(o.isMesh)o.geometry.dispose()})}
function centerCamera(){camera.position.set(5.5,3.25,6);controls.target.set(0,.8,0);controls.update()}
async function select(key){
 const e=entries[key];if(!e)return;const serial=++request;
 document.querySelectorAll('.choice').forEach(b=>{const active=b.dataset.model===key;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});
 for(const [selector,value] of [['#title',e.title],['#description',e.description],['#idea',e.idea],['#detail-index',e.index],['#asset-index',e.index+' / 03']])document.querySelector(selector).textContent=value;
 status.hidden=false;status.textContent='Se încarcă modelul 3D…';
 try{
  const [body,wheel]=await Promise.all([model(key+'_body'),model('wheel_standard')]);if(serial!==request)return;
  const vehicle=new THREE.Group();vehicle.add(addModel(body));
  // Approximate wheel centres from the existing authored wheel arches; not an in-game rig.
  for(const x of [-11.1,11.1])for(const z of [-13.8,11]){const w=addModel(wheel,8);w.position.set(x/16,4/16,z/16);vehicle.add(w)}
  const box=new THREE.Box3().setFromObject(vehicle),size=box.getSize(new THREE.Vector3()),scale=3.5/Math.max(size.x,size.z);vehicle.scale.setScalar(scale);
  const scaled=new THREE.Box3().setFromObject(vehicle),center=scaled.getCenter(new THREE.Vector3());vehicle.position.set(-center.x,-scaled.min.y,-center.z);
  if(current){scene.remove(current);disposeGeometries(current)}current=vehicle;scene.add(current);centerCamera();status.hidden=true;
 }catch(error){console.error(error);if(serial===request)status.textContent='Modelul nu s-a putut încărca. Reîncarcă pagina.'}
}
document.querySelectorAll('.choice').forEach(b=>b.addEventListener('click',()=>select(b.dataset.model)));document.querySelector('#reset').addEventListener('click',centerCamera);
new ResizeObserver(()=>{const w=holder.clientWidth,h=holder.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}).observe(holder);
function frame(){requestAnimationFrame(frame);controls.update();renderer.render(scene,camera)}frame();select('ambulance');
