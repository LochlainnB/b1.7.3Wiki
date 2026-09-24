# Hand-offs

The running list from README step 4: each merged group's **For other pages**,
**Hub or data problems** and **Red links left**, worked through in one pass
after the last group. Tick an entry off by deleting it once it is on its page.

## Red links left

None yet.

## For other pages

- **Pig Zombie**: holds a golden sword and never drops it; drops cooked
  porkchops. `src: EntityPigZombie.java:89 getHeldItem, :94, :85 getDropItemId`
  (tools)
- **Sheep**: each shearing costs the shears 1 durability.
  `src: EntitySheep.java:49` (tools)
- **Light** (the burning row): by day a zombie or skeleton catches fire with
  chance `(brightness − 0.4) × 2 / 30` a tick, 1 in 25 in full daylight.
  `src: EntityZombie.java:14, EntitySkeleton.java:26` (hostile-mobs)
- **Light**: a pig zombie runs the same burning check and takes no damage from
  it. `src: EntityPigZombie extends EntityZombie; EntityPigZombie.java:15`
  (hostile-mobs)
- **Arrow**: an arrow a player shot, or a dispenser fired, can be picked up; a
  skeleton's cannot. `src: EntityArrow.java:33, :259; BlockDispenser.java:109
  doesArrowBelongToPlayer = true` (hostile-mobs; the dispenser half corrected by
  redstone and checked against source when merging)
- **Music Disc**: a creeper killed by a skeleton's arrow drops "13" or "cat" at
  even odds. `src: EntityCreeper.java:81; Item.java:378` (hostile-mobs)
- **Feather, String, Gunpowder, Slimeball, Arrow, Bone, Cooked Porkchop**: each
  mob that drops one drops 0–2. `src: EntityLiving.java:424`, plus zombie
  feather `EntityZombie.java:34`, spider string `EntitySpider.java:70`, creeper
  and ghast gunpowder `EntityCreeper.java:129, EntityGhast.java:143`, size-1
  slime slimeball `EntitySlime.java:130`, skeleton arrow and bone
  `EntitySkeleton.java:67`, pig zombie cooked porkchop `EntityPigZombie.java:85`
  (hostile-mobs)
- **Damage#Armour**: does not say how armour is worn. Each of the four slots
  takes only its own piece, plus a pumpkin in the top slot; they run helmet,
  chestplate, leggings, boots from top to bottom. Armour cannot be put on by
  right-clicking: ItemArmor has no `onItemRightClick`.
  `src: ContainerPlayer.java:28; SlotArmor.java:19` (armour)
- **Fire**: Obtaining could say a server operator's `give` is the only way to
  hold fire as an item. `src: minecraft_server ConsoleCommandHandler.java:133;
  minecraft_server Block.java:646-647` (armour; checked against source when
  merging)
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
- **World Generation#Population**: the cactus row's 10 are patches of 10
  attempts each, within 7 blocks in x and z and 3 in y; Cactus says so.
  `src: ChunkProviderGenerate.java:567; WorldGenCactus.java:7` (biomes)
- **World Generation#Population / #Trees**: population reads one biome per
  chunk, at block (x+16, z+16), and applies its tree and plant counts to the
  whole populated area, so trees can appear in Plains, Desert or Tundra columns
  near a border. `src: ChunkProviderGenerate.java:314` (biomes)
- **Overworld or Light**: the daytime sky colour comes from a temperature noise
  read at the player's position, through the same function in every Overworld
  biome; it is not the biome's own temperature. `src: World.java:1030-:1031;
  WorldChunkManager.java:31 getTemperature; BiomeGenBase.java:123
  getSkyColorByTemp` (biomes)
- **Egg**: a chicken lays an egg every 6000 to 11999 ticks (5 to 10 minutes).
  `src: EntityChicken.java:43 onLivingUpdate; :17 and :46` (passive-mobs)
- **Bone Meal / Dye**: a dye used on an unsheared sheep dyes its fleece and is
  used up; bone meal dyes it white. `src: ItemDye.java:80 saddleEntity;
  BlockCloth.java:21 getBlockFromDye` (passive-mobs)
- **Saddle**: hitting a pig with a saddle saddles it, as using it does.
  `src: ItemSaddle.java:20 hitEntity` (passive-mobs)
- **Bone Meal**: used on grass, spends one and makes 128 tries nearby; each
  plant is tall grass 9 in 10, otherwise a flower 2 in 3 or a rose 1 in 3.
  `src: ItemDye.java:42-:70` (terrain)
- **Bone Meal**: used on a sapling, it is spent even when the tree has no room,
  and the sapling stays. `src: ItemDye.java:24-:28; BlockSapling.java:51-:53`
  (plants)
- **Torch, Redstone Dust**: both need a full cube beneath, which glass, slabs,
  stairs, leaves and TNT are not; a torch can also stand on a fence.
  `src: BlockTorch.java:27-:41; BlockRedstoneWire.java:42; World.java:1644
  isBlockNormalCube` (building-blocks)
- **Note Block**: glass under a note block gives instrument 3, rock 1, wood 4.
  `src: TileEntityNote.java:31-:48` (building-blocks)
- **Obsidian**: its "a piston cannot push it" can link
  [[Piston#Pushing]], which now lists every block that stops a piston.
  `src: BlockPistonBase.java:248 canPushBlock` (redstone)
- **Dropped Item**: an item that touches a cactus is destroyed: the cactus
  deals 1 a tick and an item has 5 health. `src: BlockCactus.java:87
  onEntityCollidedWithBlock; Entity.java:514; EntityItem.java:87, :8` (plants)
- **Crafting#The grid**: closing either grid, the inventory's 2×2 or the
  table's 3×3, drops whatever is left in it. `src: ContainerWorkbench.java:43
  onCraftGuiClosed; ContainerPlayer.java:48` (utility-blocks)
- **Crafting**: a block ingredient matches any of its subtypes, so any colour of
  wool works; Bed and Painting say so for their own recipes.
  `src: CraftingManager.java:115 new ItemStack(block, 1, -1);
  ShapedRecipes.java:62` (utility-blocks)
- **No hub yet, perhaps Player**: the chest, furnace and crafting table screens
  close when the player is more than 8 blocks away or the block is gone.
  `src: EntityPlayer.java:81; TileEntityChest.java:84, TileEntityFurnace.java:204,
  ContainerWorkbench.java:56` (utility-blocks)
- **Bone Meal**: used on crops, it is spent even when they are fully grown.
  `src: ItemDye.java:33-:38, no stage test` (farming-and-food)
- **Fireball** (with Ghast#Fireballs): a fishing bobber sends a fireball off the
  way the player looks, as a hit or an arrow does. `src: EntityFish.java:225
  attackEntityFrom(angler, 0); EntityFireball.java:202` (farming-and-food)
- **Painting**: a fishing bobber breaks a painting, which drops as an item.
  `src: EntityFish.java:225; EntityPainting.java:204` (farming-and-food)
- **Player**: a player with the username Notch drops an apple on death, in
  singleplayer and on a server; Apple says so. `src: EntityPlayer.java:223;
  minecraft_server EntityPlayer.java:203` (farming-and-food)
- **Wolf**: any hit makes a sitting wolf stand, even a 0-damage snowball.
  `src: EntityWolf.java:255 setWolfSitting(false)` (fluids-and-cold)
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
- **Mob Spawning#Passive mobs**: never says animals spawn on every difficulty,
  Peaceful included. `src: Minecraft.java:1164
  setAllowedMobSpawns(difficulty > 0, true)` (passive-mobs)
- **Mob Spawning#The spawn cycle**: "a solid block below" is really
  `isBlockNormalCube`: solid, not translucent, rendered as a full block. Glass,
  single slabs, stairs, fences, leaves, ice, cactus and TNT all fail it, so no
  mob spawns naturally on them. Monster spawners skip the test.
  `src: SpawnerAnimals.java:156-:157; World.java:1644; Material.java:87,
  :118-:131 setIsTranslucent` (building-blocks and fluids-and-cold)
- **Light#What light affects**: "Hostile mobs except slimes and ghasts
  wandering | prefer darker spaces" is wrong for the giant, which prefers
  brighter spaces. `src: EntityGiantZombie.java:14 getBlockPathWeight =
  brightness − 0.5` (hostile-mobs)
- **Light#What light affects**: the "Grass dying" row names only "water, ice or
  an opaque block above". The test is light opacity above 2, which also covers
  slabs, stairs, farmland and lava. `src: BlockGrass.java:32; BlockStep.java:16,
  BlockStairs.java:15, BlockFarmland.java:11` (terrain)
- **Light#What light affects** ("Snow melting | above 11") and **Game
  Tick#Random ticks** ("Snow | melts above block light 11"): only the snow
  layer melts. A snow block reads the block light stored in its own space,
  which is always 0 for an opaque block, so it never melts.
  `src: BlockSnowBlock.java:19; Block.java:152; MetadataChunkBlock.java:85`
  (fluids-and-cold; checked against source when merging)
- **Game Tick#Random ticks**, Leaves row: "decay when a nearby break has flagged
  them and no log is within 4 blocks" is wrong twice. The test is a chain of at
  most 4 face-to-face steps through leaves to any wood, not a distance, so wood
  2 blocks away across air does not keep them. And placed leaves start flagged,
  not only leaves near a break. Leaves has it right.
  `src: BlockLeaves.java:81-:144 updateTick; ItemLeaves.java:10
  getPlacedBlockMetadata returns var1 | 8` (plants; face-to-face checked
  against source when merging)
- **Game Tick#Random ticks**, Farmland row: "turns to dirt when dry" is wrong
  for farmland with crops on it, which never does. Only crops in the space
  directly above count. Farmland has it right. `src: BlockFarmland.java:41,
  :57 isCropsNearby, radius 0` (farming-and-food; checked against source when
  merging)
- **Monster Spawner**: with six of its mob nearby, the spawner does not just end
  the round; it also resets its delay to 200–799 ticks.
  `src: TileEntityMobSpawner.java:57-58` (hostile-mobs; checked against source
  when merging)
- **Damage#Mob attacks**: "A melee mob strikes once every 20 ticks and only
  within 2 blocks" sits under a table that lists the wolf, and is wrong for it:
  a wolf bites within 1.5 blocks, with no cooldown, so only the target's
  10-tick window spaces its bites. `src: EntityWolf.java:314, :315 sets an
  attackTime nothing reads; against EntityMob.java:50` (passive-mobs; checked
  against source when merging)
- **Explosion#Entities and Damage#Other entities**: both say a painting is
  destroyed by a blast. It drops itself as an item, spawned after the blast has
  chosen the entities it hits, so the item survives. `src: EntityPainting.java:204;
  Explosion.java:84` (utility-blocks; checked against source when merging)
- **Mining#Drops**: the Rock row of the material table leaves out Lapis Lazuli
  Block and the stone Pressure Plate, both `Material.rock`, and its "the stone
  slabs and stairs" should say every slab, the wooden one included.
  `src: Block.java:614, :662; BlockStep.java:10; Material.java:114;
  ItemPickaxe.java:18` (ores, redstone and building-blocks; lapis checked
  against source when merging)
- **Mining#What blocks actually give**: "Three blocks give nothing at all" leaves
  out the Dead Bush. The table also has no row for tall grass and ferns (seeds 1
  in 8, otherwise nothing, shears included) or for sugar cane (the item, 338).
  Mining also says broken ice "turns into flowing Water"; it is a water source,
  block 8 at level 0. `src: BlockDeadBush.java:20; BlockTallGrass.java:39;
  BlockReed.java:70; BlockIce.java:24` (plants and fluids-and-cold)
- **Mining#What each tool is effective against**: gives Wooden Stairs as the
  axe's gap, but Fence and every other wooden block but planks, wood,
  bookshelf and chest are missing too: crafting table, doors, trapdoor,
  jukebox, note block, sign, wooden pressure plate, locked chest.
  `src: ItemAxe.java:11` (building-blocks)
- **Smelting#Fuel**: the wooden block list leaves out the Locked Chest, which is
  `Material.wood` and burns for 300 ticks. `src: BlockLockedChest.java:7;
  TileEntityFurnace.java:190` (building-blocks and utility-blocks)
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
- **World Generation#Lakes**: "Dirt directly under the liquid becomes grass" is
  wrong. The loop runs over the four air layers and turns the dirt under the
  lake's open part, its banks, to grass; dirt under the liquid is untouched.
  `src: WorldGenLakes.java:77-:81` (terrain; checked against source when
  merging)
- **World Generation#Trees**: says every tree turns the block under its trunk to
  dirt. The big tree does not; it only tests for grass or dirt below.
  `src: WorldGenBigTree.java:305 func_519_e`; the other four set it at
  `WorldGenTrees.java:43, WorldGenForest.java:43, WorldGenTaiga1.java:45,
  WorldGenTaiga2.java:44` (terrain)
- **World Generation#The Nether**: "plus 10 more anywhere" for glowstone is
  wrong. WorldGenGlowStone2 is identical to WorldGenGlowStone1, so the second
  ten also hang from ceilings; they differ only in starting y, 0–127 against
  4–123. `src: ChunkProviderHell.java:332, :339` (terrain; checked against
  source when merging)
- **World Generation#Population**: "Sand and gravel do not fall while a chunk is
  being populated" is wrong. `fallInstantly` is on during population, so sand
  that is updated then drops straight to its landing spot with no entity; only
  sand nothing notifies stays hanging. Falling Sand already says so.
  `src: ChunkProviderGenerate.java:311, :602; WorldGenLiquids.java:56;
  BlockSand.java:27-:39` (terrain; checked against source when merging)
- **"Map colour" label** (data, not a page): BiomeGenBase's `color` is set but
  never read in either source tree, so "Map colour" in each biome's infobox and
  in `tools/seed.mjs` implies an in-game use it does not have. Each biome page
  carries a src comment saying so. `src: BiomeGenBase.java:89 setColor`
  (biomes; checked against source when merging)
- **data/blocks.json, block 44** (data, not a page): `variants` has no damage 3,
  the cobblestone slab, so its recipe output draws the stone slab icon (the
  game draws cobblestone, texture 16) and no `{{id}}` resolves to 44:3. Stone
  Slab types `44:3` by hand until this is fixed. `src: BlockStep.java:31;
  ItemSlab.java:10 getIconFromDamage` (building-blocks; checked against source
  when merging)
- **data/sprites.json, `music-disc`** (data, not a page): index 241 is the cat
  disc's icon (`setIconCoord(1, 15)`); the "13" disc, at (0, 15), has no sprite,
  because both ids share the name Music Disc. The Dungeon loot table and the
  Music Disc infobox both show the cat disc. `src: Item.java:378-:379`
  (utility-blocks; checked against source when merging)

## Unsettled

- **Slime#Behaviour** `<!-- check: -->`: a size-2 slime's reach is 1.2 between
  positions, and a player's position is 1.62 above its feet, so it may hurt a
  level player only mid-jump. Needs testing in game. (hostile-mobs) That 1.62
  is the singleplayer client's; on a server the player's position is at its
  feet (minecraft_server EntityPlayerMP.java:41 yOffset 0), so the answer
  likely differs by mode, as it does for Wolf. Giant's src comment ("within
  1.17 horizontally") is singleplayer-only for the same reason; its prose holds
  in both. (found merging passive-mobs)
- **Ice#Behaviour**: a player who stops walking on ice slides about 1.7 blocks,
  against 0.26 on other ground, worked out from the friction code rather than
  measured; the working is in the src comment. Worth confirming in game.
  (fluids-and-cold)
- **Minecart#Movement** `<!-- check: -->`: do minecarts push each other? The
  collision code returns early when `(dx·other.motionZ + dz·other.prevPosX)²
  > 5`, reading a position where a speed belongs, which would stop carts on a
  north–south track away from x=0 from pushing at all. Both source trees have
  it, so it is in the shipped game, not the decompile. The same early return
  may stop a furnace minecart pushing other carts. Needs testing in game.
  `src: EntityMinecart.java:673-:684; minecraft_server EntityMinecart.java:622`
  (transport; checked against source when merging)
- **Boat#Movement** `<!-- check: -->`: the boat's top speed with a rider. It is
  capped at 0.4 blocks a tick on each axis, but the rider adds only a fifth of
  their motion a tick against 1% loss, which may settle below the cap.
  `src: EntityBoat.java:195, :200-:215, :260` (transport)
