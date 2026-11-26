import * as T from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {palette,cab,platforma,atelier,ramp,wheels,platformWheels} from './design.js';
import {loadDacia} from './loading-demo.js';
import {sequence,rampRotation,LOADING,loadingEligibility} from './loading-kinematics.js';
import {buildMinecraftPreview} from './minecraft-preview.js';

const data={
 platforma:{pieces:platforma,title:'Platformă auto',desc:'Cabină închisă fără geamuri, platformă dimensionată pentru Dacia, troliu și rampe articulate.',idea:'Concept pentru recuperarea și transportul unui vehicul defect.',index:'01'},
 atelier:{pieces:atelier,title:'Atelier mobil',desc:'Cabină închisă fără geamuri și caroserie de service cu obloane și suport pe acoperiș.',idea:'Concept pentru intervenții mecanice și echipamente de service.',index:'02'}
};
const holder=document.querySelector('#scene'),status=document.querySelector('#loading');
const scene=new T.Scene(),camera=new T.PerspectiveCamera(37,1,.04,100),renderer=new T.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputColorSpace=T.SRGBColorSpace;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;holder.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.enablePan=false;controls.minDistance=1.6;controls.maxDistance=20;controls.maxPolarAngle=Math.PI*.49;
scene.add(new T.HemisphereLight(0xf9fff4,0x7d8f78,2));const lamp=new T.DirectionalLight(0xffffff,2.2);lamp.position.set(5,9,-7);lamp.castShadow=true;lamp.shadow.mapSize.set(2048,2048);lamp.shadow.camera.left=-13;lamp.shadow.camera.right=13;lamp.shadow.camera.top=13;lamp.shadow.camera.bottom=-13;lamp.shadow.normalBias=.025;scene.add(lamp);
const base=new T.Mesh(new T.CylinderGeometry(4,4,.12,100),new T.MeshStandardMaterial({color:0xeaf0e1,roughness:1}));base.position.y=-.08;base.receiveShadow=true;scene.add(base);
const ground=new T.Mesh(new T.PlaneGeometry(200,200),new T.MeshStandardMaterial({color:0xdce7d2,roughness:1}));ground.rotation.x=-Math.PI/2;ground.position.y=-.026;ground.receiveShadow=true;scene.add(ground);
const line=new T.Mesh(new T.RingGeometry(3.6,3.62,100),new T.MeshBasicMaterial({color:0xc0d0b4,side:T.DoubleSide}));line.rotation.x=-Math.PI/2;line.position.y=-.016;scene.add(line);
const mats=Object.fromEntries(Object.entries(palette).map(([key,color])=>[key,new T.MeshStandardMaterial({color,roughness:key==='glass'?.3:.76,metalness:['steel','silver','rim'].includes(key)?.45:0,transparent:key==='glass',opacity:key==='glass'?.30:1,depthWrite:key!=='glass',side:key==='glass'?T.DoubleSide:T.FrontSide})]));
let selected=null,currentKind='platforma',minecraftMode=false,request=0;
let ramps=[],demo=null,carData=null,loaded=false,cable=null,pending=false;
function box(spec,container){const [kind,x,y,z,w,h,d,rx=0]=spec;const m=new T.Mesh(new T.BoxGeometry(w,h,d),mats[kind]);m.position.set(x,y,z);m.rotation.x=rx;m.castShadow=kind!=='glass';m.receiveShadow=true;container.add(m)}
function cylinder(container,kind,radius,depth,x,y,z,segments=16){const m=new T.Mesh(new T.CylinderGeometry(radius,radius,depth,segments),mats[kind]);m.rotation.z=Math.PI/2;m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;container.add(m);return m}
function wheel(container,x,y,z,scale=1){
 const g=new T.Group();g.position.set(x,y,z);g.scale.setScalar(scale);container.add(g);
 cylinder(g,'rubber',.45,.33,0,0,0,20);
 for(const side of [-1,1]){
  cylinder(g,'dark',.315,.018,side*.171,0,0,20);
  cylinder(g,'rim',.265,.025,side*.186,0,0,20);
  cylinder(g,'steel',.18,.018,side*.205,0,0,20);
  cylinder(g,'silver',.075,.03,side*.22,0,0,16);
  for(let i=0;i<6;i++){const a=i*Math.PI/3;cylinder(g,'black',.022,.018,side*.22,Math.cos(a)*.135,Math.sin(a)*.135,8)}
 }
}
function makeVehicle(kind){
 const group=new T.Group();for(const p of cab)box(p,group);for(const p of data[kind].pieces)box(p,group);
 if(kind==='platforma')for(const side of [-1,1]){const hinge=new T.Group();hinge.name='ramp';hinge.position.set(side*1.05,LOADING.deckTop,LOADING.deckEnd);hinge.rotation.x=rampRotation(0);for(const piece of ramp)box(piece,hinge);group.add(hinge)}
 for(const [x,y,z,scale] of (kind==='platforma'?platformWheels:wheels))wheel(group,x,y,z,scale);
 group.position.y=.005;return group;
}
function center(){camera.position.set(9,5.4,-11);controls.target.set(0,1.0,currentKind==='platforma'?1.3:.18);controls.update()}
function demoView(){camera.position.set(11,8,16);controls.target.set(0,.8,4.0);controls.update()}
function clearDemo(){demo=null;pending=false;loaded=false;if(carData){scene.remove(carData.car);carData.car.traverse(x=>{if(x.geometry)x.geometry.dispose()});carData=null}if(cable){scene.remove(cable);cable.geometry.dispose();cable.material.dispose();cable=null}}
function updateButtons(){const running=!!demo||pending;document.querySelector('#drive-load').disabled=running||loaded;document.querySelector('#winch-load').disabled=running||loaded;document.querySelector('#unload').disabled=running||!loaded;document.querySelector('#trailer-attached').disabled=running||loaded}
function putCable(a,b){
 if(!cable){cable=new T.Mesh(new T.CylinderGeometry(.018,.018,1,8),new T.MeshStandardMaterial({color:0x30383a,metalness:.65,roughness:.5}));scene.add(cable)}
 const delta=new T.Vector3().subVectors(b,a);cable.position.copy(a).add(b).multiplyScalar(.5);cable.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),delta.clone().normalize());cable.scale.y=delta.length();
}
async function startDemo(mode,unload=false){
 if(demo||pending||currentKind!=='platforma'||(unload&&!loaded)||(!unload&&loaded))return;
 const eligibility=loadingEligibility(document.querySelector('#trailer-attached').checked);
 if(!unload&&!eligibility.allowed){document.querySelector('#demo-status').textContent=eligibility.reason+' · regulă simulată, nu verificare în joc.';return}
 if(minecraftMode){minecraftMode=false;document.querySelector('#switch-model').textContent='ARATĂ JSON MINECRAFT';await choose('platforma');if(currentKind!=='platforma'||!loadingEligibility(document.querySelector('#trailer-attached').checked).allowed)return}
 const token=request;pending=true;updateButtons();document.querySelector('#demo-status').textContent='Se încarcă Dacia Poliție din proiect…';
 try{if(!carData){const result=await loadDacia();if(token!==request){result.car.traverse(x=>{if(x.geometry)x.geometry.dispose()});return}carData=result;scene.add(carData.car)}
  pending=false;demo={mode,unload,start:performance.now(),lastZ:null};updateButtons();demoView();
 }catch(error){if(token!==request)return;pending=false;updateButtons();console.error(error);document.querySelector('#demo-status').textContent='Modelul demonstrativ nu a putut fi încărcat.'}
}
function tickDemo(now){
 if(!demo)return;const state=sequence((now-demo.start)/1000,demo.unload);
 ramps.forEach(r=>r.rotation.x=rampRotation(state.ramp));
 carData.car.position.set(0,state.car.y+.005,state.car.z);carData.car.rotation.x=state.car.pitch;
 if(demo.lastZ!==null)for(const w of carData.tires)w.rotation.x+=(state.car.z-demo.lastZ)/.40;
 demo.lastZ=state.car.z;carData.car.updateMatrixWorld(true);
 if(demo.mode==='winch' && state.phase!=='closing' && state.phase!=='done'){
  putCable(new T.Vector3(0,1.06,.30),carData.attach.getWorldPosition(new T.Vector3()));
 }else if(cable){scene.remove(cable);cable.geometry.dispose();cable.material.dispose();cable=null}
 const phaseText={ramps:'Rampele se deschid',moving:demo.unload?'Dacia coboară de pe platformă':demo.mode==='winch'?'Troliul trage Dacia pe platformă':'Dacia urcă pe roți',settling:'Vehiculul se oprește',closing:'Rampele se pliază',done:demo.unload?'Vehicul descărcat':'Vehicul încărcat'};
 document.querySelector('#demo-status').textContent=phaseText[state.phase]+' · simulare 3D, nu comandă în joc.';
 if(state.done){loaded=!demo.unload;demo=null;updateButtons()}
}
async function choose(kind){
 const d=data[kind];if(!d)return;clearDemo();currentKind=kind;const ticket=++request;document.querySelector('#demo-controls').hidden=kind!=='platforma';document.querySelector('#demo-status').textContent='Demonstrație 3D; comenzile nu sunt încă în joc.';updateButtons();
 status.hidden=false;status.textContent='Se pregătește modelul…';
 for(const button of document.querySelectorAll('.choice')){const on=button.dataset.model===kind;button.classList.toggle('active',on);button.setAttribute('aria-pressed',String(on))}
 for(const [key,value] of [['#title',d.title],['#description',d.desc],['#idea',d.idea],['#detail-index',d.index],['#asset-index',d.index+' / 02']])document.querySelector(key).textContent=value;
 try{
  const next=minecraftMode?await buildMinecraftPreview(kind,mats):makeVehicle(kind);
  if(ticket!==request){next.traverse(x=>{if(x.geometry)x.geometry.dispose()});return}
  if(selected){scene.remove(selected);selected.traverse(x=>{if(x.geometry)x.geometry.dispose()})}selected=next;scene.add(selected);ramps=[];selected.traverse(x=>{if(x.name==='ramp')ramps.push(x)});status.hidden=true;center();
 }catch(error){console.error(error);if(ticket===request)status.textContent='Nu se poate încărca modelul JSON.'}
}
document.querySelectorAll('.choice').forEach(button=>button.addEventListener('click',()=>choose(button.dataset.model)));
document.querySelector('#reset').addEventListener('click',center);
document.querySelector('#trailer-attached').addEventListener('change',event=>{document.querySelector('#demo-status').textContent=event.target.checked?'Remorcă sau utilaj cuplat în simulare: încărcarea este blocată.':'Fără remorcă în simulare; încărcarea poate începe.'});
document.querySelector('#drive-load').addEventListener('click',()=>startDemo('drive'));
document.querySelector('#winch-load').addEventListener('click',()=>startDemo('winch'));
document.querySelector('#unload').addEventListener('click',()=>startDemo('drive',true));
document.querySelector('#switch-model').addEventListener('click',event=>{minecraftMode=!minecraftMode;event.currentTarget.textContent=minecraftMode?'ARATĂ CONCEPTUL ORIGINAL':'ARATĂ JSON MINECRAFT';choose(currentKind)});
new ResizeObserver(()=>{const w=holder.clientWidth,h=holder.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}).observe(holder);
function frame(now){requestAnimationFrame(frame);tickDemo(now||performance.now());controls.update();renderer.render(scene,camera)}frame();choose('platforma');
