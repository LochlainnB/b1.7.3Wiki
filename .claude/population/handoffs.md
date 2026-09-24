# Hand-offs

The running list from README step 4: each merged group's **For other pages**,
**Hub or data problems** and **Red links left**, worked through in one pass
after the last group. Tick an entry off by deleting it once it is on its page.

## Red links left

None yet.

## For other pages

None left.

## Hub or data problems

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
