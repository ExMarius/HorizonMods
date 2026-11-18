// Offline protocol test: boat seat, steering and pack delivery. Not a visual test.
const mineflayer = require('mineflayer')
const bot = mineflayer.createBot({ host: '127.0.0.1', port: 25565, username: 'SmokeBot', version: '1.21.4', auth: 'offline' })
let done = false, spawned = false, driving = false, dismounted = false, packs = 0, packsAtSpawn = 0
const passengers = new Map()
const timeout = setTimeout(() => fail('timed out'), 50000)
bot._client.on('packet', (data, meta) => {
  if (meta.name === 'add_resource_pack') packs++
  if (meta.name === 'set_passengers') passengers.set(data.entityId, data.passengers)
})
function fail(message) {
  if (done) return
  done = true; clearTimeout(timeout); console.error('Offline player smoke failed: ' + message)
  bot.quit(); process.exitCode = 1
}
function success() {
  if (done) return
  done = true; clearTimeout(timeout)
  console.log('Boat mounted; model displays are attached to its carrier; movement tested; pack not resent on spawn.')
  bot.quit()
}
bot.on('error', e => fail(e.message))
bot.on('kicked', reason => fail('kicked: ' + String(reason).slice(0, 300)))
bot.on('end', () => { if (!done) fail('connection ended') })
bot.once('spawn', () => {
  setTimeout(() => bot.chat('/fill ~-8 ~-1 ~-8 ~8 ~-1 ~8 stone'), 1500)
  setTimeout(() => bot.chat('/fill ~-8 ~ ~-8 ~8 ~4 ~8 air'), 2500)
  setTimeout(() => {
    packsAtSpawn = packs
    if (packsAtSpawn !== 1) return fail('expected one join pack, got ' + packsAtSpawn)
    bot.chat('/hvehicle spawn go_kart'); spawned = true
  }, 4500)
})
bot.on('messagestr', text => {
  if (text.includes('stopped riding')) dismounted = true
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
      if (bot.vehicle.name !== 'oak_boat') return fail('seat is not an oak boat: ' + bot.vehicle.name)
      const riders = passengers.get(bot.vehicle.id) || []
      // Paper 1.21.4 promotes the player ahead of the non-player carrier.
      // This documents the observed protocol order, not a vanilla-client physics test.
      if (riders[0] !== bot.entity.id) return fail('unexpected boat passenger order: ' + riders.join(','))
      const carrierId = riders.find(id => id !== bot.entity.id)
      const attached = passengers.get(carrierId) || []
      const displayIds = new Set(displays.map(e => e.id))
      const attachedDisplays = attached.filter(id => displayIds.has(id)).length
      if (attachedDisplays < 30) return fail('model is not attached to boat carrier; attached displays: ' + attachedDisplays)
      if (packs !== packsAtSpawn) return fail('resource pack sent again on spawn')
      if (entities.some(e => e.name === 'block_display')) return fail('unwanted cosmetic hands exist')
      const startYaw = bot.vehicle.yaw
      const steerOnly = setInterval(() => bot._client.write('player_input', { inputs: { left: true } }), 50)
      setTimeout(() => {
        clearInterval(steerOnly)
        if (!bot.vehicle) return fail('dismounted while steering')
        if (Math.abs(bot.vehicle.yaw - startYaw) > .08) return fail('boat rotates on A without driving')
        const start = bot.vehicle.position.clone(), yaw = bot.vehicle.yaw
        let maxSeparation = 0
        const input = setInterval(() => {
          bot._client.write('player_input', { inputs: { forward: true, left: true } })
          if (bot.vehicle && target) {
            const distance = Math.hypot(target.position.x - bot.vehicle.position.x, target.position.z - bot.vehicle.position.z)
            maxSeparation = Math.max(maxSeparation, distance)
          }
        }, 50)
        setTimeout(() => {
          clearInterval(input)
          bot._client.write('player_input', { inputs: {} })
          if (!bot.vehicle) return fail('player dismounted during movement')
          const distance = Math.hypot(start.x - bot.vehicle.position.x, start.z - bot.vehicle.position.z)
          if (distance < .3) return fail('vehicle did not move: ' + distance)
          if (maxSeparation > 1.2) return fail('boat separated from kart during driving: ' + maxSeparation)
          if (Math.abs(bot.vehicle.yaw - yaw) < .02) return fail('boat did not follow kart turn')
          if (packs !== packsAtSpawn) return fail('resource pack sent after spawn')
          // Command dismount, since Mineflayer does not reproduce all vanilla sneak input.
          bot.chat('/ride SmokeBot dismount')
          setTimeout(() => { if (!dismounted) return fail('server did not confirm dismount'); success() }, 2500)
        }, 4000)
      }, 2000)
    }
    return
  }
  if (target && displays.length >= 20) {
    try { bot.activateEntity(target) } catch (e) { fail(e.message) }
  }
}, 1000)
