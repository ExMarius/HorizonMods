const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const root=__dirname, port=Number(process.env.PORT||4185);
const assetRoot=path.resolve(root,'../../../vehicle-plugin/src/main/resources/assets/vehicle');
const pages={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css'};
http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405).end();return}
 const u=new URL(req.url,'http://preview').pathname;let file;
 if(pages[u])file=path.join(root,pages[u]);
 else if(/^\/three\/(build|examples\/jsm)\/[\w./-]+\.js$/.test(u)&&!u.includes('..'))file=path.join(root,'node_modules/three',u.slice(7));
 else if(/^\/models\/(gas_pump_bottom|gas_pump_top|nozzle)\.json$/.test(u))file=path.join(assetRoot,'models',u.includes('nozzle')?'vehicle':'block',path.basename(u));
 else if(/^\/textures\/(gas_pump|nozzle)\.png$/.test(u))file=path.join(assetRoot,'textures/model',path.basename(u));
 else {res.writeHead(404).end();return}
 fs.readFile(file,(err,data)=>{if(err){res.writeHead(404).end();return}const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png'};res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'});res.end(req.method==='HEAD'?undefined:data)});
}).listen(port,'0.0.0.0',()=>console.log(`Preview pompa 3D pe portul ${port}`));
