import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const view=document.querySelector('#scene'), loading=document.querySelector('#loading');
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;view.appendChild(renderer.domElement);
const scene=new THREE.Scene();scene.background=new THREE.Color('#e9eee5');scene.fog=new THREE.Fog('#e9eee5',15,32);
const camera=new THREE.PerspectiveCamera(38,1,.02,60), controls=new OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.target.set(.1,.95,0);controls.minDistance=1.5;controls.maxDistance=15;controls.maxPolarAngle=Math.PI*.495;
scene.add(new THREE.HemisphereLight(0xf9fff3,0x809080,2.0));
const sun=new THREE.DirectionalLight(0xffffff,2.2);sun.position.set(3.8,8,5);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-8,right:8,top:8,bottom:-8});sun.shadow.normalBias=.025;scene.add(sun);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(200,200),new THREE.MeshStandardMaterial({color:'#dce5d6',roughness:1}));ground.rotation.x=-Math.PI/2;ground.position.y=-.055;ground.receiveShadow=true;scene.add(ground);
const island=new THREE.Mesh(new THREE.BoxGeometry(2.55,.12,1.8),new THREE.MeshStandardMaterial({color:'#f4f5ed',roughness:.9}));island.position.y=.005;island.receiveShadow=true;scene.add(island);
const border=new THREE.Mesh(new THREE.BoxGeometry(2.56,.025,1.81),new THREE.MeshStandardMaterial({color:'#a2bb83'}));border.position.y=-.058;scene.add(border);
const grid=new THREE.GridHelper(24,48,0x9bad9d,0xc4d1c2);grid.position.y=-.049;grid.material.transparent=true;grid.material.opacity=.24;scene.add(grid);

const invisible=new THREE.MeshBasicMaterial({visible:false});const loader=new THREE.TextureLoader();const mats={};
function material(name){if(!name)return invisible;let key=name.split('/').pop();if(!['gas_pump','nozzle'].includes(key))return invisible;if(!mats[key]){const map=loader.load('/textures/'+key+'.png');map.colorSpace=THREE.SRGBColorSpace;map.magFilter=THREE.NearestFilter;map.minFilter=THREE.NearestFilter;mats[key]=new THREE.MeshStandardMaterial({map,roughness:.78,transparent:true,alphaTest:.1,side:THREE.DoubleSide})}return mats[key]}
function model(data,yOffset=0){
 const group=new THREE.Group(),faces=['east','west','up','down','south','north'];
 for(const e of data.elements){
  const size=e.to.map((v,i)=>v-e.from[i]),center=e.to.map((v,i)=>(v+e.from[i])/2-(i===1?yOffset:8));
  const geo=new THREE.BoxGeometry(...size),uv=geo.attributes.uv;
  const materials=faces.map((face,i)=>{const f=e.faces[face];if(!f)return invisible;const [u0,v0,u1,v1]=f.uv||[0,0,16,16];const pts=[[u0,16-v0],[u1,16-v0],[u0,16-v1],[u1,16-v1]];const turns=((f.rotation||0)/90)%4;for(let k=0;k<4;k++){let j=k;for(let n=0;n<turns;n++)j=[1,3,0,2][j];uv.setXY(i*4+k,pts[j][0]/16,pts[j][1]/16)}return material(data.textures[f.texture.slice(1)])});
  uv.needsUpdate=true;const cube=new THREE.Mesh(geo,materials);cube.castShadow=true;cube.receiveShadow=true;
  if(e.rotation&&e.rotation.angle){const p=e.rotation.origin.map((v,i)=>v-(i===1?yOffset:8)),pivot=new THREE.Group();pivot.position.set(...p);cube.position.set(...center.map((v,i)=>v-p[i]));pivot.rotation[e.rotation.axis]=THREE.MathUtils.degToRad(e.rotation.angle);pivot.add(cube);group.add(pivot)}else{cube.position.set(...center);group.add(cube)}
 }group.scale.setScalar(1/16);return group;
}
async function getModel(name){const r=await fetch('/models/'+name+'.json');if(!r.ok)throw Error('Model lipsă: '+name);return r.json()}
const soft=(c)=>new THREE.MeshStandardMaterial({color:c,roughness:.85});
function box(size,mat,pos,parent){const mesh=new THREE.Mesh(new THREE.BoxGeometry(...size),mat);mesh.position.set(...pos);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);return mesh}
// Schematic Minecraft-like figure; not the in-game skin or proof of an actual arm pose.
const player=new THREE.Group(),skin=soft('#dba577'),shirt=soft('#4e8b81'),pants=soft('#38445a'),boots=soft('#303541'),hair=soft('#49382c');scene.add(player);
box([.5,.68,.26],shirt,[0,1.04,0],player);box([.5,.5,.5],skin,[0,1.63,0],player);box([.51,.105,.51],hair,[0,1.835,0],player);
box([.07,.055,.012],soft('#2d302f'),[-.13,1.66,.256],player);box([.07,.055,.012],soft('#2d302f'),[.13,1.66,.256],player);
for(const x of [-.13,.13]){box([.24,.59,.25],pants,[x,.35,0],player);box([.24,.1,.28],boots,[x,.065,.015],player)}
box([.22,.52,.22],shirt,[.36,1.1,0],player);box([.22,.18,.22],skin,[.36,.75,0],player);
const heldArm=new THREE.Group();player.add(heldArm);const armMesh=box([.21,1,.21],shirt,[0,0,0],heldArm);const handMesh=box([.20,.18,.20],skin,[-.30,1.22,.35],player);
const localHand=new THREE.Vector3(-.30,1.22,.35),shoulder=new THREE.Vector3(-.36,1.33,0);
function connectArm(){const v=localHand.clone().sub(shoulder), mid=shoulder.clone().add(localHand).multiplyScalar(.5);heldArm.position.copy(mid);heldArm.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),v.clone().normalize());armMesh.scale.y=v.length();}
connectArm();
const hose=new THREE.Group();scene.add(hose);const hoseMat=soft('#202b28'), hoseGeometry=new THREE.CylinderGeometry(.03125,.03125,1,10);const hoseParts=[];for(let i=0;i<8;i++){let m=new THREE.Mesh(hoseGeometry,hoseMat);m.castShadow=true;hose.add(m);hoseParts.push(m)}
const nozzlePivot=new THREE.Group();scene.add(nozzlePivot);const start=new THREE.Vector3(-.575,1.64,.1125), rest=new THREE.Vector3(-.5525,1.5,-.18);
let held=true, first=false;const distance=document.querySelector('#distance'),angle=document.querySelector('#angle');let nozzleModel;
function hermite(a,t,b,u,s){const s2=s*s,s3=s2*s;return a.clone().multiplyScalar(2*s3-3*s2+1).addScaledVector(b,-2*s3+3*s2).addScaledVector(t,s3-2*s2+s).addScaledVector(u,s3-s2)}
function update(){
 const d=+distance.value, a=THREE.MathUtils.degToRad(+angle.value);document.querySelector('#distance-value').textContent=d.toFixed(1).replace('.',',')+' blocuri';document.querySelector('#angle-value').textContent=angle.value+'°';
 player.position.set(Math.cos(a)*d,0,Math.sin(a)*d);const dir=new THREE.Vector3(-player.position.x,0,-player.position.z).normalize();player.rotation.y=Math.atan2(dir.x,dir.z);player.updateMatrixWorld(true);const hand=player.localToWorld(localHand.clone());
 nozzlePivot.position.copy(held?hand:rest);nozzlePivot.rotation.y=held?player.rotation.y:Math.PI;
 const end=(held?hand.clone().addScaledVector(dir,.22):rest.clone()),tan=held?dir.clone().multiplyScalar(3):new THREE.Vector3(0,3,0), startTan=new THREE.Vector3(0,-5,0);
 let prev=start;for(let i=0;i<8;i++){const p=hermite(start,startTan,end,tan,(i+1)/8),delta=p.clone().sub(prev),m=hoseParts[i];m.position.copy(prev).add(p).multiplyScalar(.5);m.scale.set(1,delta.length(),1);if(delta.lengthSq()>1e-9)m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),delta.normalize());m.visible=!(first&&held&&i>=6);prev=p;}
 heldArm.visible=held;handMesh.visible=held;document.querySelector('#mode').textContent=held?'PISTOL ÎN MÂNĂ':'PISTOL LA POMPĂ';
 document.querySelector('#held').classList.toggle('active',held);document.querySelector('#docked').classList.toggle('active',!held);
 document.querySelector('#orbit').classList.toggle('active',!first);document.querySelector('#first').classList.toggle('active',first);
 if(first){camera.position.copy(player.localToWorld(new THREE.Vector3(0,1.63,.05)));controls.target.copy(camera.position).add(dir);controls.enabled=false;camera.lookAt(controls.target);player.visible=false}else{controls.enabled=true;player.visible=true;}
}
function reset(){first=false;camera.position.set(5.8,3.5,6.2);controls.target.set(.45,1,0);controls.update();update()}
distance.addEventListener('input',update);angle.addEventListener('input',update);document.querySelector('#held').onclick=()=>{held=true;update()};document.querySelector('#docked').onclick=()=>{held=false;update()};document.querySelector('#orbit').onclick=reset;document.querySelector('#first').onclick=()=>{first=true;update()};document.querySelector('#reset').onclick=reset;
new ResizeObserver(()=>{const w=view.clientWidth,h=view.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}).observe(view);
Promise.all([getModel('gas_pump_bottom'),getModel('gas_pump_top'),getModel('nozzle')]).then(([bottom,top,nozzle])=>{scene.add(model(bottom));const t=model(top);t.position.y=1;scene.add(t);nozzleModel=model(nozzle,8);nozzlePivot.add(nozzleModel);loading.hidden=true;reset()}).catch(err=>{console.error(err);loading.textContent='Nu s-au putut încărca modelele. Reîncarcă pagina.'});
function frame(){requestAnimationFrame(frame);if(!first)controls.update();renderer.render(scene,camera)}frame();
