// Two offline protocol clients: player-first boat ordering and nested mount.
// Mineflayer does not implement vanilla boat prediction, camera or rendering.
const mineflayer = require('mineflayer')
const options = username => ({ host:'127.0.0.1', port:25565, username, version:'1.21.4', auth:'offline' })
const pilot = mineflayer.createBot(options('SeatPilot'))
const driver = mineflayer.createBot(options('SmokeBot'))
const passengers = new Map()
let pilotReady = false, driverReady = false, started = false, done = false, leftSeen = false
const timer = setTimeout(() => finish('timeout'), 35000)
function finish(error) {
  if (done) return
  done = true; clearTimeout(timer)
  if (error) { console.error('Second-seat protocol test failed: ' + error); process.exitCode = 1 }
  else console.log('Two player passengers ordered; second player remains mounted while root moves; Paper reports left input. Not a vanilla client or visual test.')
  pilot.quit(); driver.quit()
}
for (const bot of [pilot, driver]) {
  bot.on('error', e => finish(e.message))
  bot.on('kicked', reason => finish('kicked: ' + String(reason)))
  bot.on('end', () => { if (!done) finish('unexpected disconnect') })
}
driver.on('messagestr', text => { if (text.includes('Input test:') && text.includes('left=true')) leftSeen = true })
driver._client.on('packet', (data, meta) => { if (meta.name === 'set_passengers') passengers.set(data.entityId, data.passengers) })
pilot.once('spawn', () => { pilotReady = true; begin() })
driver.once('spawn', () => { driverReady = true; begin() })
function begin() {
  if (!pilotReady || !driverReady || started) return
  started = true
  setTimeout(() => driver.chat('/summon minecraft:armor_stand ~ ~ ~3 {Tags:["hv_second_root"],Invisible:1b,Marker:1b,NoGravity:1b,Passengers:[{id:"minecraft:oak_boat",Tags:["hv_second_boat"],NoGravity:1b}]}'), 1500)
  setTimeout(() => driver.chat('/ride SeatPilot mount @e[type=minecraft:oak_boat,tag=hv_second_boat,limit=1]'), 3500)
  setTimeout(() => driver.chat('/ride SmokeBot mount @e[type=minecraft:oak_boat,tag=hv_second_boat,limit=1]'), 5000)
  setTimeout(() => {
    const entities = Object.values(driver.entities)
    const boat = entities.find(e => e.name === 'oak_boat' && (passengers.get(e.id) || []).includes(driver.entity.id))
    if (!boat) return finish('second player did not mount boat')
    const first = driver.players.SeatPilot && driver.players.SeatPilot.entity
    if (!first) return finish('first player is not tracked')
    const riders = passengers.get(boat.id) || []
    if (riders[0] !== first.id || riders[1] !== driver.entity.id) return finish('unexpected passenger order ' + riders)
    const root = entities.find(e => e.name === 'armor_stand' && (passengers.get(e.id) || []).includes(boat.id))
    if (!root) return finish('boat not mounted on root')
    const before = root.position.clone()
    // Verify Paper exposes the second passenger's input to the plugin. This
    // does not simulate a vanilla client's boat prediction or rendering.
    const inputTimer = setInterval(() => driver._client.write('player_input', { inputs: { left: true } }), 50)
    setTimeout(() => driver.chat('/hvehicle input'), 700)
    driver.chat('/execute as @e[type=minecraft:armor_stand,tag=hv_second_root,limit=1] at @s run tp @s ~3 ~ ~')
    setTimeout(() => {
      clearInterval(inputTimer)
      if (!leftSeen) return finish('Paper did not report second passenger left input')
      const now = driver.entities[root.id]
      if (!now || now.position.distanceTo(before) < 2) return finish('root movement not observed')
      const after = passengers.get(boat.id) || []
      if (after[0] !== first.id || after[1] !== driver.entity.id) return finish('riders changed during movement')
      driver._client.write('player_input', { inputs: {} })
      driver.chat('/ride SmokeBot dismount')
      setTimeout(() => { driver.chat('/ride SeatPilot dismount'); setTimeout(() => finish(), 700) }, 700)
    }, 2500)
  }, 7500)
}
