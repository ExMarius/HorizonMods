const mineflayer=require('mineflayer');
const opts={host:'127.0.0.1',port:25578,version:'1.21.4',auth:'offline'};
let driver;
const owner=mineflayer.createBot({...opts,username:'RecoveryOwnerBot'});
const timer=setTimeout(()=>{console.error('pair test timeout');owner.quit();driver?.quit();process.exitCode=1},35000);
function fail(error){console.error(error);clearTimeout(timer);owner.quit();driver?.quit();process.exitCode=1;}
owner.on('error',fail);owner.on('kicked',fail);
owner.once('spawn',()=>{
 driver=mineflayer.createBot({...opts,username:'RecoveryProbeBot'});
 driver.on('error',fail);driver.on('kicked',fail);
 driver.once('spawn',()=>{
   if(process.env.RECOVERY_PAIR_RESTART) setTimeout(()=>{clearTimeout(timer);owner.quit();driver.quit()},5000);
 });
 driver.on('messagestr',message=>{
   if(!process.env.RECOVERY_PAIR_RESTART && message.includes('RECOVERY_DRIVE_START')) {
     const drive=setInterval(()=>driver._client.write('player_input',{inputs:{forward:true}}),50);
     setTimeout(()=>{clearInterval(drive);driver._client.write('player_input',{inputs:{}})},2500);
   }
   if(!process.env.RECOVERY_PAIR_RESTART && message.includes('RECOVERY_RESTART_NOW')) { clearTimeout(timer);owner.quit();driver.quit(); }
   if(!process.env.RECOVERY_PAIR_RESTART && message.includes('RECOVERY_OWNER_CAN_QUIT')) {
     owner.quit();setTimeout(()=>{clearTimeout(timer);driver.quit()},3500);
   }
 });
});
