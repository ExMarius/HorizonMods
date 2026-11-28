import * as THREE from 'three';

// Blockbench free/entity cube and mesh renderer. No remote texture URLs are
// fetched: the file stays local until the user explicitly clicks Send.
export async function loadBlockbench(data){
 if(!data||!Array.isArray(data.elements)||!Array.isArray(data.textures))throw Error('Nu este un proiect Blockbench cu elemente și texturi');
 if(data.elements.length>50000)throw Error('Modelul are peste 50.000 de elemente');
 const root=new THREE.Group(),elements=new Map(data.elements.map(e=>[e.uuid,e])),groups=new Map((data.groups||[]).map(g=>[g.uuid,g]));
 const missing=[],loader=new THREE.TextureLoader();
 const materials=await Promise.all(data.textures.map(async(t,i)=>{
  if(!t.source||!/^data:image\/(png|jpeg|webp);base64,/i.test(t.source)){missing.push(t.name||String(i));return new THREE.MeshStandardMaterial({color:0xb6a6b8,roughness:.8,side:THREE.DoubleSide})}
  try{const map=await loader.loadAsync(t.source);map.colorSpace=THREE.SRGBColorSpace;map.magFilter=THREE.NearestFilter;map.minFilter=THREE.NearestMipmapNearestFilter;return new THREE.MeshStandardMaterial({map,transparent:true,side:THREE.DoubleSide,roughness:.8,alphaTest:.01})}
  catch{missing.push(t.name||String(i));return new THREE.MeshStandardMaterial({color:0xb6a6b8,side:THREE.DoubleSide})}
 }));
 const invisible=new THREE.MeshBasicMaterial({visible:false});
 function materialFor(ref){if(ref===null||ref===undefined||ref===false)return invisible;let i=typeof ref==='number'?ref:data.textures.findIndex(t=>t.uuid===ref||t.id===String(ref));if(i<0&&/^\d+$/.test(String(ref)))i=Number(ref);return materials[i]||invisible}
 function textureSize(ref){let i=typeof ref==='number'?ref:data.textures.findIndex(t=>t.uuid===ref||t.id===String(ref));const t=data.textures[i]||{};return [t.uv_width||data.resolution?.width||16,t.uv_height||data.resolution?.height||16]}
 function addElement(e,parent,parentOrigin){
  if(e.visibility===false)return;const rot=e.rotation||[0,0,0],origin=e.origin||e.from?.map((v,i)=>(v+e.to[i])/2)||[0,0,0];const pivot=new THREE.Group();pivot.position.set(...origin.map((v,i)=>v-parentOrigin[i]));pivot.rotation.set(...rot.map(THREE.MathUtils.degToRad),'ZYX');pivot.name=e.name||'';parent.add(pivot);
  if((e.type==='cube'||!e.type)&&Array.isArray(e.from)&&Array.isArray(e.to)){
   const inflate=Number(e.inflate||0),size=e.to.map((v,i)=>v-e.from[i]+2*inflate);if(size.some(n=>!Number.isFinite(n)||n<=0))return;
   const geometry=new THREE.BoxGeometry(...size),uv=geometry.attributes.uv,faces=['east','west','up','down','south','north'];
   const mats=faces.map((name,faceIndex)=>{const face=e.faces?.[name];if(!face)return invisible;const rect=face.uv||[0,0,16,16],[w,h]=textureSize(face.texture);let degrees=((face.rotation||0)%360+360)%360;
    for(let n=0;n<4;n++){const i=faceIndex*4+n;let u=uv.getX(i),v=1-uv.getY(i);for(let a=0;a<degrees;a+=90)[u,v]=[1-v,u];uv.setXY(i,(rect[0]+u*(rect[2]-rect[0]))/w,1-(rect[1]+v*(rect[3]-rect[1]))/h)}return materialFor(face.texture)});uv.needsUpdate=true;
   const mesh=new THREE.Mesh(geometry,mats);mesh.position.set(...e.from.map((v,i)=>(v+e.to[i])/2-origin[i]));pivot.add(mesh);return;
  }
  if(e.type==='mesh'&&e.vertices&&e.faces){
   const buckets=new Map();
   for(const face of Object.values(e.faces)){const ids=face.vertices||[];if(ids.length<3)continue;const key=String(face.texture),[w,h]=textureSize(face.texture);if(!buckets.has(key))buckets.set(key,{positions:[],uvs:[],indices:[],material:materialFor(face.texture)});const bucket=buckets.get(key),base=bucket.positions.length/3;
    for(const id of ids){const p=e.vertices[id],uv=face.uv?.[id]||[0,0];if(!p||p.length<3)throw Error('Vârf mesh lipsă');bucket.positions.push(...p);bucket.uvs.push(uv[0]/w,1-uv[1]/h)}
    for(let j=1;j<ids.length-1;j++)bucket.indices.push(base,base+j,base+j+1);
   }
   for(const b of buckets.values()){const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(b.positions,3));geometry.setAttribute('uv',new THREE.Float32BufferAttribute(b.uvs,2));geometry.setIndex(b.indices);geometry.computeVertexNormals();pivot.add(new THREE.Mesh(geometry,b.material))}
  }
 }
 const used=new Set();
 function visit(node,parent,parentOrigin){
  if(typeof node==='string'){const e=elements.get(node);if(e){used.add(node);addElement(e,parent,parentOrigin)}return}
  if(!node||typeof node!=='object')return;const info=groups.get(node.uuid)||node;if(info.visibility===false)return;const origin=info.origin||[0,0,0],g=new THREE.Group();g.name=info.name||'';g.position.set(...origin.map((v,i)=>v-parentOrigin[i]));g.rotation.set(...(info.rotation||[0,0,0]).map(THREE.MathUtils.degToRad),'ZYX');parent.add(g);for(const child of node.children||[])visit(child,g,origin)
 }
 for(const n of data.outliner||[])visit(n,root,[0,0,0]);if(!data.outliner?.length)for(const e of elements.values())addElement(e,root,[0,0,0]);
 return {scene:root,animations:[],missing};
}
