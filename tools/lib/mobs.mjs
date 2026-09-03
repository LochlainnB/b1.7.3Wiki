// Which entities are mobs, and the shape a mob page takes.
//
// Beta 1.7.3 draws no line the extractor can read: EntityList registers mobs
// and minecarts through the same call, so the split is kept here by name.
export const MOBS = new Set(['Creeper', 'Skeleton', 'Spider', 'Zombie', 'Slime', 'Ghast',
  'PigZombie', 'Pig', 'Sheep', 'Cow', 'Chicken', 'Squid', 'Wolf', 'Giant']);

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
