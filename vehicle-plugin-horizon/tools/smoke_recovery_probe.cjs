// Two offline test players; no graphical client validation.
const mineflayer=require('mineflayer');
const opts={host:'127.0.0.1',port:25578,version:'1.21.4',auth:'offline'};
let bot;
const owner=mineflayer.createBot({...opts,username:'RecoveryOwnerBot'});
const timer=setTimeout(()=>{console.error('join timeout');owner.quit();bot?.quit();process.exitCode=1},55000);
function failed(e){clearTimeout(timer);console.error(e);process.exitCode=1;owner.quit();bot?.quit()}
owner.on('error',failed);owner.on('kicked',failed);
owner.once('spawn',()=>{
 if(process.env.RECOVERY_RESTART_CHECK){setTimeout(()=>{clearTimeout(timer);owner.quit()},4000);return;}
 bot=mineflayer.createBot({...opts,username:'RecoveryProbeBot'});
 bot.on('error',failed);bot.on('kicked',failed);
 bot.once('spawn',()=>{
   setTimeout(()=>bot.chat('/recoverytest spawn'),32000);
   setTimeout(()=>bot.chat('/recoverytest open'),33000);
   setTimeout(()=>bot.chat('/recoverytest close'),34000);
   setTimeout(()=>bot.chat('/recoverytest remove'),35000);
   setTimeout(()=>{clearTimeout(timer);bot.quit()},37000);
 });
 bot.on('messagestr', message => {
   if(message.includes('RECOVERY_OWNER_CAN_QUIT')) owner.quit();
   if(message.includes('RECOVERY_DRIVE_START')) {
     let turning=false;
     const drive=setInterval(()=>bot._client.write('player_input',{inputs:{forward:true,left:turning}}),50);
     setTimeout(()=>{turning=true},1300);
     setTimeout(()=>{clearInterval(drive);bot._client.write('player_input',{inputs:{}})},2500);
   }
 });
});
