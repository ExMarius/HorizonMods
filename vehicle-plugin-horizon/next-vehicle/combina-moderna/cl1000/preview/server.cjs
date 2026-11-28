const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const root=__dirname,workspace=path.resolve(root,'../../../../..'),viewer=path.resolve(root,'../../../vizualizator-glb');
const files={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/vehicle-assets.js':'vehicle-assets.js','/style.css':'style.css'};
http.createServer((req,res)=>{if(!['GET','HEAD'].includes(req.method))return res.writeHead(405).end();const u=new URL(req.url,'http://preview').pathname;let file;
 if(u==='/model.bbmodel')file=path.join(workspace,'downloads/glb-imports/cb7869cfffcd6e70/model.bbmodel');
 else if(/^\/vehicle-model\/(utb_650_body|utb_650_wheel_front|utb_650_wheel_rear|tractor_trailer_body|tractor_trailer_modern_body|tractor_trailer_modern_axle|tractor_trailer_modern_drawbar)\.json$/.test(u))file=path.join(workspace,'vehicle-plugin-horizon/next-vehicle/utb/assets',u.split('/').pop());
 else if(/^\/utb-textures\/(red|cream|roof|black|frame|metal|silver|lamp|tail|seat|logo|amber|gauges|plate_blue|plate_tractor|plate_trailer|rm_green|rm_dark|rm_hose_blue)\.png$/.test(u))file=path.join(workspace,'vehicle-plugin-horizon/next-vehicle/utb/assets/textures',u.split('/').pop());
 else if(/^\/minecraft-textures\/(wheat|wheat_seeds|wheat_stage7|wheat_stage3)\.png$/.test(u))file=path.join(workspace,'downloads/minecraft-preview-textures',u.split('/').pop());
 else if(u==='/bbmodel.js')file=path.join(viewer,'bbmodel.js');
 else if(files[u])file=path.join(root,files[u]);
 else if(/^\/three\/(build|examples\/jsm)\/[\w./-]+\.js$/.test(u)&&!u.includes('..'))file=path.join(viewer,'node_modules/three',u.slice(7));
 else return res.writeHead(404).end();fs.readFile(file,(err,data)=>{if(err)return res.writeHead(404).end('Fișier indisponibil');const type={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.bbmodel':'application/json; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png'}[path.extname(file)]||'application/octet-stream';res.writeHead(200,{'Content-Type':type,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}).end(req.method==='HEAD'?undefined:data)})
}).listen(Number(process.env.PORT||4188),'0.0.0.0',()=>console.log('Simulare combină CL1000 pe portul '+(process.env.PORT||4188)));
