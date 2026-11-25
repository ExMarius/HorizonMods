// Server protocol smoke only: cannot verify client rendering or terrain protection plugins.
const mineflayer=require('mineflayer')
const bot=mineflayer.createBot({host:'127.0.0.1',port:25568,username:'HorizonBot',version:'1.21.4',auth:'offline'})
const wait=ms=>new Promise(r=>setTimeout(r,ms)); let done=false, messages=[], updates=0
const timer=setTimeout(()=>fail('timeout: '+messages.slice(-15).join(' | ')),110000)
function fail(s){if(done)return;done=true;clearTimeout(timer);console.error('FAIL: '+s);bot.quit();process.exitCode=1}
function test(ok,msg){if(!ok)throw Error(msg+'; messages='+messages.slice(-15).join(' | '))}
bot.on('error',e=>fail(e.message));bot.on('kicked',r=>fail('kicked '+r));bot.on('end',()=>{if(!done)fail('disconnected')})
bot.on('messagestr',s=>messages.push(s))
bot.on('blockUpdate',(a,b)=>{if(a&&b&&b.name==='farmland'&&a.name!==b.name)updates++})
async function run(){
 await wait(2000);bot.chat('/fill ~-15 ~-1 ~-15 ~15 ~-1 ~15 dirt');await wait(1200)
 bot.chat('/fill ~-15 ~ ~-15 ~15 ~5 ~15 air');await wait(1200)
 bot.chat('/tp @s ~ ~ ~ 0 0');await wait(1000);bot.chat('/vehicle spawn utb_650');await wait(2500)
 const tractor=Object.values(bot.entities).find(e=>e.name==='interaction');test(tractor,'no tractor')
 bot.chat('/tp @s ~ ~ ~-3');await wait(1000);bot.chat('/vehicle spawn disc_gd32');await wait(2500)
 const harrow=Object.values(bot.entities).find(e=>e.name==='interaction'&&e.id!==tractor.id);test(harrow,'no harrow')
 bot.chat('/vehicle cupleaza_disc');await wait(1500);test(messages.some(s=>s.includes('Grapă cuplată')),'not coupled')
 bot.chat('/tp @s ~ ~ ~3');await wait(800);bot.activateEntity(tractor);await wait(2000);test(bot.vehicle,'not mounted')
 bot.chat('/vehicle disc');await wait(1500);test(messages.some(s=>s.includes('Grapa coboară')),'not lowered')
 const start=tractor.position.clone();const send=setInterval(()=>bot._client.write('player_input',{inputs:{forward:true}}),50)
 await wait(5000);clearInterval(send);bot._client.write('player_input',{inputs:{}});await wait(1200)
 test(tractor.position.distanceTo(start)>.3,'tractor did not move');test(updates===0,'unexpected terrain changes')
 bot.chat('/vehicle disc');await wait(800);test(messages.some(s=>s.includes('Grapa se ridică')),'not raised')
 bot.chat('/vehicle save');await wait(1000);done=true;clearTimeout(timer)
 console.log('Harrow spawned, coupled, commanded and towed without soil changes; client render not tested.');bot.quit()
}
bot.once('spawn',()=>run().catch(e=>fail(e.stack||e.message)))
