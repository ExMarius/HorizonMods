// Offline protocol client: checks spawn, display entities and mounting, not visuals or driving.
const mineflayer = require('mineflayer')
const bot = mineflayer.createBot({ host: '127.0.0.1', port: 25565, username: 'SmokeBot', version: '1.21.4', auth: 'offline' })
let done = false
let spawned = false
const timeout = setTimeout(() => fail('timed out'), 45000)
function fail(message) {
  if (done) return
  done = true; clearTimeout(timeout)
  console.error('Offline player smoke failed: ' + message)
  bot.quit(); process.exitCode = 1
}
function success() {
  if (done) return
  done = true; clearTimeout(timeout)
  console.log('Offline player created Go-Kart, saw display entities and mounted the seat.')
  bot.quit()
}
bot.on('error', e => fail(e.message))
bot.on('kicked', reason => fail('kicked: ' + String(reason).slice(0, 300)))
bot.on('end', () => { if (!done) fail('connection ended') })
bot.once('spawn', () => {
  setTimeout(() => { bot.chat('/hvehicle spawn go_kart'); spawned = true }, 2500)
})
bot.on('messagestr', text => {
  if (text.includes('Nu am putut crea Go-Kart') || text.includes('Nu este loc liber')) fail(text)
})
const interval = setInterval(() => {
  if (done) { clearInterval(interval); return }
  if (!spawned) return
  const entities = Object.values(bot.entities)
  const displays = entities.filter(e => e.name === 'item_display')
  const target = entities.find(e => e.name === 'interaction')
  if (bot.vehicle && displays.length >= 20) return success()
  if (target && displays.length >= 20) {
    try { bot.activateEntity(target) } catch (e) { fail(e.message) }
  }
}, 1000)
