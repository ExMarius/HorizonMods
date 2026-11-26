import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const entries={
 ambulance:{title:'Ambulanță',description:'Un vehicul pentru echipa medicală, cu spațiu în spate și semnalizare de intervenție.',idea:'Idee pentru joc: intervenții medicale și transport.',index:'01'},
 firetruck:{title:'Mașină de pompieri',description:'Un camion de intervenție pentru echipajele care răspund la incendii și situații de urgență.',idea:'Idee pentru joc: intervenții de pompieri și salvare.',index:'02'},
 'garbage-truck':{title:'Mașină de salubritate',description:'Un camion de serviciu pentru colectarea deșeurilor și întreținerea orașului.',idea:'Idee pentru joc: trasee de colectare și servicii municipale.',index:'03'}
};
const holder=document.querySelector('#scene'), status=document.querySelector('#loading');
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;holder.appendChild(renderer.domElement);
const scene=new THREE.Scene();const camera=new THREE.PerspectiveCamera(38,1,.05,100);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.enablePan=false;controls.minDistance=2;controls.maxDistance=15;controls.maxPolarAngle=Math.PI*.49;
scene.add(new THREE.HemisphereLight(0xf6fff2,0x829278,2.0));
const sun=new THREE.DirectionalLight(0xffffff,2.5);sun.position.set(5,10,7);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-6;sun.shadow.camera.right=6;sun.shadow.camera.top=6;sun.shadow.camera.bottom=-6;sun.shadow.normalBias=.03;scene.add(sun);
const platform=new THREE.Mesh(new THREE.CylinderGeometry(2.65,2.65,.10,96),new THREE.MeshStandardMaterial({color:0xeaf0e1,roughness:1}));platform.position.y=-.055;platform.receiveShadow=true;scene.add(platform);
const ring=new THREE.Mesh(new THREE.RingGeometry(2.31,2.32,100),new THREE.MeshBasicMaterial({color:0xc2d3b5,side:THREE.DoubleSide}));ring.rotation.x=-Math.PI/2;ring.position.y=.002;scene.add(ring);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(200,200),new THREE.ShadowMaterial({opacity:.16}));floor.rotation.x=-Math.PI/2;floor.position.y=-.11;floor.receiveShadow=true;scene.add(floor);
const loader=new GLTFLoader();let current=null,request=0;
function centerCamera(){camera.position.set(5.5,3.25,6);controls.target.set(0,.8,0);controls.update()}
function dispose(object){object.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material){for(const m of (Array.isArray(o.material)?o.material:[o.material])){if(m.map)m.map.dispose();m.dispose()}}})}
async function select(key){
 const e=entries[key];if(!e)return;const serial=++request;
 document.querySelectorAll('.choice').forEach(b=>{let active=b.dataset.model===key;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active))});
 document.querySelector('#title').textContent=e.title;document.querySelector('#description').textContent=e.description;
 document.querySelector('#idea').textContent=e.idea;document.querySelector('#detail-index').textContent=e.index;document.querySelector('#asset-index').textContent=e.index+' / 03';
 status.hidden=false;status.textContent='Se încarcă modelul 3D…';
 try{
  const gltf=await loader.loadAsync('/assets/'+key+'.glb');if(serial!==request){dispose(gltf.scene);return}
  if(current){scene.remove(current);dispose(current)}
  current=gltf.scene;current.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});
  // Normalize display scale for the gallery only; source geometry stays unchanged.
  const box=new THREE.Box3().setFromObject(current),size=box.getSize(new THREE.Vector3());
  const scale=3.5/Math.max(size.x,size.z);current.scale.setScalar(scale);
  const scaled=new THREE.Box3().setFromObject(current),center=scaled.getCenter(new THREE.Vector3());
  current.position.set(-center.x,-scaled.min.y,-center.z);scene.add(current);centerCamera();status.hidden=true;
 }catch(error){console.error(error);if(serial===request)status.textContent='Modelul nu s-a putut încărca. Reîncarcă pagina.'}
}
document.querySelectorAll('.choice').forEach(b=>b.addEventListener('click',()=>select(b.dataset.model)));
document.querySelector('#reset').addEventListener('click',centerCamera);
new ResizeObserver(()=>{const w=holder.clientWidth,h=holder.clientHeight;if(!w||!h)return;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h,false)}).observe(holder);
function frame(){requestAnimationFrame(frame);controls.update();renderer.render(scene,camera)}frame();select('ambulance');
