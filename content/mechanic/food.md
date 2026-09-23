---
title: Food
description: How eating works — food heals the moment it is used, what each food restores, and eating cake.
type: mechanic
categories: [Game mechanics]
aliases: [Eating, Foods]
---

**Food** is anything a player eats to restore health.

## Eating

Using a food eats one at once. It restores its value in health, up to the
maximum of 20; see [[Damage#Health]].
<!-- src: ItemFood.java:14 onItemRightClick, which takes one from the stack and
     calls heal with no delay; EntityLiving.java:296 heal caps at 20 -->

Food is eaten at full health as well, and restores nothing.
<!-- src: ItemFood.java:14 onItemRightClick has no health test -->

[[Mushroom Stew|Mushroom stew]] leaves an empty [[Bowl|bowl]] behind.
<!-- src: ItemSoup.java:8 onItemRightClick returns Item.bowlEmpty -->

## Foods

{{list|food}}

A [[Cake|cake]] is eaten where it stands, one slice at a time, by using or
hitting it. Each slice restores 3, and a cake has 6. A slice is eaten only when
the player is below full health.
<!-- src: BlockCake.java:67 blockActivated and :72 onBlockClicked call :76 eatCakeSlice,
     which tests health < 20, heals 3 and removes the cake at the sixth -->

Raw porkchops and raw fish [[Smelting|cook]] in a furnace.

## Wolves

A tamed [[Wolf|wolf]] below full health eats a raw or cooked porkchop from a
player's hand, and restores 3 from either.
<!-- src: EntityWolf.java:353-:361, which heals by porkRaw's amount whichever
     chop is fed; Item.java:337-:338 mark both chops as the wolf's -->
