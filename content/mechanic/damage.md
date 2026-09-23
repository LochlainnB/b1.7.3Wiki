---
title: Damage
description: Every source of damage, the ten-tick invulnerability window, how armour reduces damage and how difficulty scales it.
type: mechanic
categories: [Game mechanics]
aliases: [Health, Armor, Armour, Fall Damage, Knockback]
---

**Damage** is a whole number of health points taken off an entity.

## Health

A player has 20 health, drawn as ten hearts, and dies at 0. Healing never takes
a player above 20.
<!-- src: EntityPlayer.java:47 health = 20; EntityLiving.java:296 heal caps at 20 -->

Health regenerates only on Peaceful, at 1 point per second.
<!-- src: EntityPlayer.java:173 onLivingUpdate; the guard reads
     `ticksExisted % 20 * 12 == 0`, which Java groups as
     ((ticksExisted % 20) * 12) == 0 and so passes every 20th tick -->

Eating restores the food's own healing value at any difficulty.
<!-- src: ItemFood.java:14 onItemRightClick calls heal(healAmount) -->

## Environmental damage

| Source | Damage | Attempted |
|---|---|---|
| Falling | ceil(distance − 3) | on landing |
| Suffocating inside a solid block | 1 | every [[Game Tick\|tick]] |
| Touching a [[Cactus\|cactus]] | 1 | every tick |
| Standing in [[Fire\|fire]] or [[Lava\|lava]] | 1 | every tick |
| Standing in lava | 4 | every tick |
| Burning | 1 | every 20 ticks |
| Drowning | 2 | 320 ticks after the head goes under, then every 20 |
| Below Y = −64 | 4 | every tick |
| Struck by lightning | 5 | on the strike |
<!-- src: EntityLiving.java:440 fall, :114 suffocation, :134 drowning, :786 kill;
     BlockCactus.java:88; Entity.java:523 dealFireDamage(1) covers fire and lava
     blocks alike, :248 burning, :273 setOnFireFromLava, :1086 lightning -->

Repeating sources land far less often than they are attempted, because the
invulnerability window discards most of the attempts.

Fall distance is reset by entering [[Water|water]] and by holding a
[[Ladder|ladder]], so neither leads to fall damage.
<!-- src: Entity.java:231 water; EntityLiving.java:517 the isOnLadder branch -->

A player riding a [[Minecart|minecart]], [[Boat|boat]] or [[Pig|pig]] takes the
vehicle's fall damage, because a vehicle passes its fall on to its rider.
<!-- src: Entity.java:571 fall forwards to riddenByEntity -->

## Catching fire

Standing in fire sets the entity alight for 300 ticks, and lightning does the
same. Lava sets it alight for 600.
<!-- src: Entity.java:525 the tick after contact begins takes fire from the
     -fireResistance it was pinned at up to 0, and 0 is then set to 300;
     :274 lava; :1089 lightning -->

The count holds while the entity stands in the flame, and starts falling only
once it leaves.
<!-- src: the ++fire at Entity.java:525 cancels the --fire at :251 each tick -->

An entity standing in water or in rain does not catch, and getting wet while
alight puts it out. It takes the contact damage either way.
<!-- src: Entity.java:521 isWet gates the catch alone, :534 extinguishes;
     dealFireDamage at :523 sits outside that test -->

Fire, lava and lightning do no damage to a [[Ghast|ghast]] or a
[[Pig Zombie\|pig zombie]]. Both still catch alight, and burn off four times as
fast.
<!-- src: EntityGhast.java:17 and EntityPigZombie.java:15 set isImmuneToFire;
     Entity.java:563 dealFireDamage and :272 setOnFireFromLava test it, :242
     drains the counter by 4 a tick; the ++fire at :525 does not test it -->

## Weapons

| Tool | Wood | Gold | Stone | Iron | Diamond |
|---|---|---|---|---|---|
| Sword | 4 | 4 | 6 | 8 | 10 |
| Axe | 3 | 3 | 4 | 5 | 6 |
| Pickaxe | 2 | 2 | 3 | 4 | 5 |
| Shovel | 1 | 1 | 2 | 3 | 4 |

Gold deals the damage of wood. Every other item, and a bare hand, deals 1.
<!-- src: ItemSword.java:10 weaponDamage = 4 + material * 2; ItemTool.java:16
     damageVsEntity = base + material, base 3 axe / 2 pickaxe / 1 spade;
     EnumToolMaterial.java GOLD carries damageVsEntity 0, the same as WOOD;
     Item.java:205 getDamageVsEntity returns 1 -->

Attacking while moving downwards adds 1 damage.
<!-- src: EntityPlayer.java:492 ++var2 when motionY < 0 -->

A sword loses 1 durability per hit and a tool loses 2. Anything else loses none.
<!-- src: ItemSword.java:17, ItemTool.java:29 hitEntity; Item.hitEntity
     returns false without damaging the stack -->

## Mob attacks

| Mob | Damage |
|---|---|
| [[Giant]] | 50 |
| [[Zombie]], [[Pig Zombie\|pig zombie]] | 5 |
| [[Slime]] | its size, 2 or 4 |
| [[Spider]] | 2 |
| [[Wolf]] | 2, or 4 when tamed |
<!-- src: EntityMob.java:4 attackStrength 2, EntityZombie.java:8 and
     EntityPigZombie.java:14 set 5, EntityGiantZombie.java:8 sets 50;
     EntitySlime.java:116; EntityWolf.java:316 -->

A melee mob strikes once every 20 ticks and only within 2 blocks. A slime has
no such cooldown: it damages on contact, limited only by the invulnerability
window, and the smallest slime deals nothing at all.
<!-- src: EntityMob.java:49 attackEntity sets attackTime = 20;
     EntitySlime.java:116 onCollideWithPlayer, gated on size > 1 -->

A [[Skeleton|skeleton]] shoots an [[Arrow|arrow]] every 30 ticks instead of
striking. Arrows deal a flat 4 whether shot by a skeleton, a [[Bow|bow]] or a
[[Dispenser|dispenser]].
<!-- src: EntitySkeleton.java:34 attackEntity, :46 attackTime = 30;
     EntityArrow.java:163 -->

A [[Creeper|creeper]] and a [[Ghast|ghast]] deal no direct damage; both explode.
A ghast's fireball hits for 0 and leaves the damage to its blast.
<!-- src: EntityCreeper.java:101; EntityFireball.java:124 -->

[[Snowball|Snowballs]], [[Egg|eggs]] and a fishing bobber deal 0 damage. They
still knock their target back.
<!-- src: EntitySnowball.java:153, EntityEgg.java:153, EntityFish.java:225 -->

## Explosions

{{main|Explosion}}

An explosion damages every entity within twice its size in blocks, by up to
16 × size + 1 at the centre, and less with distance and cover.
<!-- src: Explosion.java:77 doubles the size before the entity pass, :100 -->

## The invulnerability window

Taking damage makes an entity invulnerable for 10 ticks. A source that fires
during that window is ignored unless it exceeds the damage that opened the
window, and then only the difference is applied.
<!-- src: EntityLiving.java:307 attackEntityFrom; heartsLife is set to 20 and
     the fresh-damage branch runs again once it has fallen to 10 -->

Hits of 2 and then 5 inside one window therefore cost 5 health, not 7.

A hit taken this way does not restart the window, which keeps running from the
hit that opened it. It also passes without knockback, hurt sound or hurt flash,
and kills silently if it kills.
<!-- src: EntityLiving.java:317 the branch leaves heartsLife alone and clears
     the flag gating the animation at :335, the knockback at :346 and both
     sounds at :353 and :358 -->

## Armour

Armour points depend on the slot alone, never on the material.

| Piece | Points |
|---|---|
| Chestplate | 8 |
| Leggings | 6 |
| Helmet | 3 |
| Boots | 3 |
<!-- src: ItemArmor.java:4 damageReduceAmountArray {3, 8, 6, 3} indexed by
     armorType 0 helmet, 1 chestplate, 2 leggings, 3 boots -->

Each point removes 4% of the damage, so a full set of any material removes 80%.
The reduced figure is rounded down, and the remainder is carried into the next
hit rather than lost.
<!-- src: EntityPlayer.java:439 damageEntity: damage * (25 - points) / 25,
     with damage * (25 - points) % 25 kept in damageRemainder -->

Armour reduces every kind of damage, drowning, suffocation, fire and falling
included.

Damaged armour protects less. The point total is scaled by the durability left
across all worn pieces together, down to a floor of 1 point.
<!-- src: InventoryPlayer.java:284 getTotalArmorValue returns
     (points - 1) * remaining / max + 1 -->

Every worn piece loses durability equal to the damage **before** reduction,
whatever the source. A 25-damage blast costs each piece 25 durability.
<!-- src: EntityPlayer.java:442 damageArmor is passed the incoming figure;
     InventoryPlayer.java:308 passes it to every armour slot -->

Materials differ only in durability:

| Piece | Leather | Gold | Chain | Iron | Diamond |
|---|---|---|---|---|---|
| Helmet | 33 | 66 | 66 | 132 | 264 |
| Chestplate | 48 | 96 | 96 | 192 | 384 |
| Leggings | 45 | 90 | 90 | 180 | 360 |
| Boots | 39 | 78 | 78 | 156 | 312 |
<!-- src: ItemArmor.java:5 maxDamageArray {11, 16, 15, 13} * 3 << armorLevel;
     Item.java:332 gives gold armorLevel 1, the same as chain -->

## Difficulty

Damage a player takes from a zombie, pig zombie, spider, giant, skeleton arrow
or creeper explosion is scaled by the difficulty setting.

| Difficulty | Damage taken |
|---|---|
| Peaceful | 0 |
| Easy | damage / 3 + 1 |
| Normal | damage |
| Hard | damage × 3 / 2 |
<!-- src: EntityPlayer.java:366, applied when the attacker is an EntityMob or
     an EntityArrow; integer division throughout -->

Slimes, wolves and ghasts fall outside the scaling, and so do TNT, bed and
fireball explosions. An arrow from a dispenser falls outside it too, having no
shooter to test.
<!-- src: EntitySlime, EntityWolf and EntityGhast do not extend EntityMob;
     Explosion passes its exploder, null for EntityTNTPrimed.java:68,
     BlockBed.java:45 and EntityFireball.java:127; EntityArrow.java:163 passes
     its owner, left null by the constructor BlockDispenser.java:107 uses -->

Mobs deal and take unscaled damage among themselves.

## Knockback

An attacker knocks its target back by a fixed amount, the same for a punch as
for a diamond sword. Damage with no attacker behind it knocks nothing back.
<!-- src: EntityLiving.java:392 knockBack ignores the damage argument and uses
     0.4 horizontally and 0.4 upwards -->

## Death

An entity that reaches 0 health drops its items at once and disappears 20 ticks
later.
<!-- src: EntityLiving.java:357 calls onDeath the moment health reaches zero,
     :418 dropFewItems; :157 removes the entity once deathTime passes 20 -->

## Other entities

Minecarts and boats hold a damage counter instead of health. Each hit adds ten
times the damage and the counter falls by 1 per tick; the vehicle breaks above
40.
<!-- src: EntityMinecart.java:78 and :169, EntityBoat.java:67 and :126 -->

A dropped item has 5 health and is destroyed by fire and explosions. A
[[Painting|painting]] is destroyed by any damage at all.
<!-- src: EntityItem.java:8 and :87, EntityPainting.java:204 -->
