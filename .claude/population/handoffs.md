# Hand-offs

The running list from README step 4: each merged group's **For other pages**,
**Hub or data problems** and **Red links left**, worked through in one pass
after the last group. Tick an entry off by deleting it once it is on its page.

## Red links left

- `[[Achievements]]` — Wooden Pickaxe, Stone Pickaxe, Wooden Hoe, Wooden Sword
  (tools).

## For other pages

- **Achievements** (new page): an achievement is awarded only once its parent
  is unlocked. Crafting awards the crafting table, wooden pickaxe, furnace,
  wooden hoe, bread, cake, stone pickaxe and wooden sword achievements.
  `src: EntityPlayerSP.java:180 addStat; AchievementList.java:33-48;
  SlotCrafting.java:19-35` (tools)
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

## Hub or data problems

- **Mining#Tool wear** says a sword's two points per block halve its blocks.
  The counts are 30, 66, 126, 781 and 17 for wood, stone, iron, diamond and
  gold; iron and gold are not exact halves. `src: ItemSword.java:22;
  ItemStack.java:127` (tools)
- **Mining#Tool wear** says shears "last 239 blocks". Shearing a sheep draws on
  the same 239 uses. `src: EntitySheep.java:49` (tools)
