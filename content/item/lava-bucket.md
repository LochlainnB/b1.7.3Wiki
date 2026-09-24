---
title: Lava bucket
description: A bucket holding a lava source, which it places where it is used, and the longest-burning furnace fuel.
type: item
categories: [Items, Tools]
---

A **lava bucket** is a [[Bucket|bucket]] holding one [[Lava|lava]] source.

## Obtaining

An empty [[Bucket#Filling|bucket]] used on a [[Lava|lava]] source fills with
it.
<!-- src: ItemBucket.java:46 -->

## Usage

A lava bucket [[Bucket#Emptying|places]] a [[Lava|lava]] source, and becomes
an empty bucket.
<!-- src: ItemBucket.java:87, :90 -->

### Fuel

In a [[Furnace|furnace]], a lava bucket [[Smelting#Fuel|burns]] for 20,000
ticks, enough to smelt 100 items. The bucket is used up with the lava.
<!-- src: TileEntityFurnace.java:196 getItemBurnTime; :118 takes the whole
     item from the fuel slot and returns no container -->

## Data values

- Item ID: {{id|Lava bucket}}
- Translation key: `item.bucketLava`
