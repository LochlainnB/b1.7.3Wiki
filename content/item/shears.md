---
title: Shears
description: The iron tool that shears sheep and collects leaves and cobweb.
type: item
categories: [Items, Tools]
---

**Shears** are a tool made from [[Iron Ingot|iron ingots]], used to shear
[[Sheep|sheep]].

## Obtaining

### Crafting

{{crafting|Shears}}

## Usage

Shears act on:

- [[Sheep]], which they shear
- [[Leaves]], which they break at a [[Mining#Tools|mining speed]] of 15 and
  collect
- [[Cobweb]], which they break at a mining speed of 15 and
  [[Mining#Drops|harvest]]
- [[Wool]], which they break at a mining speed of 5

<!-- src: EntitySheep.java:36 interact; BlockLeaves.java:164 harvestBlock;
     ItemShears.java:22 getStrVsBlock; ItemShears.java:18 canHarvestBlock -->

Each leaf block, cobweb and sheep sheared costs them 1
[[Durability|durability]]. Breaking any other block costs them nothing.
<!-- src: ItemShears.java:10 onBlockDestroyed damages only on leaves and web;
     EntitySheep.java:49 damageItem(1) per shearing -->

## Data values

- Item ID: {{id|Shears}}
- Translation key: `item.shears`
