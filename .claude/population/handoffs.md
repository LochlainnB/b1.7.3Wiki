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
- **Saddle**: hitting a pig with a saddle saddles it, as using it does.
  `src: ItemSaddle.java:20 hitEntity` (passive-mobs)
- **Torch, Redstone Dust**: both need a full cube beneath, which glass, slabs,
  stairs, leaves and TNT are not; a torch can also stand on a fence.
  `src: BlockTorch.java:27-:41; BlockRedstoneWire.java:42; World.java:1644
  isBlockNormalCube` (building-blocks)
- **Note Block**: glass under a note block gives instrument 3, rock 1, wood 4.
  `src: TileEntityNote.java:31-:48` (building-blocks)
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

## Hub or data problems

- **Monster Spawner**: with six of its mob nearby, the spawner does not just end
  the round; it also resets its delay to 200–799 ticks.
  `src: TileEntityMobSpawner.java:57-58` (hostile-mobs; checked against source
  when merging)
- **Achievements**: the Monster Hunter "Earned by" column leaves out the
  Monster, which is EntityMob itself, exactly what the kill test checks.
  `src: EntityPlayer.java:797` (entities)
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
