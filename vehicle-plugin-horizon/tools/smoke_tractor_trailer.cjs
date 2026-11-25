// Protocol integration: inventory, incompatible and compatible coupling, towing and persistence.
const mineflayer=require('mineflayer')
const farmId=process.env.FARM_TRAILER_ID || 'tractor_trailer'
const bot=mineflayer.createBot({host:'127.0.0.1',port:25568,username:'HorizonBot',version:'1.21.4',auth:'offline'})
const wait=ms=>new Promise(r=>setTimeout(r,ms));let done=false,messages=[]
const timer=setTimeout(()=>fail('timeout: '+messages.slice(-12).join(' | ')),110000)
function fail(s){if(done)return;done=true;clearTimeout(timer);console.error('FAIL: '+s);bot.quit();process.exitCode=1}
function pass(){if(done)return;done=true;clearTimeout(timer);console.log('Farm trailer inventory, tractor-only coupling and towing verified; visuals not tested.');bot.quit()}
function check(c,m){if(!c)throw new Error(m+'; '+messages.slice(-12).join(' | '))}
bot.on('error',e=>fail(e.message));bot.on('kicked',r=>fail('kicked '+String(r)));bot.on('end',()=>{if(!done)fail('unexpected disconnect')});bot.on('messagestr',s=>messages.push(s))
function interactions(){return Object.values(bot.entities).filter(e=>e.name==='interaction')}
async function run(){
 await wait(1800);bot.chat('/fill ~-15 ~-1 ~-15 ~15 ~-1 ~15 stone');await wait(1300);bot.chat('/fill ~-15 ~ ~-15 ~15 ~5 ~15 air');await wait(1100);bot.chat('/tp @s ~ ~ ~ 0 0');await wait(800)
 bot.chat('/vehicle spawn '+farmId);await wait(2200)
 const trailer=interactions()[0];check(trailer,'no trailer interaction')
 const displayCount=()=>Object.values(bot.entities).filter(e=>e.name==='item_display').length
 const emptyDisplays=displayCount()
 if(farmId==='tractor_trailer_modern')check(emptyDisplays>=6,'modern trailer must have body, front assembly and four wheels')
 bot.chat('/give @s minecraft:diamond 3');await wait(800);bot.chat('/give @s minecraft:wheat_seeds 5');await wait(800)
 const opened=new Promise(r=>bot.once('windowOpen',r));bot.activateEntity(trailer);const window=await opened;await wait(500)
 const slot=window.slots.findIndex((x,i)=>i>=window.inventoryStart && x && x.name==='diamond');check(slot>=0,'missing diamonds in player inventory')
 await bot.clickWindow(slot,0,0);await bot.clickWindow(0,0,0);await wait(400);check(window.slots[0] && window.slots[0].name==='diamond','failed to store cargo')
 const seeds=window.slots.findIndex((x,i)=>i>=window.inventoryStart && x && x.name==='wheat_seeds');check(seeds>=0,'missing seeds')
 await bot.clickWindow(seeds,0,0);await bot.clickWindow(1,0,0);await wait(400);bot.closeWindow(window);await wait(1600)
 check(displayCount()>=emptyDisplays+2, 'missing cargo ItemDisplays: empty='+emptyDisplays+' now='+displayCount())
 bot.chat('/tp @s ~ ~ ~3');await wait(500);bot.chat('/vehicle spawn quad_bike');await wait(1600)
 bot.chat('/vehicle cupleaza_remorca');await wait(1000);check(messages.some(s=>s.includes('Ai nevoie de un tractor autorizat')),'non-tractor was not rejected')
 const before=new Set(interactions().map(e=>e.id));bot.chat('/vehicle spawn utb_650');await wait(2200)
 const tractor=interactions().find(e=>!before.has(e.id));check(tractor,'no tractor interaction')
 bot.chat('/vehicle cupleaza_remorca');await wait(1500);check(messages.some(s=>s.includes('Remorcă agricolă cuplată')),'tractor coupling failed')
 bot.activateEntity(tractor);await wait(1500);check(bot.vehicle,'tractor mount failed')
 const start=trailer.position.clone();const drive=setInterval(()=>bot._client.write('player_input',{inputs:{forward:true}}),50);await wait(6000);clearInterval(drive);bot._client.write('player_input',{inputs:{}});await wait(1000)
 check(trailer.position.distanceTo(start)>.5,'trailer did not follow tractor')
 if(farmId==='tractor_trailer_modern'){
  const curve=setInterval(()=>bot._client.write('player_input',{inputs:{forward:true,left:true}}),50);await wait(3000);clearInterval(curve);bot._client.write('player_input',{inputs:{}});await wait(700)
  check(trailer.position.distanceTo(tractor.position)<7.5,'trailer separated from tractor while turning')
 }
 bot.chat('/vehicle save');await wait(1000);pass()
}
bot.once('spawn',()=>run().catch(e=>fail(e.stack||e.message)))
