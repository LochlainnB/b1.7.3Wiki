// Site-wide configuration. Everything an editor might reasonably want to change
// about the wiki's identity, navigation or namespaces lives here.
export default {
  title: 'Minecraft Beta 1.7.3 Wiki',
  shortTitle: 'Beta 1.7.3 Wiki',
  tagline: 'The complete reference for Minecraft Beta 1.7.3',
  version: 'Beta 1.7.3',
  lang: 'en',

  // Where content lives and where the built site goes.
  contentDir: 'content',
  outDir: 'site',

  // Content namespaces. The key is the directory under content/ and the first
  // path segment of the URL. `label` names it in navigation and breadcrumbs.
  namespaces: {
    block: { label: 'Block', plural: 'Blocks', index: 'Blocks' },
    item: { label: 'Item', plural: 'Items', index: 'Items' },
    entity: { label: 'Entity', plural: 'Entities', index: 'Entities' },
    biome: { label: 'Biome', plural: 'Biomes', index: 'Biomes' },
    dimension: { label: 'Dimension', plural: 'Dimensions', index: 'Dimensions' },
    structure: { label: 'Structure', plural: 'Structures', index: 'Structures' },
    mechanic: { label: 'Mechanic', plural: 'Mechanics', index: 'Game mechanics' },
    guide: { label: 'Guide', plural: 'Guides', index: 'Guides' },
    wiki: { label: 'Wiki', plural: 'Wiki', index: 'Wiki pages' },
  },

  // Every category a page may carry, and which pages carry it. A category not
  // listed here is a build error: add it here, deliberately, rather than
  // inventing it on a page. A page takes the one category that names its kind,
  // then every topic category whose rule it meets.
  categories: {
    // One per page, by what the page is about.
    'Blocks': 'Every page in content/block/.',
    'Items': 'Every page in content/item/.',
    'Mobs': 'Entity pages for living creatures other than the player.',
    'Entities': 'Entity pages that are not mobs: the player, dropped items, fireballs, falling sand and lightning.',
    'Biomes': 'Every biome page.',
    'Dimensions': 'Every dimension page.',
    'Structures': 'Every structure page.',
    'Game mechanics': 'Every page in content/mechanic/.',
    'Guides': 'Every page in content/guide/.',
    'Wiki': 'Pages about the wiki itself.',

    // Topics, as many as apply.
    'Naturally generated': 'Blocks the world generator places.',
    'Building blocks': 'Full or partial blocks placed to build with: stone, planks, bricks, glass, wool, slabs, stairs.',
    'Plants': 'Saplings, leaves, flowers, tall grass, ferns, dead bushes, mushrooms, crops, cactus, sugar cane and pumpkins.',
    'Ores': 'The six ore blocks.',
    'Redstone': 'Blocks and items that give off, carry or respond to redstone power.',
    'Transportation': 'Rails, minecarts, boats and the saddle.',
    'Utility blocks': 'Blocks placed to be used rather than built with: crafting table, furnace, chest, bed, sign, ladder, jukebox, note block.',
    'Tools': 'Pickaxes, axes, shovels, hoes, shears, flint and steel, buckets, the fishing rod, compass, clock and map.',
    'Weapons': 'Swords, the bow and arrows.',
    'Armour': 'The twenty armour pieces.',
    'Food': 'Everything eaten to heal.',
    'Materials': 'Items whose only use is as a crafting ingredient, a smelting input or fuel.',
    'Hostile mobs': 'Mobs the game counts as monsters: zombie, skeleton, spider, creeper, slime, ghast, pig zombie, giant, monster.',
    'Passive mobs': 'Mobs the game counts as creatures or water creatures: pig, sheep, cow, chicken, wolf, squid.',
  },

  // Left sidebar. Each portlet becomes a #p-<id> block in the Vector sidebar.
  sidebar: [
    {
      id: 'navigation',
      label: 'Navigation',
      links: [
        { text: 'Main page', href: '/' },
        { text: 'All pages', href: '/wiki/all-pages/' },
        { text: 'Categories', href: '/wiki/categories/' },
        { text: 'Recent changes', href: '/wiki/recent-changes/' },
        { text: 'Random page', href: '/wiki/random/' },
      ],
    },
    {
      id: 'content',
      label: 'Content',
      links: [
        { text: 'Blocks', href: '/block/' },
        { text: 'Items', href: '/item/' },
        { text: 'Entities', href: '/entity/' },
        { text: 'Biomes', href: '/biome/' },
        { text: 'Dimensions', href: '/dimension/' },
        { text: 'Structures', href: '/structure/' },
        { text: 'Game mechanics', href: '/mechanic/' },
        { text: 'Guides', href: '/guide/' },
      ],
    },
    {
      id: 'reference',
      label: 'Reference',
      links: [
        { text: 'Crafting recipes', href: '/mechanic/crafting/' },
        { text: 'Smelting', href: '/mechanic/smelting/' },
        { text: 'Mining', href: '/mechanic/mining/' },
        { text: 'Mob spawning', href: '/mechanic/mob-spawning/' },
        { text: 'World generation', href: '/mechanic/world-generation/' },
        { text: 'Game tick', href: '/mechanic/game-tick/' },
        { text: 'Damage', href: '/mechanic/damage/' },
        { text: 'Block IDs', href: '/wiki/data-values/' },
        { text: 'Sprite sheet', href: '/wiki/sprites/' },
      ],
    },
    {
      id: 'wiki-community',
      label: 'This wiki',
      links: [
        { text: 'About', href: '/wiki/about/' },
        { text: 'Page templates', href: '/wiki/page-templates/' },
        { text: 'Stubs', href: '/wiki/stubs/' },
      ],
    },
  ],

  // Footer.
  license: {
    text: 'CC BY-NC-SA 3.0',
    href: 'https://creativecommons.org/licenses/by-nc-sa/3.0/',
  },
  disclaimer:
    'An unofficial fan project. Minecraft content and materials are trademarks ' +
    'and copyrights of Mojang AB and its licensors. All rights reserved. ' +
    'This site is not affiliated with Mojang or Microsoft.',

  // Editing. `editorUrl` turns the "View source" tab into a clickable link to the
  // backing Markdown file; set to null to show a plain path instead. Built by
  // GitHub Actions, it links the file on GitHub; built anywhere else, it opens
  // the file in VS Code.
  editorUrl: process.env.GITHUB_ACTIONS
    ? (absPath, relFile) => `${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}` +
      `/blob/${process.env.GITHUB_REF_NAME}/${relFile}`
    : (absPath) => `vscode://file/${absPath.replace(/\\/g, '/')}`,
};
