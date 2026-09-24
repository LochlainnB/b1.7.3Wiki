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
- **Pumpkin**: can be worn in the helmet slot, and gives no armour points; only
  armour pieces count towards the total. `src: SlotArmor.java:22 isItemValid;
  InventoryPlayer.java:290 getTotalArmorValue counts only ItemArmor` (armour)
- **Damage#Armour**: does not say how armour is worn. Each of the four slots
  takes only its own piece, plus a pumpkin in the top slot; they run helmet,
  chestplate, leggings, boots from top to bottom. Armour cannot be put on by
  right-clicking: ItemArmor has no `onItemRightClick`.
  `src: ContainerPlayer.java:28; SlotArmor.java:19` (armour)
- **Fire**: Obtaining could say a server operator's `give` is the only way to
  hold fire as an item. `src: minecraft_server ConsoleCommandHandler.java:133;
  minecraft_server Block.java:646-647` (armour; checked against source when
  merging)
- **Minecart with Furnace**: each coal or charcoal adds 1200 fuel. While
  pushing, fuel falls by 1 one tick in four, so one coal lasts about 4800 ticks
  on average. `src: EntityMinecart.java:778-783 interact (tests the item id
  only, so charcoal works); :485-486 onUpdate` (ores)
- **Wool / Dye**: the dye-and-wool recipe takes white wool only (damage 0), so
  coloured wool cannot be re-dyed by crafting. `src: RecipesDyes.java:6` (ores)
- **Dye**: dyeing a sheep that is sheared, or already that colour, does nothing
  and uses no dye. `src: ItemDye.java:84 saddleEntity` (ores)
- **World Generation#Plants**: tall grass and dead bush patches fall from their
  random y through air and leaves to the ground before placing. Flower, rose,
  mushroom and cactus patches do not, and place only when their y lands within
  3 of a surface they grow on. `src: WorldGenTallGrass.java:16,
  WorldGenDeadBush.java:14, WorldGenFlowers.java:13, WorldGenCactus.java:7`
  (biomes)
- **Cactus / World Generation**: each cactus patch makes 10 attempts within 7
  blocks in x and z and 3 in y of a random y from 0 to 127.
  `src: ChunkProviderGenerate.java:567; WorldGenCactus.java:7` (biomes)
- **World Generation#Population / #Trees**: population reads one biome per
  chunk, at block (x+16, z+16), and applies its tree and plant counts to the
  whole populated area, so trees can appear in Plains, Desert or Tundra columns
  near a border. `src: ChunkProviderGenerate.java:314` (biomes)
- **Grass, Leaves**: grass, tall grass and oak leaves take their colour from
  the temperature and rainfall at the block, not from the biome; spruce and
  birch leaves have fixed colours. `src: BlockGrass.java:23 colorMultiplier;
  BlockTallGrass.java:32; BlockLeaves.java:26-:33` (biomes)
- **Overworld or Light**: the daytime sky colour comes from a temperature noise
  read at the player's position, through the same function in every Overworld
  biome; it is not the biome's own temperature. `src: World.java:1030-:1031;
  WorldChunkManager.java:31 getTemperature; BiomeGenBase.java:123
  getSkyColorByTemp` (biomes)

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
- **Mining#Drops**: the Rock row of the material table leaves out Lapis Lazuli
  Block, which is `Material.rock` and needs a pickaxe like the rest.
  `src: Block.java:614` (ores; checked against source when merging)
- **World Generation#The noise fields**: "Rainforest and Swampland carry the
  most extreme terrain, Tundra and Desert the least" is wrong twice. Relief
  scales with `1 − (1 − r)^4`, r = rainfall × temperature. Swampland's r is 0.5
  to 0.7, so 0.94 to 0.99, below Forest (r up to 0.97) and Seasonal Forest (up
  to 0.9); Rainforest alone is the most. Savanna (r below 0.2) shares the least
  with Tundra and Desert. The biome pages already say this, so the hub
  contradicts them until fixed. `src: ChunkProviderGenerate.java:229-:236;
  BiomeGenBase.java:100` (biomes; checked against source when merging)
- **World Generation#Biomes**: the lookup rounds temperature and rainfall down
  to steps of 1/63 before the table applies. Tundra's "temperature < 0.1" is
  below 7/63, about 0.111, and Taiga and Tundra columns can read up to 0.508;
  the ice and snow tests use the unrounded value, so a thin band at those
  biomes' warm edge has no sea ice or low snow. `src: BiomeGenBase.java:94-:97;
  ChunkProviderGenerate.java:82, :596` (biomes; checked against source when
  merging)
- **"Map colour" label** (data, not a page): BiomeGenBase's `color` is set but
  never read in either source tree, so "Map colour" in each biome's infobox and
  in `tools/seed.mjs` implies an in-game use it does not have. Each biome page
  carries a src comment saying so. `src: BiomeGenBase.java:89 setColor`
  (biomes; checked against source when merging)

## Unsettled

- **Slime#Behaviour** `<!-- check: -->`: a size-2 slime's reach is 1.2 between
  positions, and a player's position is 1.62 above its feet, so it may hurt a
  level player only mid-jump. Needs testing in game. (hostile-mobs)
