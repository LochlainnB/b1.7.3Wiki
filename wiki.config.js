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
    entity: { label: 'Entity', plural: 'Entities', index: 'Mobs' },
    biome: { label: 'Biome', plural: 'Biomes', index: 'Biomes' },
    mechanic: { label: 'Mechanic', plural: 'Mechanics', index: 'Game mechanics' },
    guide: { label: 'Guide', plural: 'Guides', index: 'Guides' },
    wiki: { label: 'Wiki', plural: 'Wiki', index: 'Wiki pages' },
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
        { text: 'Mobs', href: '/entity/' },
        { text: 'Biomes', href: '/biome/' },
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
        { text: 'Block IDs', href: '/wiki/data-values/' },
        { text: 'Sprite sheet', href: '/wiki/sprites/' },
      ],
    },
    {
      id: 'wiki-community',
      label: 'This wiki',
      links: [
        { text: 'About', href: '/wiki/about/' },
        { text: 'Style guide', href: '/wiki/style-guide/' },
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

  // Editing. `editorUrl` turns the "View source" tab into a clickable link that
  // opens the backing Markdown file; set to null to show a plain path instead.
  editorUrl: (absPath) => `vscode://file/${absPath.replace(/\\/g, '/')}`,
};
