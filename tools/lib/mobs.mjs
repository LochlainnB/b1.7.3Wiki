// Which entities are mobs, and the shape an entity page takes.
//
// Beta 1.7.3 draws no line the extractor can read: EntityList registers mobs
// and minecarts through the same call, so the split is kept here by name.
// Monster is EntityMob itself, registered under its own name; it is concrete,
// so it can exist, where Mob (EntityLiving) is abstract and cannot.
export const MOBS = new Set(['Creeper', 'Skeleton', 'Spider', 'Zombie', 'Slime', 'Ghast',
  'PigZombie', 'Pig', 'Sheep', 'Cow', 'Chicken', 'Squid', 'Wolf', 'Giant', 'Monster']);

// Callers spell a mob three ways: the game's "PigZombie", the page title
// "Pig Zombie", and whatever an editor types on the command line.
const key = (name) => String(name).replace(/[^A-Za-z0-9]+/g, '').toLowerCase();
const KEYS = new Set([...MOBS].map(key));

export const isMob = (name) => name != null && KEYS.has(key(name));

// A mob is not obtained and then used. It arrives under its own spawning
// rules, leaves something behind when it dies, and acts on its own in between,
// so a mob stub asks those three questions instead of Obtaining and Usage.
export const MOB_SECTIONS = [
  '## Spawning',
  '',
  '<!-- Light level, biome, what it needs to stand on, pack size, despawning. -->',
  '',
  '## Drops',
  '',
  '<!-- What it leaves on death, how much, and what changes the amount. -->',
  '',
  '## Behaviour',
  '',
  '<!-- Movement, what provokes it, how it attacks, what it does when idle. -->',
  '',
];

// Every other entity page is for something with no block or item of its own:
// the player, a dropped item, a fireball, falling sand, lightning. Nothing
// obtains or uses one either. It is created, it acts, and something ends it.
// An item or block in motion -- an arrow in flight, lit TNT, a minecart -- has
// no entity page; the item's or block's page covers it.
export const ENTITY_SECTIONS = [
  '## Spawning',
  '',
  '<!-- What creates it, and where it appears. -->',
  '',
  '## Behaviour',
  '',
  '<!-- How it moves, what it does to blocks and entities, and what ends it. -->',
  '',
];
