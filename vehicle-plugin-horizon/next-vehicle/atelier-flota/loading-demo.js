import * as T from 'three';

/** Real user-edited Dacia body, loaded from the repo; wheel positions are preview approximations. */
export async function loadDacia(){
 const response=await fetch('/reference/dacia/body.json');if(!response.ok)throw Error('Modelul Dacia nu poate fi încărcat');
 const data=await response.json(),loader=new T.TextureLoader(),materials=new Map();
 const invisible=new T.MeshBasicMaterial({visible:false});
 function material(ref){
  if(!ref?.startsWith('daciapolice:item/'))return invisible;
  if(!materials.has(ref)){const map=loader.load('/reference/dacia/'+ref.split('/').pop()+'.png');map.colorSpace=T.SRGBColorSpace;map.magFilter=T.NearestFilter;map.minFilter=T.NearestFilter;materials.set(ref,new T.MeshStandardMaterial({map,roughness:.7,transparent:true,alphaTest:.1,side:T.DoubleSide}))}
  return materials.get(ref);
 }
 const body=new T.Group();body.scale.setScalar(1.7/16);body.position.y=(.5+2.6/16)*1.7;
 const names=['east','west','up','down','south','north'];
 for(const e of data.elements){
  const size=e.to.map((v,i)=>Math.max(.001,v-e.from[i])),center=e.to.map((v,i)=>(v+e.from[i])/2-8),geo=new T.BoxGeometry(...size),uv=geo.attributes.uv;
  const faceMaterials=names.map((face,i)=>{
   const f=e.faces?.[face];if(!f)return invisible;const [u0,v0,u1,v1]=f.uv||[0,0,16,16];const points=[[u0,16-v0],[u1,16-v0],[u0,16-v1],[u1,16-v1]];
   const turns=((f.rotation||0)/90)%4;for(let k=0;k<4;k++){let j=k;for(let n=0;n<turns;n++)j=[1,3,0,2][j];uv.setXY(i*4+k,points[j][0]/16,points[j][1]/16)}
   return material(data.textures[(f.texture||'').slice(1)]);
  });
  uv.needsUpdate=true;const mesh=new T.Mesh(geo,faceMaterials);mesh.castShadow=true;mesh.receiveShadow=true;
  if(e.rotation){const pivot=new T.Group(),p=e.rotation.origin.map(n=>n-8);pivot.position.set(...p);mesh.position.set(...center.map((n,i)=>n-p[i]));pivot.rotation[e.rotation.axis]=T.MathUtils.degToRad(e.rotation.angle);pivot.add(mesh);body.add(pivot)}else{mesh.position.set(...center);body.add(mesh)}
 }
 const car=new T.Group(),oriented=new T.Group();oriented.rotation.y=Math.PI;oriented.add(body);car.add(oriented);
 const tires=[],rubber=new T.MeshStandardMaterial({color:'#202426',roughness:.9}),rim=new T.MeshStandardMaterial({color:'#a6afb0',metalness:.45,roughness:.55});
 for(const x of [-1.03,1.03])for(const z of [-1.65,1.65]){
  const pivot=new T.Group();pivot.position.set(x,.40,z);car.add(pivot);tires.push(pivot);
  const tire=new T.Mesh(new T.CylinderGeometry(.40,.40,.32,16),rubber);tire.rotation.z=Math.PI/2;tire.castShadow=true;pivot.add(tire);
  const hub=new T.Mesh(new T.CylinderGeometry(.23,.23,.035,16),rim);hub.rotation.z=Math.PI/2;hub.position.x=Math.sign(x)*.18;pivot.add(hub);
 }
 // Approximate cable attachment in front of the vehicle; no claim of a physical tow eye.
 const attach=new T.Object3D();attach.position.set(0,.55,-2.30);car.add(attach);
 return {car,tires,attach};
}
