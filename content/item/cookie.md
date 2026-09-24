---
title: Cookie
description: A food crafted eight at a time from wheat and cocoa beans, and the only food that stacks.
type: item
categories: [Items, Food]
---

A **cookie** is a [[Food|food]] crafted from [[Wheat|wheat]] and
[[Cocoa Beans|cocoa beans]].

## Obtaining

### Crafting

{{crafting|Cookie}}

## Usage

A cookie is [[Food#Eating|eaten]] to restore 1 health.
<!-- src: Item.java:375 ItemCookie(101, 1, false, 8) -->

Cookies stack to 8. No other food stacks.
<!-- src: ItemCookie.java:5 sets maxStackSize from the fourth argument;
     ItemFood.java:11 sets 1 for every other food -->

## Data values

- Item ID: {{id|Cookie}}
- Translation key: `item.cookie`
