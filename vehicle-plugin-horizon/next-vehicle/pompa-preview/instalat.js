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
// Reference from GasPumpRig: 8 square segments sampling the same Hermite
// curve, at yaw zero. The currently installed hose terminates at the display
// origin, not at a verified physical fitting on the nozzle model.
const hose=new THREE.Group();scene.add(hose);
const rubber=new THREE.MeshStandardMaterial({color:'#202426',roughness:1});
const hoseGeometry=new THREE.BoxGeometry(.0625,.0625,1);
const hoseParts=Array.from({length:8},()=>{const p=new THREE.Mesh(hoseGeometry,rubber);hose.add(p);return p});
const start=new THREE.Vector3(-.575,1.64,.1125),t0=new THREE.Vector3(0,-5,0),t1=new THREE.Vector3(0,3,0);
function renderHose(){
 if(!nozzle)return;const end=nozzle.position;
 function point(t){const q=t*t,r=q*t;return start.clone().multiplyScalar(2*r-3*q+1).addScaledVector(end,-2*r+3*q).addScaledVector(t0,r-2*q+t).addScaledVector(t1,r-q)}
 let last=point(0);for(let i=0;i<hoseParts.length;i++){const next=point((i+1)/hoseParts.length),d=next.clone().sub(last),part=hoseParts[i];part.position.copy(last).add(next).multiplyScalar(.5);part.scale.z=d.length();if(d.lengthSq()>1e-8)part.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),d.normalize());last=next}
}
// Display uses a canvas purely to demonstrate changing litres and total price.
const displayCanvas=document.createElement('canvas');displayCanvas.width=512;displayCanvas.height=192;const ctx=displayCanvas.getContext('2d');const displayTexture=new THREE.CanvasTexture(displayCanvas);displayTexture.colorSpace=THREE.SRGBColorSpace;const display=new THREE.Mesh(new THREE.PlaneGeometry(.57,.215),new THREE.MeshBasicMaterial({map:displayTexture}));display.position.set(0,1.49,.439);scene.add(display);
function displayUpdate(){const l=Math.max(0,Number(document.querySelector('#litres').value)||0),p=Math.max(0,Number(document.querySelector('#price').value)||0);ctx.fillStyle='#b7d1c0';ctx.fillRect(0,0,512,192);ctx.fillStyle='#20342e';ctx.font='bold 48px monospace';ctx.fillText(l.toFixed(2)+' L',15,65);ctx.fillText((l*p).toFixed(2)+' $',15,125);ctx.font='20px sans-serif';ctx.fillText('PREȚ / L   '+p.toFixed(2),15,169);displayTexture.needsUpdate=true}document.querySelector('#litres').oninput=displayUpdate;document.querySelector('#price').oninput=displayUpdate;displayUpdate();
// Schematic 1.8-block-tall player for an honest scale comparison.
const person=new THREE.Group();scene.add(person);person.position.set(1.35,0,.25);
function part(size,pos,color){const m=new THREE.Mesh(new THREE.BoxGeometry(...size),new THREE.MeshStandardMaterial({color}));m.position.set(...pos);person.add(m)}
part([.5,.5,.5],[0,1.55,0],'#dba577');part([.5,.65,.25],[0,.975,0],'#4e8b81');for(const x of [-.13,.13])part([.24,.65,.25],[x,.325,0],'#38445a');for(const x of [-.36,.36])part([.22,.65,.22],[x,.975,0],'#4e8b81');
let nozzle;
const gizmo=new TransformControls(camera,renderer.domElement);gizmo.setSize(.8);scene.add(gizmo.getHelper());
gizmo.addEventListener('dragging-changed',e=>{controls.enabled=!e.value});
const fields=Object.fromEntries(['px','py','pz','rx','ry','rz'].map(k=>[k,document.querySelector('#'+k)]));
const deg=THREE.MathUtils.radToDeg,rad=THREE.MathUtils.degToRad;
function sync(){if(!nozzle)return;const p=nozzle.position,r=nozzle.rotation;const values={px:p.x,py:p.y,pz:p.z,rx:deg(r.x),ry:deg(r.y),rz:deg(r.z)};for(const [k,v] of Object.entries(values))fields[k].value=Number(v.toFixed(3));document.querySelector('#values').value=`Poziție X=${fields.px.value} Y=${fields.py.value} Z=${fields.pz.value} blocuri; rotație X=${fields.rx.value} Y=${fields.ry.value} Z=${fields.rz.value} grade (ordine YXZ; pompă orientată ca în preview).`;renderHose()}
gizmo.addEventListener('objectChange',sync);
for(const field of Object.values(fields))field.addEventListener('change',()=>{if(!nozzle)return;const values=Object.fromEntries(Object.entries(fields).map(([k,e])=>[k,Number(e.value)]));if(Object.values(values).some(v=>!Number.isFinite(v)))return;nozzle.position.set(values.px,values.py,values.pz);nozzle.rotation.set(rad(values.rx),rad(values.ry),rad(values.rz),'YXZ');sync()});
function initial(){if(!nozzle)return;nozzle.position.set(-.49,1.5,-.18);nozzle.rotation.set(0,Math.PI,0,'YXZ');sync()}
function mode(value){gizmo.enabled=true;gizmo.getHelper().visible=true;gizmo.setMode(value);for(const id of ['move','rotate','hide'])document.querySelector('#'+id).classList.toggle('active',id===(value==='translate'?'move':'rotate'));document.querySelector('#status').textContent=value==='translate'?'MOD MUTARE':'MOD ROTIRE'}
document.querySelector('#move').onclick=()=>mode('translate');document.querySelector('#rotate').onclick=()=>mode('rotate');document.querySelector('#hide').onclick=()=>{gizmo.enabled=false;gizmo.getHelper().visible=false;for(const id of ['move','rotate','hide'])document.querySelector('#'+id).classList.toggle('active',id==='hide');document.querySelector('#status').textContent='AXE ASCUNSE'};
document.querySelector('#original').onclick=initial;
document.querySelector('#copy').onclick=async()=>{const output=document.querySelector('#values');try{await navigator.clipboard.writeText(output.value);document.querySelector('#copy-status').textContent='Copiat! Trimite-mi valorile în conversație.'}catch{output.focus();output.select();document.querySelector('#copy-status').textContent='Selectează și copiază textul de mai sus, apoi trimite-mi-l.'}};
function reset(){camera.position.set(-3.1,2.25,3.5);controls.target.set(-.34,1.15,0);controls.update()}document.querySelector('#reset').onclick=reset;
new ResizeObserver(()=>{const w=host.clientWidth,h=host.clientHeight;if(w&&h){camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h)}}).observe(host);
Promise.all(['/minecraft/gas_pump_bottom.json','/minecraft/gas_pump_top.json','/assets/nozzle.json'].map(async url=>{const r=await fetch(url);if(!r.ok)throw Error(url);return r.json()})).then(([bottom,top,n])=>{
 // Reproduce the two models from the currently installed red resource pack.
 const b=makeModel(bottom,pumpTexture),t=makeModel(top,pumpTexture);b.position.y=.5;t.position.y=1.5;scene.add(b,t);
 nozzle=new THREE.Group();nozzle.add(makeModel(n,nozzleTexture));scene.add(nozzle);gizmo.attach(nozzle);initial();mode('translate');reset();document.querySelector('#loading').hidden=true}).catch(e=>{console.error(e);document.querySelector('#loading').textContent='Nu am putut încărca modelele. Reîncarcă pagina.'});
function frame(){requestAnimationFrame(frame);controls.update();renderer.render(scene,camera)}frame();
