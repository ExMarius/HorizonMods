const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const root=__dirname,port=Number(process.env.PORT||4176);
const files=new Map([['/','index.html'],['/index.html','index.html'],['/app.js','app.js'],['/design.js','design.js'],['/style.css','style.css']]);
http.createServer((req,res)=>{
 if(req.method!=='GET'&&req.method!=='HEAD')return res.writeHead(405).end();
 const p=new URL(req.url,'http://local').pathname;let f=files.get(p);
 if(!f&&/^\/three\/(build|examples\/jsm)\/[\w./-]+\.js$/.test(p)&&!p.includes('..'))f='node_modules/three/'+p.slice(7);
 if(!f)return res.writeHead(404).end('Not found');
 fs.readFile(path.join(root,f),(e,b)=>{if(e)return res.writeHead(404).end('Not found');let t=f.endsWith('.html')?'text/html; charset=utf-8':f.endsWith('.css')?'text/css; charset=utf-8':'text/javascript; charset=utf-8';res.writeHead(200,{'Content-Type':t,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}).end(req.method==='HEAD'?undefined:b)});
}).listen(port,'0.0.0.0',()=>console.log('Atelier 3D pe portul '+port));
