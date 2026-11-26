import * as T from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {palette,cab,platforma,atelier,wheels} from './design.js';

const data={
 platforma:{pieces:platforma,title:'Platformă auto',desc:'Cabină cu interior, platformă joasă, troliu, ghidaje și rampe de încărcare.',idea:'Concept pentru recuperarea și transportul unui vehicul defect.',index:'01'},
 atelier:{pieces:atelier,title:'Atelier mobil',desc:'Cabină vitrată și caroserie de service cu obloane, compartimente și suport pe acoperiș.',idea:'Concept pentru intervenții mecanice și echipamente de service.',index:'02'}
};
const holder=document.querySelector('#scene'),status=document.querySelector('#loading');
const scene=new T.Scene(),camera=new T.PerspectiveCamera(37,1,.04,100),renderer=new T.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.outputColorSpace=T.SRGBColorSpace;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;holder.appendChild(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.enablePan=false;controls.minDistance=1.6;controls.maxDistance=20;controls.maxPolarAngle=Math.PI*.49;
scene.add(new T.HemisphereLight(0xf9fff4,0x7d8f78,2));const lamp=new T.DirectionalLight(0xffffff,2.2);lamp.position.set(5,9,-7);lamp.castShadow=true;lamp.shadow.mapSize.set(2048,2048);lamp.shadow.camera.left=-7;lamp.shadow.camera.right=7;lamp.shadow.camera.top=7;lamp.shadow.camera.bottom=-7;lamp.shadow.normalBias=.025;scene.add(lamp);
const base=new T.Mesh(new T.CylinderGeometry(4,4,.12,100),new T.MeshStandardMaterial({color:0xeaf0e1,roughness:1}));base.position.y=-.08;base.receiveShadow=true;scene.add(base);
const line=new T.Mesh(new T.RingGeometry(3.6,3.62,100),new T.MeshBasicMaterial({color:0xc0d0b4,side:T.DoubleSide}));line.rotation.x=-Math.PI/2;line.position.y=-.016;scene.add(line);
const mats=Object.fromEntries(Object.entries(palette).map(([key,color])=>[key,new T.MeshStandardMaterial({color,roughness:key==='glass'?.3:.76,metalness:['steel','silver','rim'].includes(key)?.45:0,transparent:key==='glass',opacity:key==='glass'?.30:1,depthWrite:key!=='glass',side:key==='glass'?T.DoubleSide:T.FrontSide})]));
let selected=null;
function box(spec,container){const [kind,x,y,z,w,h,d,rx=0]=spec;const m=new T.Mesh(new T.BoxGeometry(w,h,d),mats[kind]);m.position.set(x,y,z);m.rotation.x=rx;m.castShadow=kind!=='glass';m.receiveShadow=true;container.add(m)}
function cylinder(container,kind,radius,depth,x,y,z,segments=16){const m=new T.Mesh(new T.CylinderGeometry(radius,radius,depth,segments),mats[kind]);m.rotation.z=Math.PI/2;m.position.set(x,y,z);m.castShadow=true;m.receiveShadow=true;container.add(m);return m}
function wheel(container,x,y,z){
 cylinder(container,'rubber',.45,.33,x,y,z,16);
 const side=Math.sign(x);cylinder(container,'rim',.27,.035,x+side*.18,y,z,16);cylinder(container,'steel',.10,.045,x+side*.205,y,z,12);
 // The small bolts are aligned with the visible outer face of the rim.
 for(const angle of [0,Math.PI/2,Math.PI,3*Math.PI/2])cylinder(container,'silver',.028,.03,x+side*.205,y+Math.cos(angle)*.18,z+Math.sin(angle)*.18,8);
}
function makeVehicle(kind){
 const group=new T.Group();for(const p of cab)box(p,group);for(const p of data[kind].pieces)box(p,group);
 for(const [x,y,z] of wheels)wheel(group,x,y,z);
 // Open, visible steering wheel in the cabin; not a flat dark windscreen.
 const steering=new T.Mesh(new T.TorusGeometry(.17,.024,6,16),mats.black);steering.position.set(-.43,1.32,-1.49);steering.rotation.x=-.4;group.add(steering);
 const stem=new T.Mesh(new T.CylinderGeometry(.025,.025,.25,8),mats.black);stem.position.set(-.43,1.21,-1.57);stem.rotation.x=.6;group.add(stem);
 group.position.y=.005;return group;
}
function center(){camera.position.set(7.4,4.7,-8.6);controls.target.set(0,1.05,.18);controls.update()}
function choose(kind){const d=data[kind];if(!d)return;if(selected){scene.remove(selected);selected.traverse(x=>{if(x.geometry)x.geometry.dispose()})}selected=makeVehicle(kind);scene.add(selected);
 for(const button of document.querySelectorAll('.choice')){const on=button.dataset.model===kind;button.classList.toggle('active',on);button.setAttribute('aria-pressed',String(on))}
 for(const [key,value] of [['#title',d.title],['#description',d.desc],['#idea',d.idea],['#detail-index',d.index],['#asset-index',d.index+' / 02']])document.querySelector(key).textContent=value;
 status.hidden=true;center();}
document.querySelectorAll('.choice').forEach(button=>button.addEventListener('click',()=>choose(button.dataset.model)));document.querySelector('#reset').addEventListener('click',center);
new ResizeObserver(()=>{const w=holder.clientWidth,h=holder.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}).observe(holder);
function frame(){requestAnimationFrame(frame);controls.update();renderer.render(scene,camera)}frame();choose('platforma');
