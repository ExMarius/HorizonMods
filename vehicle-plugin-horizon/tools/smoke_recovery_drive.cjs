const mineflayer=require('mineflayer');
const bot=mineflayer.createBot({host:'127.0.0.1',port:25579,version:'1.21.4',auth:'offline',username:'RecoveryDriveBot'});
let timer,inputs={};
const deadline=setTimeout(()=>{console.error('drive probe timed out');bot.quit();process.exitCode=1},45000);
bot.on('error',error=>{console.error(error);process.exitCode=1;clearTimeout(deadline)});
bot.on('messagestr',message=>{
 if(message.includes('RECOVERY_DRIVE_FORWARD')) {
  inputs={forward:true};timer=setInterval(()=>bot._client.write('player_input',{inputs}),50);
 }
 if(message.includes('RECOVERY_DRIVE_TURN')) inputs={forward:true,left:true};
 if(message.includes('RECOVERY_DRIVE_DONE')) {clearInterval(timer);clearTimeout(deadline);bot.quit()}
});
