const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root=__dirname, port=Number(process.env.PORT||4175);
const content=path.resolve(root,'../../../content/assets/gokart');
const allowed=new Map([
 ['/', 'index.html'], ['/index.html','index.html'], ['/app.js','app.js'], ['/style.css','style.css']
]);
http.createServer((req,res)=>{
 if(req.method!=='GET' && req.method!=='HEAD'){res.writeHead(405).end();return;}
 const url=new URL(req.url,'http://localhost'); let file=allowed.get(url.pathname);
 if(!file && /^\/three\/(build|examples\/jsm)\/[\w./-]+\.js$/.test(url.pathname) && !url.pathname.includes('..'))
   file='node_modules/three/'+url.pathname.slice('/three/'.length);
 let full;
 if (/^\/models\/(ambulance_body|smurd_body|fire_truck_body|wheel_standard)\.json$/.test(url.pathname))
   full=path.join(content,'models/block',path.basename(url.pathname));
 else if (/^\/textures\/[a-z0-9_]+\.png$/.test(url.pathname))
   full=path.join(content,'textures/block',path.basename(url.pathname));
 else if (file) full=path.join(root,file);
 else {res.writeHead(404).end('Not found');return;}

 fs.readFile(full,(err,data)=>{
  if(err){res.writeHead(404).end('Not found');return;}
  const ext=path.extname(full), types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.glb':'model/gltf-binary','.png':'image/png','.json':'application/json; charset=utf-8','.txt':'text/plain; charset=utf-8'};
  res.writeHead(200,{'Content-Type':types[ext]||'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
  res.end(req.method==='HEAD'?undefined:data);
 });
}).listen(port,'0.0.0.0',()=>console.log(`Galeria 3D pornește pe portul ${port}`));
