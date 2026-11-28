// Protocol-only test of 3 distinct riders and shared movement; no visual assertion.
const mineflayer=require('mineflayer')
const wait=ms=>new Promise(r=>setTimeout(r,ms))
const create=name=>mineflayer.createBot({host:'127.0.0.1',port:25568,username:name,version:'1.21.4',auth:'offline'})
const driver=create('HorizonBot'), guests=[create('UtbGuest1'),create('UtbGuest2')], bots=[driver,...guests]
let done=false;const messages=[]
const timer=setTimeout(()=>fail('timeout; '+messages.slice(-15).join(' | ')),110000)
function fail(s){if(done)return;done=true;clearTimeout(timer);console.error('FAIL: '+s);bots.forEach(b=>b.quit());process.exitCode=1}
function pass(){if(done)return;done=true;clearTimeout(timer);console.log('Three independent UTB seats mounted and moved together; visual alignment not tested.');bots.forEach(b=>b.quit())}
function check(c,m){if(!c)throw new Error(m+'; '+messages.slice(-12).join(' | '))}
for(const b of bots){b.on('error',e=>fail(b.username+': '+e.message));b.on('kicked',r=>fail(b.username+' kicked: '+String(r)));b.on('end',()=>{if(!done)fail(b.username+' disconnected')});b.on('messagestr',s=>messages.push(b.username+': '+s))}
const ready=b=>new Promise(resolve=>b.once('spawn',resolve))
async function run(){
 await Promise.all(bots.map(ready));await wait(1500)
 driver.chat('/fill ~-12 ~-1 ~-12 ~12 ~-1 ~12 stone');await wait(1300)
 driver.chat('/fill ~-12 ~ ~-12 ~12 ~5 ~12 air');await wait(1300)
 driver.chat('/tp @s ~ ~ ~ 0 0');await wait(700)
 driver.chat('/tp UtbGuest1 @s');await wait(400);driver.chat('/tp UtbGuest2 @s');await wait(700)
 driver.chat('/vehicle spawn utb_650');await wait(2200)
 const tractor=Object.values(driver.entities).find(e=>e.name==='interaction');check(tractor,'missing tractor interaction')
 for(const b of bots){
  const target=Object.values(b.entities).find(e=>e.name==='interaction');check(target,b.username+' missing interaction')
  b.activateEntity(target);await wait(1500);check(b.vehicle,b.username+' did not mount')
 }
 check(new Set(bots.map(b=>b.vehicle.id)).size===3,'riders not in three distinct seats')
 const start=tractor.position.clone()
 const inputs=setInterval(()=>driver._client.write('player_input',{inputs:{forward:true}}),50)
 await wait(5000);clearInterval(inputs);driver._client.write('player_input',{inputs:{}});await wait(1000)
 check(tractor.position.distanceTo(start)>.3,'tractor did not move')
 for(const b of bots)check(b.vehicle,'rider left their seat while moving')
 driver.chat('/op UtbGuest1');await wait(500);driver.chat('/op UtbGuest2');await wait(500)
 // Operator-only /ride exercises the server-side dismount path; Mineflayer shift is unreliable here.
 for(const b of bots){b.chat('/ride @s dismount');await wait(1500)}
 driver.chat('/vehicle save');await wait(1000);pass()
}
run().catch(e=>fail(e.stack||e.message))
