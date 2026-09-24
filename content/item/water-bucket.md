---
title: Water Bucket
description: A bucket holding a water source, which it places where it is used, except in the Nether.
type: item
categories: [Items, Tools]
---

A **water bucket** is a [[Bucket|bucket]] holding one [[Water|water]] source.

## Obtaining

An empty [[Bucket#Filling|bucket]] used on a [[Water|water]] source fills with
it.
<!-- src: ItemBucket.java:41 -->

## Usage

A water bucket [[Bucket#Emptying|places]] a [[Water|water]] source, and becomes
an empty bucket.
<!-- src: ItemBucket.java:87, :90 -->

In the [[Nether#Behaviour|Nether]], the water fizzes away and places nothing.
The bucket empties all the same.
<!-- src: ItemBucket.java:80 -->

## Data values

- Item ID: {{id|Water Bucket}}
- Translation key: `item.bucketWater`
