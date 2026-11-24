// Protocol-only test: spawn, mount, drive, inventory stability, save. No visual validation.
const mineflayer = require('mineflayer')
const bot = mineflayer.createBot({host:'127.0.0.1',port:25568,username:'HorizonBot',version:'1.21.4',auth:'offline'})
let done=false,started=false,mounting=false,driving=false,packs=0,originalPacks=0
const timeout=setTimeout(()=>fail('timeout'),100000)
function fail(s){if(done)return;done=true;clearTimeout(timeout);console.error('FAIL: '+s);bot.quit();process.exitCode=1}
function success(){if(done)return;done=true;clearTimeout(timeout);console.log('UTB tractor spawn, mount, movement, inventory and save passed; no visual assertion.');bot.quit()}
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms))
bot.on('error',e=>fail(e.message));bot.on('kicked',r=>fail('kicked '+String(r).slice(0,200)));bot.on('end',()=>{if(!done)fail('unexpected disconnect')})
bot._client.on('packet',(data,meta)=>{if(meta.name==='add_resource_pack')packs++})
bot.on('messagestr',s=>{if(s.includes('UTB 650 creat'))started=true})
bot.once('spawn',()=>{
 setTimeout(()=>bot.chat('/fill ~-12 ~-1 ~-12 ~12 ~-1 ~12 stone'),1000)
 setTimeout(()=>bot.chat('/fill ~-12 ~ ~-12 ~12 ~5 ~12 air'),2200)
 setTimeout(()=>bot.chat('/tp @s ~ ~ ~ 0 0'),3000)
 setTimeout(()=>{originalPacks=packs;if(packs!==1)return fail('expected one login pack');bot.chat('/vehicle spawn utb_650')},4500)
})
async function drive(target){
 if(bot.vehicle.name!=='horse')throw new Error('unexpected mount '+bot.vehicle.name)
 const start=target.position.clone(),before=JSON.stringify(bot.inventory.slots)
 const send=setInterval(()=>bot._client.write('player_input',{inputs:{forward:true}}),50)
 await wait(5000);clearInterval(send);bot._client.write('player_input',{inputs:{}})
 if(!bot.vehicle || target.position.distanceTo(start)<.3)throw new Error('tractor did not drive')
 if(JSON.stringify(bot.inventory.slots)!==before)throw new Error('inventory changed while driving')
 if(packs!==originalPacks)throw new Error('pack resent after spawn')
 bot.chat('/vehicle save');await wait(1200);console.log('POSITION tractor='+JSON.stringify(target.position)+' horse='+JSON.stringify(bot.vehicle?.position)+' yaw='+bot.entity.yaw);success()
}
const interval=setInterval(()=>{
 if(done){clearInterval(interval);return}
 if(!started)return
 const entities=Object.values(bot.entities),target=entities.find(e=>e.name==='interaction'), displays=entities.filter(e=>e.name==='item_display')
 if(!driving && bot.vehicle && target){driving=true;if(displays.length<6)return fail('missing display groups: '+displays.length);drive(target).catch(e=>fail(e.message))}
 else if(!bot.vehicle && target && displays.length>=6 && !mounting){mounting=true;bot.activateEntity(target);setTimeout(()=>mounting=false,1500)}
},500)
