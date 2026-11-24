// Offline protocol test, including three passengers. It does not render a model.
const mineflayer = require('mineflayer')
const bot = mineflayer.createBot({ host:'127.0.0.1', port:25568, username:'HorizonBot', version:'1.21.4', auth:'offline' })
const others=[]
let done=false, started=false, mounting=false, driving=false, packs=0, packsAtSpawn=0, sirenOn=0, sirenOff=0, stopPackets=0
const timeout=setTimeout(()=>fail('timeout'), 100000)
function fail(s) { if(done)return; done=true; clearTimeout(timeout); console.error('FAIL: '+s); for(const b of others)b.quit(); bot.quit(); process.exitCode=1 }
function success() { if(done)return; done=true; clearTimeout(timeout); console.log('Four distinct riders mounted and stayed aboard during movement; no visual assertion.'); for(const b of others)b.quit(); bot.quit() }
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms))
bot.on('error', e=>fail(e.message))
bot.on('kicked', r=>fail('kicked '+String(r).slice(0,200)))
bot.on('end', ()=>{ if(!done)fail('unexpected disconnect') })
bot._client.on('packet', (data, meta)=>{ if(meta.name==='add_resource_pack') packs++; if(meta.name==='stop_sound') stopPackets++ })
bot.on('messagestr', s=>{ if(s.includes('Dacia Logan Politie creat')) started=true; if(s.includes('Sirena pornita.'))sirenOn++; if(s.includes('Sirena oprita.'))sirenOff++ })
bot.once('spawn', ()=>{
  setTimeout(()=>bot.chat('/fill ~-12 ~-1 ~-12 ~12 ~-1 ~12 stone'),1000)
  setTimeout(()=>bot.chat('/fill ~-12 ~ ~-12 ~12 ~5 ~12 air'),2200)
  setTimeout(()=>bot.chat('/tp @s ~ ~ ~ 0 0'),3000)
  setTimeout(()=>{ packsAtSpawn=packs; if(packsAtSpawn!==1)return fail('expected one login pack, got '+packsAtSpawn); bot.chat('/vehicle spawn dacia_logan_police') },4500)
})
async function testPassengers(target) {
  // Local root yaw is forced to zero; offsets come from the original Dacia configuration.
  const offsets=[[-4*1.7/16,-0.5*1.7/16],[-4*1.7/16,-8.4*1.7/16],[4*1.7/16,-8.4*1.7/16]]
  for(let i=0;i<3;i++) {
    const name='Passenger'+(i+1)
    const rider=mineflayer.createBot({host:'127.0.0.1',port:25568,username:name,version:'1.21.4',auth:'offline'})
    others.push(rider)
    rider.on('error',e=>fail(name+': '+e.message))
    rider.on('kicked',r=>fail(name+' kicked: '+String(r).slice(0,200)))
    await Promise.race([new Promise(resolve=>rider.once('spawn',resolve)),wait(15000).then(()=>{throw new Error(name+' did not join')})])
    const x=target.position.x+offsets[i][0], y=target.position.y+1, z=target.position.z+offsets[i][1]
    bot.chat(`/tp ${name} ${x} ${y} ${z}`)
    await wait(1800)
    const t=Object.values(rider.entities).find(e=>e.name==='interaction')
    if(!t)throw new Error(name+' cannot see vehicle')
    for(let j=0;j<4 && !rider.vehicle;j++){ rider.activateEntity(t); await wait(1000) }
    if(!rider.vehicle) throw new Error(name+' failed to mount')
    const ids=[bot,...others].map(b=>b.vehicle && b.vehicle.id)
    if(new Set(ids).size!==ids.length)throw new Error('two players assigned to same seat')
  }
  const start=target.position.clone()
  const input=setInterval(()=>bot._client.write('player_input',{inputs:{forward:true}}),50)
  await wait(5000);clearInterval(input);bot._client.write('player_input',{inputs:{}})
  if([bot,...others].some(b=>!b.vehicle))throw new Error('a rider left their seat while moving')
  if(target.position.distanceTo(start)<0.3)throw new Error('driver did not move vehicle')
  if(packs!==packsAtSpawn)throw new Error('resource pack resent during driving')
  bot.chat('/item replace entity HorizonBot weapon.mainhand with minecraft:diamond 3')
  bot.chat('/item replace entity HorizonBot weapon.offhand with minecraft:torch 2')
  await wait(1000)
  const before=[bot.heldItem?.name,bot.heldItem?.count,bot.inventory.slots[45]?.name,bot.inventory.slots[45]?.count]
  if(before.join(',')!=='diamond,3,torch,2') throw new Error('test inventory setup failed: '+before)
  function pressF(){ bot._client.write('block_dig',{status:6,location:{x:0,y:0,z:0},face:0,sequence:0}) }
  bot.chat('/vehicle sirena'); await wait(600)
  others[0]._client.write('block_dig',{status:6,location:{x:0,y:0,z:0},face:0,sequence:0}); await wait(600)
  bot.chat('/vehicle sirena'); await wait(700)
  if(sirenOn!==1 || sirenOff!==1) throw new Error('passenger toggled siren')
  pressF(); await wait(1000)
  bot.chat('/vehicle sirena'); await wait(1000)
  if(sirenOff!==2 || stopPackets<1) throw new Error('F did not start siren or stop packet missing')
  pressF(); await wait(1000)
  bot.chat('/vehicle sirena'); await wait(1000)
  if(sirenOff!==3) throw new Error('F did not restart siren')
  bot.chat('/vehicle sirena'); await wait(600); bot.chat('/vehicle sirena'); await wait(600)
  if(sirenOn!==2 || sirenOff!==4) throw new Error('siren command toggle failed')
  const after=[bot.heldItem?.name,bot.heldItem?.count,bot.inventory.slots[45]?.name,bot.inventory.slots[45]?.count]
  if(before.join(',')!==after.join(',')) throw new Error('F changed inventory: '+after)
  bot.chat('/item replace entity HorizonBot weapon.mainhand with minecraft:air')
  bot.chat('/item replace entity HorizonBot weapon.offhand with minecraft:air')
  await wait(700); pressF(); await wait(700); bot.chat('/vehicle sirena'); await wait(700)
  if(sirenOff!==5) throw new Error('F failed with empty hands')
  bot.chat('/vehicle save'); await wait(1000); success()
}
const interval=setInterval(()=>{
  if(done) {clearInterval(interval); return}
  if(!started)return
  const entities=Object.values(bot.entities), displays=entities.filter(e=>e.name==='item_display')
  const target=entities.find(e=>e.name==='interaction')
  if(!driving && bot.vehicle && target) {
    driving=true
    if(bot.vehicle.name!=='horse')return fail('unexpected mount '+bot.vehicle.name)
    if(displays.length<13)return fail('not all expected displays present: '+displays.length)
    if(packs!==packsAtSpawn)return fail('resource pack resent on spawn')
    testPassengers(target).catch(e=>fail(e.message))
  } else if(!bot.vehicle && target && displays.length>=13 && !mounting) {
    mounting=true; bot.activateEntity(target); setTimeout(()=>{mounting=false},1500)
  }
},500)
