---
title: Fluid
description: How water and lava flow — sources, levels, how far and how fast each spreads, infinite water, what a flow washes away, and where lava meets water.
type: mechanic
categories: [Game mechanics]
aliases: [Fluids, Liquid, Liquids, Source block, Flowing water, Infinite water]
---

A **fluid** is [[Water|water]] or [[Lava|lava]]: a block that flows out from a
source.

## Levels

Every fluid block has a level. A **source** is level 0, and each block of flow
is one step weaker than the block it came from. Flow stops where the next step
would pass 7.
<!-- src: BlockFlowing.java:21 updateTick; :38 a level of 8 or more on the
     flat is removed -->

| | Water | Lava | Lava in the [[Nether]] |
|---|---|---|---|
| Levels lost per block | 1 | 2 | 1 |
| Blocks of flow from a source, on the flat | 7 | 3 | 7 |
| Ticks per block of spread | 5 | 30 | 30 |

<!-- src: BlockFlowing.java:25 var7, 2 for lava outside isHellWorld;
     BlockFluid.java:187 tickRate -->

Fluid falling straight down stays at full strength, and starts to spread again
from level 1 wherever it lands.
<!-- src: BlockFlowing.java:42-:49 a block under fluid takes 8 plus its level;
     :90 falling fluid spreads sideways at level 1 -->

## Flow

Fluid flows down whenever the block below lets it. Otherwise it spreads
sideways, but only towards the nearest place within 4 blocks where it could flow
down. Where several are equally near it spreads towards each, and where there
is none it spreads in all four directions.
<!-- src: BlockFlowing.java:80 down first; :173 getOptimalFlowDirections and
     :132 calculateFlowCost, searching to a depth of 4 -->

When a source is removed, the flow it fed dries up from the source outwards.
Each block of flowing lava that would weaken holds on 3 updates in 4, so lava
dries up slowly.
<!-- src: BlockFlowing.java:30-:40 each block recomputes from its strongest
     neighbour; :59 the lava hesitation -->

### What stops flow

Solid blocks stop fluid, and so do [[Wooden Door|doors]], [[Sign|signs]],
[[Ladder|ladders]] and [[Sugar cane|sugar cane]]. Fluid flows into every other
block and replaces it:

- plants: [[Flower|flowers]], [[Rose|roses]], [[Sapling|saplings]],
  [[Tall Grass|tall grass]], [[Dead Bush|dead bushes]], [[Mushroom|mushrooms]]
  and [[Crops|crops]];
- [[Torch|torches]], [[Redstone Dust|redstone dust]],
  [[Redstone Torch|redstone torches]], [[Redstone Repeater|repeaters]],
  [[Rail|rails]], [[Lever|levers]] and [[Button|buttons]];
- [[Snow|snow]] layers, [[Fire|fire]] and [[Nether Portal|portal]] blocks.

Water breaks these into their drops. Lava destroys them.
<!-- src: BlockFlowing.java:220 blockBlocksFlow, true for the four named
     blocks and any solid material; the non-solid materials are plants,
     circuits, snow, fire and portal (Material.java:108-:138,
     MaterialLogic.java, MaterialTransparent.java, MaterialPortal.java);
     :116 flowIntoBlock drops the block for water and fizzes for lava -->

## Infinite water

A space of flowing water with two or more water sources beside it becomes a
source, if the block below it is solid. Lava never makes new sources.
<!-- src: BlockFlowing.java:51-:57, for water only. The second branch, water
     below, tests the block's own level, which is never 0 here, so it never
     applies -->

## Lava and water

Lava that has water beside it or above it hardens:

| Lava | Becomes |
|---|---|
| A source | {{sprite\|Obsidian}} |
| Level 1 to 4: the first two blocks of flow | {{sprite\|Cobblestone}} |
| Weaker, or falling | stays lava |

<!-- src: BlockFluid.java:247 checkForHarden, run from onBlockAdded and
     onNeighborBlockChange; the water test covers the four sides and above,
     not below -->

Water below lava does not harden it. Lava can flow into a space of water and
replace it. Water never flows into lava.
<!-- src: BlockFlowing.java:251 liquidCanDisplaceBlock stops water flowing
     into lava, and lets lava flow into water, water not being a solid
     material -->

## Still and flowing blocks

Water and lava each have two blocks: a flowing one, and a still one it becomes
once it stops changing. A still block turns back into flowing when a block
beside it changes.
<!-- src: BlockFlowing.java:14 updateFlow swaps in the still id;
     BlockStationary.java:15 onNeighborBlockChange -->

Still lava takes [[Game Tick#Random ticks|random ticks]], and uses them to set
[[Fire|fire]]. Still water takes none.

## Entities

Water pushes entities in the direction it flows. Lava does not.
<!-- src: Entity.java:585 handleWaterMovement calls
     World.handleMaterialAcceleration; Entity.java:607 handleLavaMovement only
     tests for lava -->

Entities in water can drown, and entities in lava burn; see
[[Damage#Environmental damage]].
