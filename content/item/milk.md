---
title: Milk
description: A bucket of milk filled from a cow, used to craft cake; it cannot be drunk.
type: item
categories: [Items, Tools]
---

**Milk** is a [[Bucket|bucket]] filled from a [[Cow|cow]].

## Obtaining

Using an empty [[Bucket|bucket]] on a [[Cow|cow]] fills it with milk.
<!-- src: EntityCow.java:38 interact -->

## Usage

### Crafting ingredient

{{used in|Milk}}

Crafting a [[Cake|cake]] leaves the milk buckets in the crafting grid, empty.
<!-- src: SlotCrafting.java:41-:42 puts back an item's container item;
     Item.java:353 gives milk the empty bucket as its container -->

### Pouring

Milk used on a block within 5 blocks is poured away, and leaves an empty
[[Bucket|bucket]]. Nothing is placed.
<!-- src: ItemBucket.java:28 the 5-block trace; :51 returns an empty bucket
     when isFull is -1 (Item.java:353), before any block is placed -->

Milk cannot be drunk.
<!-- src: ItemBucket.java:12 onItemRightClick is milk's only use; it heals
     nothing -->

## Data values

- Item ID: {{id|Milk}}
- Translation key: `item.milk`
