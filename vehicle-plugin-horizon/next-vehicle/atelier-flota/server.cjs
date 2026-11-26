const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const root=__dirname,port=Number(process.env.PORT||4176);
const files=new Map([['/','index.html'],['/index.html','index.html'],['/app.js','app.js'],['/design.js','design.js'],['/loading-demo.js','loading-demo.js'],['/loading-kinematics.js','loading-kinematics.js'],['/minecraft-preview.js','minecraft-preview.js'],['/style.css','style.css']]);
http.createServer((req,res)=>{
 if(req.method!=='GET'&&req.method!=='HEAD')return res.writeHead(405).end();
 const p=new URL(req.url,'http://local').pathname;let f=files.get(p);
 if(!f&&/^\/three\/(build|examples\/jsm)\/[\w./-]+\.js$/.test(p)&&!p.includes('..'))f='node_modules/three/'+p.slice(7);
 if(!f && /^\/minecraft\/models\/item\/horizon_service_(cab|flatbed|workshop|wheel|steering|ramp)\.json$/.test(p)) f='minecraft/assets/'+p.slice('/minecraft/'.length);
 if(p==='/reference/dacia/body.json')f='../assets/user-edits/body_flash_1.json';
 else if(/^\/reference\/dacia\/[a-z0-9_]+\.png$/.test(p))f='reference/dacia/'+path.basename(p);
 if(!f)return res.writeHead(404).end('Not found');
 fs.readFile(path.join(root,f),(e,b)=>{if(e)return res.writeHead(404).end('Not found');let t=f.endsWith('.html')?'text/html; charset=utf-8':f.endsWith('.css')?'text/css; charset=utf-8':f.endsWith('.json')?'application/json; charset=utf-8':f.endsWith('.png')?'image/png':'text/javascript; charset=utf-8';res.writeHead(200,{'Content-Type':t,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}).end(req.method==='HEAD'?undefined:b)});
}).listen(port,'0.0.0.0',()=>console.log('Atelier 3D pe portul '+port));
