// Only connects a disposable offline test player; does not assert visuals.
const mineflayer=require('mineflayer');
const bot=mineflayer.createBot({host:'127.0.0.1',port:25578,username:'RecoveryProbeBot',version:'1.21.4',auth:'offline'});
const timer=setTimeout(()=>{console.error('join timeout');bot.quit();process.exitCode=1},55000);
bot.once('spawn',()=>{
  setTimeout(()=>bot.chat('/recoverytest spawn'),32000);
  setTimeout(()=>bot.chat('/recoverytest open'),33000);
  setTimeout(()=>bot.chat('/recoverytest close'),34000);
  setTimeout(()=>bot.chat('/recoverytest remove'),35000);
  setTimeout(()=>{clearTimeout(timer);bot.quit()},37000);
});
bot.on('error',e=>{clearTimeout(timer);console.error(e);process.exitCode=1});
bot.on('kicked',r=>{clearTimeout(timer);console.error('kicked',r);process.exitCode=1});

bot.on('messagestr', message => {
 if(message.includes('RECOVERY_DRIVE_START')) {
   const drive=setInterval(()=>bot._client.write('player_input',{inputs:{forward:true}}),50);
   setTimeout(()=>{clearInterval(drive);bot._client.write('player_input',{inputs:{}})},2500);
 }
});
