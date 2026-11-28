import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {TransformControls} from 'three/addons/controls/TransformControls.js';
const scene=new THREE.Scene();scene.background=new THREE.Color('#e9eee5');
const host=document.querySelector('#scene'),renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;host.appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(38,1,.01,40),controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=.6;controls.maxDistance=10;controls.maxPolarAngle=Math.PI*.495;
scene.add(new THREE.HemisphereLight(0xffffff,0x88978a,2));const sun=new THREE.DirectionalLight(0xffffff,2);sun.position.set(-3,6,5);scene.add(sun);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(40,40),new THREE.MeshStandardMaterial({color:'#dce5d6'}));floor.rotation.x=-Math.PI/2;floor.position.y=-.01;scene.add(floor);
const noFace=new THREE.MeshBasicMaterial({visible:false}),sides=['east','west','up','down','south','north'];
function texture(path){const t=new THREE.TextureLoader().load(path);t.colorSpace=THREE.SRGBColorSpace;t.magFilter=THREE.NearestFilter;t.minFilter=THREE.NearestFilter;return t}
const pumpTexture=texture('/minecraft/pump.png'),nozzleTexture=texture('/assets/nozzle-red.png');
function makeModel(data,tex){
 const group=new THREE.Group(),mat=new THREE.MeshStandardMaterial({map:tex,side:THREE.DoubleSide,transparent:true,alphaTest:.1,roughness:.8});
 for(const e of data.elements){const dims=e.to.map((v,i)=>v-e.from[i]),center=e.to.map((v,i)=>(v+e.from[i])/2-8),g=new THREE.BoxGeometry(...dims),uv=g.attributes.uv;
  const mats=sides.map((side,i)=>{let f=e.faces[side];if(!f)return noFace;const [a,b,c,d]=f.uv||[0,0,16,16],pts=[[a,16-b],[c,16-b],[a,16-d],[c,16-d]],turns=((f.rotation||0)/90)%4;for(let k=0;k<4;k++){let j=k;for(let n=0;n<turns;n++)j=[1,3,0,2][j];uv.setXY(i*4+k,pts[j][0]/16,pts[j][1]/16)}return mat});
  const mesh=new THREE.Mesh(g,mats);if(e.rotation&&e.rotation.angle){const pivot=new THREE.Group(),origin=e.rotation.origin.map(x=>x-8);pivot.position.set(...origin);mesh.position.set(...center.map((x,i)=>x-origin[i]));pivot.rotation[e.rotation.axis]=THREE.MathUtils.degToRad(e.rotation.angle);pivot.add(mesh);group.add(pivot)}else{mesh.position.set(...center);group.add(mesh)}
 }group.scale.setScalar(1/16);return group;
}
const hose=new THREE.Group();scene.add(hose);const hoseMaterial=new THREE.MeshStandardMaterial({color:'#242625',roughness:1});const geometry=new THREE.BoxGeometry(.0625,.0625,1);
function renderHose(end){while(hose.children.length)hose.remove(hose.children[0]);const start=new THREE.Vector3(-.575,1.64,.1125),m0=new THREE.Vector3(0,-5,0),m1=new THREE.Vector3(0,3,0);function point(t){const q=t*t,r=q*t;return start.clone().multiplyScalar(2*r-3*q+1).addScaledVector(end,-2*r+3*q).addScaledVector(m0,r-2*q+t).addScaledVector(m1,r-q)}let last=point(0);for(let i=1;i<=8;i++){const next=point(i/8),d=next.clone().sub(last),seg=new THREE.Mesh(geometry,hoseMaterial);seg.position.copy(last).add(next).multiplyScalar(.5);seg.scale.z=d.length();seg.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),d.normalize());hose.add(seg);last=next}}
let nozzle;
const gizmo=new TransformControls(camera,renderer.domElement);gizmo.setSize(.8);scene.add(gizmo.getHelper());
gizmo.addEventListener('dragging-changed',e=>{controls.enabled=!e.value});
const fields=Object.fromEntries(['px','py','pz','rx','ry','rz'].map(k=>[k,document.querySelector('#'+k)]));
const deg=THREE.MathUtils.radToDeg,rad=THREE.MathUtils.degToRad;
function sync(){if(!nozzle)return;const p=nozzle.position,r=nozzle.rotation;const values={px:p.x,py:p.y,pz:p.z,rx:deg(r.x),ry:deg(r.y),rz:deg(r.z)};for(const [k,v] of Object.entries(values))fields[k].value=Number(v.toFixed(3));document.querySelector('#values').value=`Poziție X=${fields.px.value} Y=${fields.py.value} Z=${fields.pz.value} blocuri; rotație X=${fields.rx.value} Y=${fields.ry.value} Z=${fields.rz.value} grade (ordine YXZ; pompă orientată ca în preview).`;renderHose(p)}
gizmo.addEventListener('objectChange',sync);
for(const field of Object.values(fields))field.addEventListener('change',()=>{if(!nozzle)return;const values=Object.fromEntries(Object.entries(fields).map(([k,e])=>[k,Number(e.value)]));if(Object.values(values).some(v=>!Number.isFinite(v)))return;nozzle.position.set(values.px,values.py,values.pz);nozzle.rotation.set(rad(values.rx),rad(values.ry),rad(values.rz),'YXZ');sync()});
function initial(){if(!nozzle)return;nozzle.position.set(-.5525,1.5,-.18);nozzle.rotation.set(Math.PI/2,Math.PI,0,'YXZ');sync()}
function mode(value){gizmo.enabled=true;gizmo.getHelper().visible=true;gizmo.setMode(value);for(const id of ['move','rotate','hide'])document.querySelector('#'+id).classList.toggle('active',id===(value==='translate'?'move':'rotate'));document.querySelector('#status').textContent=value==='translate'?'MOD MUTARE':'MOD ROTIRE'}
document.querySelector('#move').onclick=()=>mode('translate');document.querySelector('#rotate').onclick=()=>mode('rotate');document.querySelector('#hide').onclick=()=>{gizmo.enabled=false;gizmo.getHelper().visible=false;for(const id of ['move','rotate','hide'])document.querySelector('#'+id).classList.toggle('active',id==='hide');document.querySelector('#status').textContent='AXE ASCUNSE'};
document.querySelector('#original').onclick=()=>{if(!nozzle)return;nozzle.position.set(-.5525,1.5,-.18);nozzle.rotation.set(0,Math.PI,0,'YXZ');sync()};
document.querySelector('#copy').onclick=async()=>{const output=document.querySelector('#values');try{await navigator.clipboard.writeText(output.value);document.querySelector('#copy-status').textContent='Copiat! Trimite-mi valorile în conversație.'}catch{output.focus();output.select();document.querySelector('#copy-status').textContent='Selectează și copiază textul de mai sus, apoi trimite-mi-l.'}};
function reset(){camera.position.set(-2.8,2.3,3.4);controls.target.set(-.32,1.25,0);controls.update()}document.querySelector('#reset').onclick=reset;
new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;if(w&&h){camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h)}}).observe(host);
Promise.all(['/minecraft/gas_pump_bottom.json','/minecraft/gas_pump_top.json','/assets/nozzle.json'].map(async url=>{const r=await fetch(url);if(!r.ok)throw Error(url);return r.json()})).then(([bottom,top,n])=>{const b=makeModel(bottom,pumpTexture),t=makeModel(top,pumpTexture);b.position.y=.5;t.position.y=1.5;scene.add(b,t);nozzle=new THREE.Group();nozzle.add(makeModel(n,nozzleTexture));scene.add(nozzle);gizmo.attach(nozzle);initial();mode('translate');reset();document.querySelector('#loading').hidden=true}).catch(e=>{console.error(e);document.querySelector('#loading').textContent='Nu am putut încărca modelele. Reîncarcă pagina.'});
function frame(){requestAnimationFrame(frame);controls.update();renderer.render(scene,camera)}frame();
