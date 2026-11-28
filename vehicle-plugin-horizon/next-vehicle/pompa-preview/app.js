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

// Original block-built concept: dimensions are in Minecraft blocks.
const soft=(c,roughness=.78)=>new THREE.MeshStandardMaterial({color:c,roughness});
function box(size,mat,pos,parent){const mesh=new THREE.Mesh(new THREE.BoxGeometry(...size),mat);mesh.position.set(...pos);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);return mesh}
const red=soft('#c83132'),redDark=soft('#8f2024'),redLight=soft('#e04b43'),cream=soft('#f1eee0'),black=soft('#20282a'),steel=soft('#9faeb0',.45),green=soft('#60a770'),amber=soft('#edb552');
const pump=new THREE.Group();scene.add(pump);
// Body 0.94 × 1.84 × 0.72, raised on a short dark plinth.
box([.99,.12,.77],black,[0,.12,0],pump);
box([.94,1.53,.72],red,[0,.945,0],pump);
box([.99,.10,.77],redDark,[0,1.76,0],pump);
box([.93,.10,.72],redLight,[0,1.86,0],pump);
// Front white fascia, display surround, readout, buttons and lower access door.
box([.79,.56,.035],cream,[0,1.43,.377],pump);
box([.68,.30,.024],black,[0,1.49,.409],pump);
box([.63,.25,.012],soft('#b7d1c0'),[0,1.49,.427],pump);
box([.54,.23,.025],redDark,[0,.60,.379],pump);
box([.48,.17,.014],red,[0,.60,.398],pump);
box([.63,.025,.026],cream,[0,.86,.382],pump);
for(const [x,m] of [[-.23,green],[0,amber],[.23,green]]){box([.13,.075,.025],black,[x,1.22,.410],pump);box([.10,.046,.012],m,[x,1.22,.43],pump)}
// Integrated nozzle cradle on the right side; hose exits above it.
box([.08,.50,.34],redDark,[.51,1.31,.04],pump);
box([.10,.32,.25],black,[.57,1.29,.04],pump);
box([.12,.05,.29],steel,[.58,1.08,.04],pump);
box([.15,.11,.16],black,[.55,1.61,.02],pump);
// A hand-authored label is preview artwork, not a resource-pack texture.
function label(text,sub){const c=document.createElement('canvas');c.width=512;c.height=192;const q=c.getContext('2d');q.fillStyle='#b7d1c0';q.fillRect(0,0,512,192);q.fillStyle='#20342e';q.font='bold 54px monospace';q.fillText(text,22,78);q.font='bold 25px sans-serif';q.fillText(sub,25,137);const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;const plane=new THREE.Mesh(new THREE.PlaneGeometry(.57,.215),new THREE.MeshBasicMaterial({map:tex}));plane.position.set(0,1.49,.436);pump.add(plane)}
label('00.00 L','HORIZON   /   COMBUSTIBIL');
const nameCanvas=document.createElement('canvas');nameCanvas.width=512;nameCanvas.height=100;const nc=nameCanvas.getContext('2d');nc.fillStyle='#8f2024';nc.fillRect(0,0,512,100);nc.font='bold 48px sans-serif';nc.fillStyle='#fff1de';nc.textAlign='center';nc.fillText('HORIZON',256,65);const nt=new THREE.CanvasTexture(nameCanvas);nt.colorSpace=THREE.SRGBColorSpace;const nameplate=new THREE.Mesh(new THREE.PlaneGeometry(.62,.11),new THREE.MeshBasicMaterial({map:nt}));nameplate.position.set(0,1.72,.375);pump.add(nameplate);
// Pistol: grip, guard, trigger, body and metal spout are independently built.
const nozzlePivot=new THREE.Group();scene.add(nozzlePivot);
box([.13,.25,.13],redDark,[0,-.075,0],nozzlePivot);
box([.15,.095,.27],red,[0,.065,.085],nozzlePivot);
box([.12,.075,.18],black,[0,.075,-.095],nozzlePivot);
box([.08,.075,.25],steel,[0,.085,.30],nozzlePivot);
box([.09,.075,.045],steel,[0,.105,.445],nozzlePivot);
box([.055,.025,.16],steel,[0,-.13,.105],nozzlePivot);
box([.055,.14,.025],steel,[0,-.065,.18],nozzlePivot);
box([.055,.08,.035],black,[0,-.02,.075],nozzlePivot);
const nozzleHosePoint=new THREE.Vector3(0,-.205,-.035);
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
const hose=new THREE.Group();scene.add(hose);const hoseMat=soft('#202426'), hoseGeometry=new THREE.CylinderGeometry(.034,.034,1,10);const hoseParts=[];for(let i=0;i<16;i++){let m=new THREE.Mesh(hoseGeometry,hoseMat);m.castShadow=true;hose.add(m);hoseParts.push(m)}
// Endpoints are explicit: the fixed outlet and the nozzle connector follow
// their own transforms. Sag is an illustrative curve, not a physics solver.
const start=new THREE.Vector3(.625,1.61,.02), rest=new THREE.Vector3(.65,1.31,.06);
let held=true, first=false;const distance=document.querySelector('#distance'),angle=document.querySelector('#angle');
function hosePoint(a,b,t,sag){const point=a.clone().lerp(b,t);point.y=Math.max(.09,point.y-4*sag*t*(1-t));return point}
function update(){
 const d=+distance.value, a=THREE.MathUtils.degToRad(+angle.value);document.querySelector('#distance-value').textContent=d.toFixed(1).replace('.',',')+' blocuri';document.querySelector('#angle-value').textContent=angle.value+'°';
 player.position.set(Math.cos(a)*d,0,Math.sin(a)*d);const dir=new THREE.Vector3(-player.position.x,0,-player.position.z).normalize();player.rotation.y=Math.atan2(dir.x,dir.z);player.updateMatrixWorld(true);const hand=player.localToWorld(localHand.clone());
 nozzlePivot.position.copy(held?hand:rest);nozzlePivot.rotation.y=held?player.rotation.y:0;nozzlePivot.updateMatrixWorld(true);
 const end=nozzlePivot.localToWorld(nozzleHosePoint.clone());
 const sag=held?Math.max(.12,.7-start.distanceTo(end)*.10):.24;
 let prev=start;for(let i=0;i<16;i++){const p=hosePoint(start,end,(i+1)/16,sag),delta=p.clone().sub(prev),m=hoseParts[i];m.position.copy(prev).add(p).multiplyScalar(.5);m.scale.set(1,delta.length(),1);if(delta.lengthSq()>1e-9)m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),delta.normalize());m.visible=!(first&&held&&i>=14);prev=p;}
 heldArm.visible=held;handMesh.visible=held;document.querySelector('#mode').textContent=held?'PISTOL ÎN MÂNĂ':'PISTOL LA POMPĂ';
 document.querySelector('#held').classList.toggle('active',held);document.querySelector('#docked').classList.toggle('active',!held);
 document.querySelector('#orbit').classList.toggle('active',!first);document.querySelector('#first').classList.toggle('active',first);
 if(first){camera.position.copy(player.localToWorld(new THREE.Vector3(0,1.63,.05)));controls.target.copy(camera.position).add(dir);controls.enabled=false;camera.lookAt(controls.target);player.visible=false}else{controls.enabled=true;player.visible=true;}
}
function reset(){first=false;camera.position.set(5.8,3.5,6.2);controls.target.set(.45,1,0);controls.update();update()}
distance.addEventListener('input',update);angle.addEventListener('input',update);document.querySelector('#held').onclick=()=>{held=true;update()};document.querySelector('#docked').onclick=()=>{held=false;update()};document.querySelector('#orbit').onclick=reset;document.querySelector('#first').onclick=()=>{first=true;update()};document.querySelector('#reset').onclick=reset;
new ResizeObserver(()=>{const w=view.clientWidth,h=view.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}).observe(view);
loading.hidden=true;reset();
function frame(){requestAnimationFrame(frame);if(!first)controls.update();renderer.render(scene,camera)}frame();
