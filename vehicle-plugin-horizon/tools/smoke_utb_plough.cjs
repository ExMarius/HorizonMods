// Protocol-level integration only: exercises attachment, opt-in and tilling, not rendering.
const mineflayer = require('mineflayer')
const bot = mineflayer.createBot({host:'127.0.0.1',port:25568,username:'HorizonBot',version:'1.21.4',auth:'offline'})
const wait = ms => new Promise(r=>setTimeout(r,ms))
let done=false, messages=[], updates=0
const timer=setTimeout(()=>fail('timeout; messages='+messages.slice(-15).join(' | ')),110000)
function fail(s){if(done)return;done=true;clearTimeout(timer);console.error('FAIL: '+s);bot.quit();process.exitCode=1}
function pass(){if(done)return;done=true;clearTimeout(timer);console.log('UTB plough spawned, attached, activated, and tilled soil; visuals not validated.');bot.quit()}
function test(condition,msg){if(!condition)throw new Error(msg+'; messages='+messages.slice(-10).join(' | '))}
bot.on('error',e=>fail(e.message));bot.on('kicked',r=>fail('kicked '+String(r).slice(0,200)));bot.on('end',()=>{if(!done)fail('unexpected disconnect')})
bot.on('messagestr',s=>messages.push(s))
bot.on('blockUpdate',(oldBlock,newBlock)=>{if(oldBlock && newBlock && ['dirt','grass_block','dirt_path'].includes(oldBlock.name) && newBlock.name==='farmland')updates++})
async function run(){
 await wait(2000);bot.chat('/fill ~-15 ~-1 ~-15 ~15 ~-1 ~15 dirt'); await wait(1200)
 bot.chat('/fill ~-15 ~ ~-15 ~15 ~5 ~15 air');await wait(1300)
 bot.chat('/tp @s ~ ~ ~ 0 0');await wait(1000)
 bot.chat('/vehicle spawn utb_650');await wait(2500)
 const tractor=Object.values(bot.entities).find(e=>e.name==='interaction');test(tractor,'no tractor interaction')
 bot.chat('/tp @s ~ ~ ~-3');await wait(1100)
 bot.chat('/vehicle spawn utb_plough');await wait(2500)
 const plough=Object.values(bot.entities).find(e=>e.name==='interaction' && e.id!==tractor.id);test(plough,'no plough interaction')
 bot.setControlState('sneak',true);await wait(600);bot.activateEntity(plough);await wait(1400);bot.setControlState('sneak',false);await wait(500)
 test(messages.some(s=>s.includes('Tragi remorca')),'could not pick up plough')
 bot.chat('/tp @s ~ ~ ~3');await wait(800);bot.activateEntity(tractor);await wait(1600)
 test(messages.some(s=>s.includes('cuplată')),'could not attach plough')
 bot.activateEntity(tractor);await wait(2000);test(bot.vehicle,'could not mount tractor')
 bot.chat('/vehicle plug');await wait(900)
 test(messages.some(s=>s.includes('Plug activat')),'could not activate plough')
 const start=tractor.position.clone()
 const sender=setInterval(()=>bot._client.write('player_input',{inputs:{forward:true}}),50)
 await wait(7500);clearInterval(sender);bot._client.write('player_input',{inputs:{}});await wait(1500)
 test(tractor.position.distanceTo(start)>.3,'tractor failed to move');test(updates>0,'no farmland block update observed')
 bot.chat('/vehicle plug');await wait(600);test(messages.some(s=>s.includes('Plug dezactivat')),'could not deactivate')
 bot.chat('/vehicle save');await wait(1000);pass()
}
bot.once('spawn',()=>run().catch(e=>fail(e.stack||e.message)))
