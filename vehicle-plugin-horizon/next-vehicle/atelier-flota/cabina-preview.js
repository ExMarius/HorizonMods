import * as T from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {palette,platforma,ramp,platformWheels} from './design.js';
import {body as cabBody,roof as cabRoof,interior as cabInterior,underbed,frontWheels,steeringPosition,steeringZ,compactCabZ,compactCabPiece} from './cabina-concept-detaliat.js';
import {revisedRearPart,rearShift} from './cabina-geometry.js';
import {loadDacia} from './loading-demo.js';

const holder=document.querySelector('#scene'), status=document.querySelector('#status');
const scene=new T.Scene();scene.background=new T.Color('#d5dfcd');scene.fog=new T.Fog('#d5dfcd',18,42);
const camera=new T.PerspectiveCamera(35,1,.05,100);
const renderer=new T.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputColorSpace=T.SRGBColorSpace;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;holder.appendChild(renderer.domElement);
const orbit=new OrbitControls(camera,renderer.domElement);orbit.enableDamping=true;orbit.minDistance=.65;orbit.maxDistance=30;orbit.maxPolarAngle=Math.PI*.50;
scene.add(new T.HemisphereLight(0xf9fff2,0x6f806b,2.2));
const sun=new T.DirectionalLight(0xffffff,2.1);sun.position.set(-6,10,-8);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-12;sun.shadow.camera.right=12;sun.shadow.camera.top=12;sun.shadow.camera.bottom=-12;sun.shadow.normalBias=.025;scene.add(sun);
const floor=new T.Mesh(new T.PlaneGeometry(100,100),new T.MeshStandardMaterial({color:'#c2d0b9',roughness:1}));floor.rotation.x=-Math.PI/2;floor.position.y=-.025;floor.receiveShadow=true;scene.add(floor);
const disc=new T.Mesh(new T.CylinderGeometry(6.2,6.2,.08,96),new T.MeshStandardMaterial({color:'#e4ebdd',roughness:.95}));disc.position.set(0,-.045,1);disc.receiveShadow=true;scene.add(disc);
const ring=new T.Mesh(new T.RingGeometry(5.5,5.515,96),new T.MeshBasicMaterial({color:'#b9c9b0',side:T.DoubleSide}));ring.rotation.x=-Math.PI/2;ring.position.set(0,.002,1);scene.add(ring);
const mats=Object.fromEntries(Object.entries(palette).map(([name,color])=>[name,new T.MeshStandardMaterial({color,roughness:name==='glass'?.28:.76,metalness:['steel','silver','rim'].includes(name)?.4:0,transparent:name==='glass',opacity:name==='glass'?.19:1,depthWrite:name!=='glass',side:name==='glass'?T.DoubleSide:T.FrontSide})]));
function box(part,parent){const [kind,x,y,z,w,h,d,rx=0]=part;const mesh=new T.Mesh(new T.BoxGeometry(w,h,d),mats[kind]);mesh.position.set(x,y,z);mesh.rotation.x=rx;mesh.castShadow=kind!=='glass';mesh.receiveShadow=true;parent.add(mesh);return mesh}
function cylinder(parent,material,radius,depth,x,y,z){const mesh=new T.Mesh(new T.CylinderGeometry(radius,radius,depth,24),mats[material]);mesh.rotation.z=Math.PI/2;mesh.position.set(x,y,z);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh)}
function wheel(parent,x,y,z,scale){const group=new T.Group();group.position.set(x,y,z);group.scale.setScalar(scale);parent.add(group);cylinder(group,'rubber',.45,.33,0,0,0);for(const side of [-1,1]){cylinder(group,'dark',.315,.018,side*.171,0,0);cylinder(group,'rim',.265,.025,side*.186,0,0);cylinder(group,'steel',.18,.018,side*.205,0,0);cylinder(group,'silver',.075,.03,side*.22,0,0);for(let i=0;i<6;i++){const a=i*Math.PI/3;cylinder(group,'black',.022,.018,side*.22,Math.cos(a)*.135,Math.sin(a)*.135)}}}
const truck=new T.Group();scene.add(truck);
// Concept only: separate groups expose the detailed cabin without changing game assets.
const shell=new T.Group(),roof=new T.Group(),interior=new T.Group();truck.add(shell,roof,interior);
cabBody.forEach(part=>box(compactCabPiece(part,'body'),shell));cabRoof.forEach(part=>box(compactCabPiece(part,'roof'),roof));cabInterior.forEach(part=>box(compactCabPiece(part,'interior'),interior));
// The previous cab's roof lights came from the deck model; the new roof has its own.
platforma.filter(([kind,x,y,z])=>{
 if(kind==='amber'&&y===2.73&&z===-1.30)return false;
 // Replace the old detached toolbox and handle with the mounted assembly.
 if(z===2.08 && ((kind==='chassis'&&x===-1.04)||(kind==='steel'&&x===-1.24)||(kind==='dark'&&x===-1.263)))return false;
 return true;
}).forEach(part=>box(revisedRearPart(part),truck));
underbed.forEach(part=>box(part,truck));
const rearWheels=platformWheels.slice(2).map(([x,y,z,scale])=>[x,y,z-rearShift,scale]);
const compactFrontWheels=frontWheels.map(([x,y,z,scale])=>[x,y,compactCabZ(z),scale]);
for(const [x,y,z,scale] of [...compactFrontWheels,...rearWheels])wheel(truck,x,y,z,scale);
for(const side of [-1,1]){const hinge=new T.Group();hinge.position.set(side*1.05,.86,5.35);hinge.rotation.x=Math.PI/2;ramp.forEach(part=>box(part,hinge));truck.add(hinge)}
// Steering rim and spokes are separate geometry; placement is illustrative, not game animation.
const steering=new T.Group();steering.position.set(steeringPosition[0],steeringPosition[1],steeringZ);steering.rotation.x=-.37;truck.add(steering);
const rim=new T.Mesh(new T.TorusGeometry(.22,.026,8,24),mats.black);steering.add(rim);
box(['dark',0,0,0,.045,.37,.035],steering);box(['dark',0,0,0,.37,.045,.035],steering);
const hub=new T.Mesh(new T.CylinderGeometry(.062,.062,.05,12),mats.silver);hub.rotation.x=Math.PI/2;steering.add(hub);
const column=new T.Mesh(new T.CylinderGeometry(.045,.045,.38,10),mats.dark);column.position.set(-.62,1.40,(steeringZ+compactCabZ(-1.94))/2);column.rotation.x=.78;truck.add(column);
// Blocky seated occupant: a scale cue only, not a captured in-game player model.
const occupant=new T.Group();occupant.position.set(-.62,1.07,-.78);truck.add(occupant);occupant.visible=false;
const coat=new T.MeshStandardMaterial({color:'#52727a',roughness:.9}),skin=new T.MeshStandardMaterial({color:'#c89870',roughness:1}),pants=new T.MeshStandardMaterial({color:'#2c3945',roughness:1});
function personPart(w,h,d,x,y,z,material){const mesh=new T.Mesh(new T.BoxGeometry(w,h,d),material);mesh.position.set(x,y,z);mesh.castShadow=true;occupant.add(mesh)}
personPart(.48,.68,.26,0,.37,0,coat);personPart(.48,.48,.48,0,.95,0,skin);personPart(.19,.50,.21,-.33,.38,-.12,coat);personPart(.19,.50,.21,.33,.38,-.12,coat);personPart(.20,.20,.45,-.13,-.03,-.20,pants);personPart(.20,.20,.45,.13,-.03,-.20,pants);
let cargo=null;const cargoToggle=document.querySelector('#show-car');cargoToggle.addEventListener('change',async()=>{
 if(cargo){cargo.visible=cargoToggle.checked;return}if(!cargoToggle.checked)return;
 cargoToggle.disabled=true;status.textContent='Se încarcă modelul Dacia din proiect…';
 try{const result=await loadDacia();cargo=result.car;cargo.position.set(0,.86,2.64);cargo.rotation.y=Math.PI;scene.add(cargo);cargo.visible=cargoToggle.checked;status.textContent='Dacia este orientativă în previzualizare. Verificarea pozițiilor reale se face în Minecraft.'}
 catch(error){console.error(error);cargoToggle.checked=false;status.textContent='Modelul Dacia nu a putut fi încărcat; poți vedea cabina fără el.'}
 finally{cargoToggle.disabled=false}
});
document.querySelector('#show-player').addEventListener('change',e=>occupant.visible=e.target.checked);
document.querySelector('#show-roof').addEventListener('change',e=>roof.visible=e.target.checked);
document.querySelector('#show-shell').addEventListener('change',e=>shell.visible=e.target.checked);
const views={exterior:{p:[9,5.7,-10.5],t:[0,1.25,1.0]},front:{p:[.05,3.8,-12],t:[0,1.5,-.2]},side:{p:[12,4,1],t:[0,1.25,1]},cab:{p:[-4.0,3.7,1.6],t:[-.3,1.15,-1.10]},inside:{p:[-.62,1.85,-.12],t:[-.40,1.22,-1.8]},detail:{p:[-3.2,2.4,-.1],t:[-.5,1.02,-1.4]}};
function setView(name){const view=views[name];camera.position.set(...view.p);orbit.target.set(...view.t);orbit.update();document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===name))}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>setView(b.dataset.view)));setView('exterior');
new ResizeObserver(()=>{const w=holder.clientWidth,h=holder.clientHeight;if(w&&h){camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}}).observe(holder);
function frame(){requestAnimationFrame(frame);orbit.update();renderer.render(scene,camera)}frame();
