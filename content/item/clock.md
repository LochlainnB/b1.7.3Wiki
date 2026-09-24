---
title: Clock
description: An item crafted from gold and redstone, whose face shows the time of day.
type: item
categories: [Items, Tools]
---

**Clock** is an item whose face shows the time of day.

## Obtaining

### Crafting

{{crafting|Clock}}

## Usage

### Telling the time

A clock's face turns with the sky, showing the sun at noon and the moon at
midnight.
<!-- src: TextureWatchFX.java:36 turns the dial by getCelestialAngle, which is
     0 at time 6000 and 0.5 at 18000 (WorldProvider.java:42
     calculateCelestialAngle). misc/dial.png has the sun in its upper half and
     the moon in its lower, and the icon's face is its upper half. -->

In the [[Nether#Light and weather|Nether]], the face spins at random.
<!-- src: TextureWatchFX.java:38 -->

## Data values

- Item ID: {{id|Clock}}
- Translation key: `item.clock`
