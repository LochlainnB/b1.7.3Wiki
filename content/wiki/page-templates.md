---
title: Page templates
description: Every template available in page bodies, with examples.
type: wiki
categories: [Wiki]
---

Templates are written `{{name|arg|key=value}}` and may span several lines. A
template alone on a line becomes a block; one inside a sentence stays inline.
To show a template without running it, put it in backticks or a fenced block.

## Sprites and slots

```
{{sprite|Cobblestone}}          icon plus a link, inline
{{sprite|Diamond|link=no}}      icon only, no link
{{sprite|Coal|text=fuel}}       icon with custom label
{{slot|Iron Ingot|3}}           one inventory slot holding a stack of 3
```

{{sprite|Cobblestone}} {{sprite|Diamond|link=no}} {{slot|Iron Ingot|3}}

## Recipes

Called with no argument, these use the page's own subject and read the real
recipes out of the game data.

```
{{crafting}}                    every recipe producing this page's subject
{{crafting|Furnace}}            every recipe producing a named thing
{{smelting|Stone}}              every smelting recipe producing it
{{used in|Cobblestone}}         every recipe that consumes it
{{recipe list}}                 every crafting recipe in the game
{{recipe list|type=smelting}}   every smelting recipe in the game
```

An explicit grid, for a recipe the data does not cover:

```
{{crafting
| pattern = ###/#X#/###
| # = Wooden Planks
| X = Diamond
| output = Jukebox
}}
```

{{crafting|Furnace}}

## Notes and boxes

```
{{stub}}                        marks the page as needing work
{{stub|block}}                  same, naming what kind of page it is
{{main|Crafting}}               "Main article: Crafting"
{{see also|Smelting}}           "See also: Smelting"
{{hatnote|This is about the block. For the item, see [[Sign]].}}
{{msgbox|type=warning|Careful.}}
```

{{msgbox|type=notice|Message boxes take `type=notice`, `warning`, `error` or `stub`.}}

## Data

```
{{id|Cobblestone}}              the numeric id, as code
{{id|Fern}}                     a subtype's id with its metadata: 31:2
{{id|block 68}}                 one id of several that share a name
{{list|blocks}}                 sortable table of every block
{{list|items}}                  every item
{{list|entities}}               every entity
{{list|light}}                  the blocks that give off light
{{list|opacity}}                the blocks with a hand-set opacity
{{list|food}}                   the items that heal
{{pagelist|namespace=biome}}    linked, sprite-led list of pages
```

Cobblestone's block id is {{id|Cobblestone}}, and a fern is {{id|Fern}}.

## Infoboxes

Infoboxes are automatic. If a page's title (or its `subject`) matches a block,
item or entity, the box builds itself from the extracted data. Add or override
rows from frontmatter:

```yaml
infobox:
  Tool: Pickaxe
  Renewable: "No"
```

Set `infobox: false` to suppress it entirely.
