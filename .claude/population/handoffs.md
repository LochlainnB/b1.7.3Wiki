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
- **Music Disc**: a creeper killed by a skeleton's arrow drops "13" or "cat" at
  even odds. `src: EntityCreeper.java:81; Item.java:378` (hostile-mobs)
- **Fire**: Obtaining could say a server operator's `give` is the only way to
  hold fire as an item. `src: minecraft_server ConsoleCommandHandler.java:133;
  minecraft_server Block.java:646-647` (armour; checked against source when
  merging)
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
- **Saddle**: hitting a pig with a saddle saddles it, as using it does.
  `src: ItemSaddle.java:20 hitEntity` (passive-mobs)
- **Torch, Redstone Dust**: both need a full cube beneath, which glass, slabs,
  stairs, leaves and TNT are not; a torch can also stand on a fence.
  `src: BlockTorch.java:27-:41; BlockRedstoneWire.java:42; World.java:1644
  isBlockNormalCube` (building-blocks)
- **Note Block**: glass under a note block gives instrument 3, rock 1, wood 4.
  `src: TileEntityNote.java:31-:48` (building-blocks)
- **Obsidian**: its "a piston cannot push it" can link
  [[Piston#Pushing]], which now lists every block that stops a piston.
  `src: BlockPistonBase.java:248 canPushBlock` (redstone)
- **Crafting#The grid**: closing either grid, the inventory's 2×2 or the
  table's 3×3, drops whatever is left in it. `src: ContainerWorkbench.java:43
  onCraftGuiClosed; ContainerPlayer.java:48` (utility-blocks)
- **Crafting**: a block ingredient matches any of its subtypes, so any colour of
  wool works; Bed and Painting say so for their own recipes.
  `src: CraftingManager.java:115 new ItemStack(block, 1, -1);
  ShapedRecipes.java:62` (utility-blocks)
- **Painting**: a fishing bobber breaks a painting, which drops as an item.
  `src: EntityFish.java:225; EntityPainting.java:204` (farming-and-food)
- **Nether#Light and weather**: could add that a map's marker spins in the
  Nether, and that a Nether map shows a fixed brown and grey pattern; Map says
  so. `src: MapData.java:92; ItemMap.java:50, :82-:94` (paper-and-instruments)
- **Bed#Spawn point** (optional): a compass keeps pointing to the world spawn,
  not the bed. `src: TextureCompassFX.java:53; World.java:2286 getSpawnPoint`
  (paper-and-instruments)
- **Skeleton**: holds a bow and never drops it; Bow says so.
  `src: EntitySkeleton.java:88 defaultHeldItem; :67 dropFewItems drops only
  arrows and bones` (mob-drops)
- **Wolf**: any hit makes a sitting wolf stand, even a 0-damage snowball.
  `src: EntityWolf.java:255 setWolfSitting(false)` (fluids-and-cold)
- **Snowball#Throwing (and its description), Egg, Fishing Rod#Hooking**: a hit
  that deals 0 damage does nothing to a player: no knockback, and a bobber
  does not hook one. It still hooks and knocks back mobs. Player says so.
  `src: EntityPlayer.java:380 returns false on 0 damage, before
  EntityLiving.attackEntityFrom; EntityFish.java:224 hooks only when that
  returns true` (entities; checked against source when merging)
- **Achievements**: the Monster Hunter row could name and link [[Monster]]; Mob
  Spawning now links it. `src: EntityMob.java:20;
  EntityPlayer.java:797` (entities)
- **Ghast#Fireballs**: Fireball is now written. Cut the section to one line and
  `{{main|Fireball}}`; Ghast keeps when and how often it fires. (entity
  restructure; ready since the entities group)
- **Weather#Lightning**: Lightning Bolt is now written. Keep when and where
  lightning strikes, and cut the strike list and the extra flashes to one line
  and `{{main|Lightning Bolt}}`. (entity restructure; ready since the entities
  group)

## Hub or data problems

- **Monster Spawner**: with six of its mob nearby, the spawner does not just end
  the round; it also resets its delay to 200–799 ticks.
  `src: TileEntityMobSpawner.java:57-58` (hostile-mobs; checked against source
  when merging)
- **Damage#Catching fire and Weather#Lightning**: "Standing in fire sets the
  entity alight for 300 ticks, and lightning does the same" and "5 damage and
  300 ticks alight" are wrong for the player. A player must stand in fire 20
  ticks before catching alight, and a strike never lights a player: it adds 1
  to a count that rests at −20. `src: EntityPlayer.java:50 fireResistance 20;
  Entity.java:525-:531, :1087` (entities; checked against source when merging)
- **Weather#Lightning and Fire#Starting a fire**: "on Normal and Hard" holds for
  a bolt's first flash only. Each of its one to three later flashes sets fire
  to the struck space on any difficulty. `src: EntityLightningBolt.java:16
  guards the first flash alone; :51-:57 have no difficulty test` (entities;
  checked against source when merging)
- **Achievements**: the Monster Hunter "Earned by" column leaves out the
  Monster, which is EntityMob itself, exactly what the kill test checks.
  `src: EntityPlayer.java:797` (entities)
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
- **Mining#Breaking a block**: "one divided by that, rounded up" is a tick short
  wherever the per-tick strength is not an exact binary fraction, because the
  running total is a float. Stone by hand takes 151 ticks, not the table's 150;
  obsidian 301, not 300 (Obsidian and Diamond Pickaxe's "15 seconds" is off by
  the same tick); cobweb by hand 401. Tool times on stone (23, 12, 8, 6, 4) and
  a sword on cobweb (8) are exact. `src: PlayerControllerSP.java:9 float
  curBlockDamage, :72 adds Block.java:331 blockStrength each tick`
  (mob-drops; simulated in float arithmetic when merging, and it agrees)
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

- **data/recipes.json, dye and wool** (data, not a page): the dye-and-wool
  recipes write their wool as `{"block":35}`, the same form as the bed's and
  painting's any-colour wool, but the dye recipe takes white wool only. Nothing
  renders wrong today; data/ just cannot say the difference.
  `src: RecipesDyes.java:6 (damage 0); CraftingManager.java:115 (-1);
  ShapelessRecipes.java:32` (mob-drops)
- **Ink Sac `{{id}}` and infobox** (tools, not a page): `{{id|Ink Sac}}`
  renders `351` and its infobox has no damage-value row, because its damage is
  0, so its id looks the same as the whole Dye item's. Bone Meal and Cocoa
  Beans show `351:15` and `351:3`. (mob-drops)

## Unsettled

None. The four open questions were tested in game and written up on 2026-09-25.
