// Offline protocol smoke test. It does not validate rendering or camera.
const mineflayer = require('mineflayer')
const bot = mineflayer.createBot({ host:'127.0.0.1', port:25568, username:'HorizonBot', version:'1.21.4', auth:'offline' })
let done=false, started=false, mounting=false, driving=false, packs=0, packsAtSpawn=0
const timeout=setTimeout(()=>fail('timeout'), 65000)
function fail(s) { if(done)return; done=true; clearTimeout(timeout); console.error('FAIL: '+s); bot.quit(); process.exitCode=1 }
function success() { if(done)return; done=true; clearTimeout(timeout); console.log('Horizon vehicle spawned, mounted and moved with display entities; no visual assertion.'); bot.quit() }
bot.on('error', e=>fail(e.message))
bot.on('kicked', r=>fail('kicked '+String(r).slice(0,200)))
bot.on('end', ()=>{ if(!done)fail('unexpected disconnect') })
bot._client.on('packet', (data, meta)=>{ if(meta.name==='add_resource_pack') packs++ })
bot.on('messagestr', s=>{ if(s.includes('Horizon Off Roader creat')) started=true })
bot.once('spawn', ()=>{
  setTimeout(()=>bot.chat('/fill ~-12 ~-1 ~-12 ~12 ~-1 ~12 stone'),1000)
  setTimeout(()=>bot.chat('/fill ~-12 ~ ~-12 ~12 ~5 ~12 air'),2200)
  setTimeout(()=>{ packsAtSpawn=packs; if(packsAtSpawn!==1)return fail('expected one login pack, got '+packsAtSpawn); bot.chat('/vehicle spawn horizon_off_roader') },4000)
})
const interval=setInterval(()=>{
  if(done) {clearInterval(interval); return}
  if(!started)return
  const entities=Object.values(bot.entities)
  const displays=entities.filter(e=>e.name==='item_display')
  const target=entities.find(e=>e.name==='interaction')
  if(!driving && bot.vehicle && target) {
    driving=true
    if(bot.vehicle.name!=='horse')return fail('unexpected mount '+bot.vehicle.name)
    if(displays.length<30)return fail('not all grouped displays present: '+displays.length)
    if(packs!==packsAtSpawn)return fail('pack sent again when spawning vehicle')
    const start=target.position.clone()
    const input=setInterval(()=>bot._client.write('player_input',{inputs:{forward:true}}),50)
    setTimeout(()=>{
      clearInterval(input); bot._client.write('player_input',{inputs:{}})
      if(!bot.vehicle)return fail('rider left seat while driving')
      if(packs!==packsAtSpawn)return fail('resource pack resent during driving')
      if(target.position.distanceTo(start)<0.3)return fail('vehicle did not move: '+target.position.distanceTo(start))
      bot.chat('/vehicle save')
      setTimeout(success,1000)
    },5000)
  } else if(!bot.vehicle && target && displays.length>=30 && !mounting) {
    mounting=true
    bot.activateEntity(target)
    setTimeout(()=>{mounting=false},1500)
  }
},500)
