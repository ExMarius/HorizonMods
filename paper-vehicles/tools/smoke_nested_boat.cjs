// Protocol-only experiment: root armor stand -> boat -> player, plus a display.
// It cannot validate vanilla client prediction, rendering, camera or smoothness.
const mineflayer = require('mineflayer')
const bot = mineflayer.createBot({host:'127.0.0.1', port:25565, username:'SmokeBot', version:'1.21.4', auth:'offline'})
const passengers = new Map()
let done = false
const timer = setTimeout(() => finish('timeout'), 30000)
function finish(error) {
  if (done) return
  done = true; clearTimeout(timer)
  if (error) { console.error('Nested boat experiment failed: ' + error); process.exitCode = 1 }
  else console.log('Protocol experiment: armor stand carries boat and display; player rides boat; root move packet observed. Not a visual test.')
  bot.quit()
}
bot._client.on('packet', (data, meta) => { if (meta.name === 'set_passengers') passengers.set(data.entityId, data.passengers) })
bot.on('error', e => finish(e.message))
bot.on('kicked', reason => finish('kicked: ' + String(reason)))
bot.on('end', () => { if (!done) finish('connection ended') })
bot.once('spawn', () => {
  setTimeout(() => bot.chat('/summon minecraft:armor_stand ~ ~ ~3 {Tags:["hv_nested_test"],Invisible:1b,Marker:1b,NoGravity:1b,Passengers:[{id:"minecraft:oak_boat",Tags:["hv_nested_boat"],NoGravity:1b},{id:"minecraft:item_display",Tags:["hv_nested_display"]}]}'), 1500)
  setTimeout(() => bot.chat('/ride SmokeBot mount @e[type=minecraft:oak_boat,tag=hv_nested_boat,limit=1]'), 3500)
  setTimeout(() => {
    const entities = Object.values(bot.entities)
    const boat = entities.find(e => e.name === 'oak_boat' && (passengers.get(e.id) || []).includes(bot.entity.id))
    const root = boat && entities.find(e => e.name === 'armor_stand' && (passengers.get(e.id) || []).includes(boat.id))
    const display = root && entities.find(e => e.name === 'item_display' && (passengers.get(root.id) || []).includes(e.id))
    if (!root || !boat || !display) return finish('missing experiment entities')
    const riders = passengers.get(root.id) || []
    if (!riders.includes(boat.id) || !riders.includes(display.id)) return finish('root passenger list incomplete: ' + riders)
    if (!(passengers.get(boat.id) || []).includes(bot.entity.id)) return finish('player not mounted on nested boat')
    const before = root.position.clone()
    bot.chat('/execute as @e[type=minecraft:armor_stand,tag=hv_nested_test,limit=1] at @s run tp @s ~3 ~ ~')
    setTimeout(() => {
      if (!bot.entities[root.id] || bot.entities[root.id].position.distanceTo(before) < 2) return finish('root movement not observed')
      if (!(passengers.get(root.id) || []).includes(boat.id) || !(passengers.get(boat.id) || []).includes(bot.entity.id)) return finish('passenger chain broken')
      bot.chat('/ride SmokeBot dismount')
      setTimeout(() => finish(), 1000)
    }, 2500)
  }, 6000)
})
