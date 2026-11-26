// Only connects a disposable offline test player; does not assert visuals.
const mineflayer=require('mineflayer');
const bot=mineflayer.createBot({host:'127.0.0.1',port:25578,username:'RecoveryProbeBot',version:'1.21.4',auth:'offline'});
const timer=setTimeout(()=>{console.error('join timeout');bot.quit();process.exitCode=1},30000);
bot.once('spawn',()=>{
  setTimeout(()=>bot.chat('/recoverytest spawn'),5500);
  setTimeout(()=>bot.chat('/recoverytest open'),6200);
  setTimeout(()=>bot.chat('/recoverytest close'),6900);
  setTimeout(()=>bot.chat('/recoverytest remove'),7600);
  setTimeout(()=>{clearTimeout(timer);bot.quit()},8500);
});
bot.on('error',e=>{clearTimeout(timer);console.error(e);process.exitCode=1});
bot.on('kicked',r=>{clearTimeout(timer);console.error('kicked',r);process.exitCode=1});
