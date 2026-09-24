# Hand-offs

The running list from README step 4: each merged group's **For other pages**,
**Hub or data problems** and **Red links left**, worked through in one pass
after the last group. Tick an entry off by deleting it once it is on its page.

## Red links left

None yet.

## For other pages

- **Farmland**: farmland tilled under a solid block reverts to dirt only when a
  neighbouring block changes. `src: BlockFarmland.java:85 onNeighborBlockChange`
  (tools)
- **Pig Zombie**: holds a golden sword and never drops it; drops cooked
  porkchops. `src: EntityPigZombie.java:89 getHeldItem, :94, :85 getDropItemId`
  (tools)
- **Sheep**: each shearing costs the shears 1 durability.
  `src: EntitySheep.java:49` (tools)
- **Seeds / Grass**: hoeing grass drops nothing. Seeds come only from tall grass
  (1 in 8) and crops. `src: ItemHoe.java:10-26; BlockTallGrass.java:40;
  BlockCrops.java:98` (tools)
- **Light** (the burning row): by day a zombie or skeleton catches fire with
  chance `(brightness − 0.4) × 2 / 30` a tick, 1 in 25 in full daylight.
  `src: EntityZombie.java:14, EntitySkeleton.java:26` (hostile-mobs)
- **Light**: a pig zombie runs the same burning check and takes no damage from
  it. `src: EntityPigZombie extends EntityZombie; EntityPigZombie.java:15`
  (hostile-mobs)
- **Arrow**: only an arrow a player shot can be picked up; skeleton and
  dispenser arrows cannot. `src: EntityArrow.java:33, :259` (hostile-mobs)
- **Music Disc**: a creeper killed by a skeleton's arrow drops "13" or "cat" at
  even odds. `src: EntityCreeper.java:81; Item.java:378` (hostile-mobs)
- **Farmland**: each step an entity takes on it turns it to dirt 1 time in 4.
  Spiders never trample it. `src: BlockFarmland.java:50; Entity.java:478;
  EntitySpider.java:15` (hostile-mobs)
- **Feather, String, Gunpowder, Slimeball, Arrow, Bone, Cooked Porkchop**: each
  mob that drops one drops 0–2. `src: EntityLiving.java:424`, plus zombie
  feather `EntityZombie.java:34`, spider string `EntitySpider.java:70`, creeper
  and ghast gunpowder `EntityCreeper.java:129, EntityGhast.java:143`, size-1
  slime slimeball `EntitySlime.java:130`, skeleton arrow and bone
  `EntitySkeleton.java:67`, pig zombie cooked porkchop `EntityPigZombie.java:85`
  (hostile-mobs)

- **Ghast#Fireballs**: once Fireball is written, cut the section to one line
  and `{{main|Fireball}}`. Ghast keeps when and how often it fires. (entity
  restructure, before the entities group)
- **Weather#Lightning**: once Lightning Bolt is written, keep when and where
  lightning strikes, and cut the strike list and the extra flashes to one line
  and `{{main|Lightning Bolt}}`. (entity restructure, before the entities
  group)

## Hub or data problems

- **Mob Spawning#Despawning**: slimes and ghasts never age, so the 1-in-800
  check past 600 ticks never removes them; only the 128-block rule does. Their
  despawn check also runs every tick, not only when they have no path.
  `src: entityAge rises only at EntityLiving.java:690 and EntityMob.java:14;
  EntitySlime.java:68 and EntityGhast.java:31 override updatePlayerActionState`
  (hostile-mobs; checked against source when merging)
- **Mob Spawning#Hostile mobs**: "A slime above the smallest size also needs a
  difficulty above Peaceful" implies size-1 slimes spawn on Peaceful. No slime
  does: Peaceful skips the whole monster category. `src: Minecraft.java:1164;
  SpawnerAnimals.java:48` (hostile-mobs)
- **Mob Spawning**: the Peaceful removal of ghasts is cited as
  `EntityGhast.java:30 onUpdate`; it is at `EntityGhast.java:32`, in
  updatePlayerActionState. (hostile-mobs)
- **Light#What light affects**: "Hostile mobs except slimes and ghasts
  wandering | prefer darker spaces" is wrong for the giant, which prefers
  brighter spaces. `src: EntityGiantZombie.java:14 getBlockPathWeight =
  brightness − 0.5` (hostile-mobs)
- **Monster Spawner**: with six of its mob nearby, the spawner does not just end
  the round; it also resets its delay to 200–799 ticks.
  `src: TileEntityMobSpawner.java:57-58` (hostile-mobs; checked against source
  when merging)

## Unsettled

- **Slime#Behaviour** `<!-- check: -->`: a size-2 slime's reach is 1.2 between
  positions, and a player's position is 1.62 above its feet, so it may hurt a
  level player only mid-jump. Needs testing in game. (hostile-mobs)
