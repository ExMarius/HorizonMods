const http=require('node:http'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=__dirname,workspace=path.resolve(root,'../../..'),dir=path.join(workspace,'downloads/glb-imports'),port=Number(process.env.PORT||4189);
const files={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/bbmodel.js':'bbmodel.js','/style.css':'style.css'};
function fail(res,code,message){res.writeHead(code,{'Content-Type':'application/json; charset=utf-8'}).end(JSON.stringify({error:message}))}
function body(req,res,limit,done){let size=0,parts=[],stopped=false;req.on('data',p=>{size+=p.length;if(size>limit){if(!stopped){stopped=true;fail(res,413,'Fișierul este prea mare.');}parts=[]}else if(!stopped)parts.push(p)});req.on('end',()=>{if(!stopped)done(Buffer.concat(parts))});req.on('error',()=>{if(!res.headersSent)fail(res,400,'Transfer întrerupt.')})}
function sameOrigin(req){if(!req.headers.origin)return false;try{return new URL(req.headers.origin).host===req.headers.host}catch{return false}}
http.createServer((req,res)=>{const url=new URL(req.url,'http://preview'),u=url.pathname;
 if(req.method==='POST'){
  if(!sameOrigin(req))return fail(res,403,'Origine nepermisă');
  if(u==='/api/upload'||u==='/api/upload-bbmodel')return body(req,res,40*1024*1024,data=>{
   const bb=u.endsWith('bbmodel');
   if(bb){try{const d=JSON.parse(data.toString('utf8'));if(!d||!Array.isArray(d.elements)||!Array.isArray(d.textures))throw Error()}catch{return fail(res,400,'Fișierul nu este un proiect Blockbench valid.')}}
   else if(data.length<12||data.toString('ascii',0,4)!=='glTF'||data.readUInt32LE(4)!==2||data.readUInt32LE(8)!==data.length)return fail(res,400,'Fișierul nu este un GLB 2.0 complet.');
   const id=crypto.randomBytes(8).toString('hex'),folder=path.join(dir,id);
   try{fs.mkdirSync(folder,{recursive:true});const name=bb?'model.bbmodel':'model.glb';fs.writeFileSync(path.join(folder,name),data,{flag:'wx'});res.writeHead(201,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'}).end(JSON.stringify({id,path:`downloads/glb-imports/${id}/${name}`}))}catch(err){console.error(err);fail(res,500,'Nu am putut salva fișierul.')}
  });
  const match=u.match(/^\/api\/capture\/([a-f0-9]{16})\/(front|back|left|right|overview)$/);
  if(match)return body(req,res,8*1024*1024,data=>{
   if(data.length<8||!data.subarray(0,8).equals(Buffer.from('89504e470d0a1a0a','hex')))return fail(res,400,'Imaginea nu este PNG.');
   const folder=path.join(dir,match[1]);if(!fs.existsSync(path.join(folder,'model.glb'))&&!fs.existsSync(path.join(folder,'model.bbmodel')))return fail(res,404,'Modelul nu există.');
   try{fs.writeFileSync(path.join(folder,match[2]+'.png'),data);res.writeHead(200,{'Content-Type':'application/json'}).end(JSON.stringify({path:`downloads/glb-imports/${match[1]}/${match[2]}.png`}))}catch(err){console.error(err);fail(res,500,'Nu am putut salva imaginea.')}
  });
  return fail(res,404,'Rută necunoscută');
 }
 if(!['GET','HEAD'].includes(req.method))return fail(res,405,'Metodă nepermisă');let file;
 const imported=u.match(/^\/api\/model\/([a-f0-9]{16})$/);
 if(imported){const folder=path.join(dir,imported[1]);file=path.join(folder,fs.existsSync(path.join(folder,'model.bbmodel'))?'model.bbmodel':'model.glb');res.setHeader('X-Model-Type',file.endsWith('.bbmodel')?'bbmodel':'glb');}else if(files[u])file=path.join(root,files[u]);else if(/^\/three\/(build|examples\/jsm)\/[\w./-]+\.js$/.test(u)&&!u.includes('..'))file=path.join(root,'node_modules/three',u.slice(7));else return fail(res,404,'Nu există');
 fs.readFile(file,(err,data)=>{if(err)return fail(res,404,'Fișier negăsit');const type={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8'}[path.extname(file)]||'application/octet-stream';res.writeHead(200,{'Content-Type':type,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}).end(req.method==='HEAD'?undefined:data)})
}).listen(port,'0.0.0.0',()=>console.log(`Vizualizator GLB disponibil pe portul ${port}`));
