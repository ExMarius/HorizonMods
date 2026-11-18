// Offline protocol client: checks spawn, mounting, movement and cosmetic hand lifecycle, not visual fidelity.
const mineflayer = require('mineflayer')
const bot = mineflayer.createBot({ host: '127.0.0.1', port: 25565, username: 'SmokeBot', version: '1.21.4', auth: 'offline' })
let done = false
let spawned = false
let driving = false
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
  console.log('Offline player created Go-Kart, mounted, drove, and observed hands appear and disappear.')
  bot.quit()
}
bot.on('error', e => fail(e.message))
bot.on('kicked', reason => fail('kicked: ' + String(reason).slice(0, 300)))
bot.on('end', () => { if (!done) fail('connection ended') })
bot.once('spawn', () => {
  setTimeout(() => bot.chat('/fill ~-8 ~-1 ~-8 ~8 ~-1 ~8 stone'), 1500)
  setTimeout(() => bot.chat('/fill ~-8 ~ ~-8 ~8 ~4 ~8 air'), 2500)
  setTimeout(() => { bot.chat('/hvehicle spawn go_kart'); spawned = true }, 4500)
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
  if (bot.vehicle && displays.length >= 20) {
    if (!driving) {
      driving = true
      const start = bot.vehicle.position.clone()
      const hands = entities.filter(e => e.name === 'block_display')
      if (hands.length !== 4) return fail('expected four cosmetic hand segments, got ' + hands.length)
      const input = setInterval(() => bot._client.write('player_input', { inputs: { forward: true } }), 50)
      setTimeout(() => {
        clearInterval(input)
        bot._client.write('player_input', { inputs: {} })
        if (!bot.vehicle) return fail('player dismounted during movement')
        const distance = Math.hypot(start.x - bot.vehicle.position.x, start.z - bot.vehicle.position.z)
        if (distance < .3) return fail('vehicle did not move: ' + distance)
        bot._client.write('player_input', { inputs: { shift: true } })
        setTimeout(() => {
          bot._client.write('player_input', { inputs: {} })
          const remaining = Object.values(bot.entities).filter(e => e.name === 'block_display').length
          if (bot.vehicle) return fail('player did not dismount')
          if (remaining !== 0) return fail('cosmetic hands remained after dismount: ' + remaining)
          success()
        }, 2500)
      }, 4000)
    }
    return
  }
  if (target && displays.length >= 20) {
    try { bot.activateEntity(target) } catch (e) { fail(e.message) }
  }
}, 1000)
