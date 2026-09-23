// Cross-check data/*.json against the decompiled source.
//
// data/ is extracted from the client jar's bytecode; the decompiled source is
// an independent reading of the same jar. When the two agree, the numbers on
// every page are right. When they disagree, one of the two extractors is wrong
// and a reader would be told something false.
//
// Disagreements are errors: a value that contradicts the source is a bug.
// Omissions are warnings: something the extractors never picked up is a
// to-do, in the same way a red link is.

import { readClass } from './source.mjs';

// ---------------------------------------------------------------------------
// Java source parsing
//
// Only static initialisers are read, and only the handful of registration
// idioms the game uses. This is deliberately not a Java parser.
// ---------------------------------------------------------------------------

/**
 * Assignment statements in a class body, joined across lines.
 * Yields [lhs, rhs] for every `name = ... ;` at field-initialiser depth.
 */
function statements(src) {
  const out = [];
  const lines = src.split('\n');
  let lhs = null;
  let buf = '';
  for (const line of lines) {
    if (lhs === null) {
      const m = /^\s{4,}([A-Za-z_]\w*) = (.*)$/.exec(line);
      if (!m) continue;
      lhs = m[1];
      buf = m[2];
    } else {
      buf += ' ' + line.trim();
    }
    if (buf.trimEnd().endsWith(';')) {
      out.push([lhs, buf.trimEnd().slice(0, -1)]);
      lhs = null;
      buf = '';
    }
  }
  return out;
}

/** Java float arithmetic, so light values truncate exactly as the game does. */
const f32 = (n) => Math.fround(n);

/** Setter calls in source order: [name, firstArgText]. */
function chain(rhs) {
  const out = [];
  const re = /\.(set[A-Za-z]+|disableStats|disableNeighborNotifyOnMetadataChange)\(([^()]*(?:\([^()]*\))?[^()]*)\)/g;
  let m;
  while ((m = re.exec(rhs))) out.push([m[1], m[2]]);
  return out;
}

/** The body of the first `{` at or after `from`, brace-matched. */
function block(src, from) {
  const open = src.indexOf('{', from);
  if (open < 0) return null;
  let depth = 0;
  for (let i = open; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}' && --depth === 0) return src.slice(open + 1, i);
  }
  return null;
}

/** Split an argument list on commas that are not inside brackets. */
function splitArgs(text) {
  const out = [];
  let depth = 0;
  let buf = '';
  for (const c of text) {
    if (c === '(' || c === '[') depth++;
    else if (c === ')' || c === ']') depth--;
    if (c === ',' && depth === 0) { out.push(buf.trim()); buf = ''; } else buf += c;
  }
  if (buf.trim()) out.push(buf.trim());
  return out;
}

/**
 * A block class's constructor: its parameters, its super() call, its body.
 *
 * Most block classes declare one; BlockContainer declares two, so the overload
 * is chosen by how many arguments the caller passed.
 */
function ctorOf(src, cls, arity) {
  const re = new RegExp(`(?:public|protected)\\s+${cls}\\s*\\(([^)]*)\\)\\s*\\{`, 'g');
  const found = [];
  let sig;
  while ((sig = re.exec(src))) {
    const params = splitArgs(sig[1]).map((p) => p.split(/\s+/).pop());
    const body = block(src, sig.index);
    if (body !== null) found.push({ params, body });
  }
  const hit = found.find((c) => c.params.length === arity) ?? found[0];
  if (!hit) return null;
  const sup = /\bsuper\(([^;]*)\);/.exec(hit.body);
  const ext = new RegExp(`class\\s+${cls}\\s+extends\\s+(\\w+)`).exec(src);
  return { ...hit, superName: ext?.[1] ?? null, superArgs: sup ? splitArgs(sup[1]) : [] };
}

/**
 * Builder calls a block makes from inside its own constructor.
 *
 * Block's <clinit> is only half the chain: the pistons set their own hardness,
 * a stair block copies the block it is cut from, and stairs, slabs and
 * farmland set their own light opacity. Reading only the chain written onto
 * the `new` expression left those six with no hardness, which both extractors
 * used to agree on -- data/ said null, this said 0, and `near` called it a
 * match. Walking the constructor is what makes the two readings independent.
 *
 * Constructor bodies run base-class-first, so the frames are replayed in
 * reverse. An argument is followed through a super() call only when it is
 * passed straight down as a bare parameter name, which is all Beta ever does.
 */
function ctorCalls(readCls, cls, callArgs, blockAt) {
  const frames = [];
  let current = cls;
  let args = callArgs;
  const unresolved = [];
  while (current && current !== 'Block' && frames.length < 8) {
    const src = readCls(current);
    const ctor = src && ctorOf(src, current, args.length);
    if (!ctor) break;
    frames.push({ ctor, args });
    args = ctor.superArgs.map((a) => {
      const i = ctor.params.indexOf(a);
      return i >= 0 ? args[i] : a;
    });
    current = ctor.superName;
  }

  const out = [];
  for (const { ctor, args: frameArgs } of frames.reverse()) {
    const re = /this\.(set[A-Za-z]+)\(([^;]*)\);/g;
    let m;
    while ((m = re.exec(ctor.body))) {
      const [, name, expr] = m;
      if (!/^set(Hardness|Resistance|LightValue|LightOpacity|BlockUnbreakable)$/.test(name)) continue;
      const value = evalCtorArg(expr, ctor.params, frameArgs, blockAt);
      if (value === undefined) unresolved.push(`${cls}.${name}(${expr.trim()})`);
      else out.push([name, value]);
    }
  }
  return { calls: out, unresolved };
}

/**
 * One constructor argument, as a number.
 *
 * Only two shapes occur: a literal, and a field of another block scaled by a
 * constant -- `var2.blockResistance / 3.0F`. Anything else returns undefined
 * and is reported rather than guessed at.
 */
function evalCtorArg(expr, params, args, blockAt) {
  const text = expr.trim();
  if (text === '') return null;                       // setBlockUnbreakable()
  if (/^-?[\d.]+[FfDdLl]?$/.test(text)) return parseFloat(text);
  const ref = /^(\w+)\.(blockHardness|blockResistance)\s*(?:([*/])\s*(-?[\d.]+)[FfDd]?)?$/.exec(text);
  if (!ref) return undefined;
  const i = params.indexOf(ref[1]);
  if (i < 0) return undefined;
  const model = blockAt(args[i]);
  if (!model) return undefined;
  // The record holds blast resistance, which is the raw field over five.
  let v = ref[2] === 'blockHardness' ? model.hardness : model.blastResistance * 5;
  if (ref[3] === '*') v *= parseFloat(ref[4]);
  else if (ref[3] === '/') v /= parseFloat(ref[4]);
  return v;
}

/**
 * Replay Block's builder chain.
 *
 * The order matters. From Block.java:
 *   setResistance(r)  -> blockResistance = r * 3
 *   setHardness(h)    -> blockHardness = h; if (blockResistance < h * 5) blockResistance = h * 5
 * so setHardness only ever raises resistance. Reordering the calls, or treating
 * the second as an assignment, gets bedrock and portal wrong. The constructor's
 * calls come first, because it finishes before the chain written onto its
 * result begins.
 */
function parseBlocks(src, superId, readCls, note) {
  const blocks = new Map();   // id -> record
  const fields = new Map();   // field name -> id
  const blockAt = (field) => blocks.get(fields.get(field));
  for (const [field, rhs] of statements(src)) {
    const ctor = /new\s+(\w+)\(([^;]*)/.exec(rhs);
    if (!ctor) continue;
    const callArgs = splitArgs(ctor[2].slice(0, matchedParen(ctor[2])));
    const first = /^\s*(\d+)/.exec(ctor[2]);
    // A few blocks take no id: BlockCloth() hardcodes super(35, ...) instead.
    const id = first ? Number(first[1]) : superId(ctor[1]);
    if (id === null) continue;
    let hardness = 0;
    let resistance = 0;
    let light = 0;
    let opacity = null;
    let key = null;
    const own = ctorCalls(readCls, ctor[1], callArgs, blockAt);
    for (const u of own.unresolved) note(u);
    const calls = own.calls.concat(chain(rhs).map(([n, a]) => [n, parseFloat(a), a]));
    for (const [name, v, arg] of calls) {
      if (name === 'setHardness') {
        hardness = v;
        if (resistance < v * 5) resistance = v * 5;
      } else if (name === 'setBlockUnbreakable') {
        hardness = -1;
        if (resistance < -5) resistance = -5;
      } else if (name === 'setResistance') {
        resistance = v * 3;
      } else if (name === 'setLightValue') {
        light = Math.trunc(f32(15 * f32(v)));
      } else if (name === 'setLightOpacity') {
        opacity = v;
      } else if (name === 'setBlockName' && arg !== undefined) {
        key = /"([^"]+)"/.exec(arg)?.[1] ?? null;
      }
    }
    if (rhs.includes('setBlockUnbreakable()')) hardness = -1;
    fields.set(field, id);
    // Blocks are declared once each; a later re-registration would be a bug.
    if (!blocks.has(id)) {
      blocks.set(id, {
        id, field, key, hardness, blastResistance: resistance / 5,
        lightEmission: light, lightOpacity: opacity,
      });
    }
  }
  return { blocks, fields };
}

/** Index just past the `)` closing an argument list that starts after `(`. */
function matchedParen(text) {
  let depth = 1;
  for (let i = 0; i < text.length; i++) {
    if (text[i] === '(') depth++;
    else if (text[i] === ')' && --depth === 0) return i;
  }
  return text.length;
}

function parseItems(src) {
  const items = new Map();
  const fields = new Map();
  for (const [field, rhs] of statements(src)) {
    const ctor = /new\s+(\w+)\(\s*(\d+)/.exec(rhs);
    if (!ctor) continue;
    const id = 256 + Number(ctor[2]);   // Item(int): this.shiftedIndex = 256 + var1
    const argText = rhs.slice(rhs.indexOf('(', ctor.index) + 1);
    const args = splitArgs(argText.slice(0, matchedParen(argText)));
    const builders = chain(rhs);
    let icon = null;
    let key = null;
    for (const [name, arg] of builders) {
      if (name === 'setIconCoord') {
        const xy = /(\d+)\s*,\s*(\d+)/.exec(arg);
        if (xy) icon = { x: Number(xy[1]), y: Number(xy[2]) };
      } else if (name === 'setItemName') {
        key = /"([^"]+)"/.exec(arg)?.[1] ?? null;
      }
    }
    fields.set(field, id);
    if (!items.has(id)) items.set(id, { id, field, key, icon, cls: ctor[1], args, builders });
  }
  return { items, fields };
}

/**
 * stackSize, durability, attackDamage and heal for one item, from the source.
 *
 * Each is what the finished item answers when the game asks it:
 * getItemStackLimit(), getMaxDamage(), getDamageVsEntity() where a subclass
 * overrides Item's flat 1, and the heal() in onItemRightClick. A durability of
 * 0 and a missing override or heal come back as null, meaning data/ should
 * carry no such key; undefined means the source could not be read.
 */
function itemProperties(readCls, cls, argTexts, builders) {
  const scope = ctorScope(readCls, [], [], {}, []);
  const built = itemState(readCls, cls, argTexts.map((a) => evaluate(a, scope)), builders);
  if (!built) return null;
  const { state, chain: classes } = built;
  const attack = getterValue(classes, 'getDamageVsEntity', state);
  const durability = getterValue(classes, 'getMaxDamage', state)?.value;
  const heal = healValue(classes, state);
  return {
    stackSize: getterValue(classes, 'getItemStackLimit', state)?.value,
    durability: durability === 0 ? null : durability,
    attackDamage: attack && attack.cls !== 'Item' ? attack.value : null,
    heal: heal ? heal.value : null,
  };
}

/**
 * Compare one extracted property with the source's reading of it.
 * `theirs` null means the key should be absent; undefined, unreadable.
 */
function checkProperty(add, label, what, mine, theirs, where) {
  if (theirs === undefined) {
    add('warn', `${label}: ${what} could not be read from ${where}`);
  } else if ((mine ?? null) === theirs) {
    // agrees
  } else if (mine == null) {
    add('warn', `${label}: ${where} gives a ${what} of ${theirs}, which data/ does not carry`);
  } else {
    add('error', `${label}: ${what} is ${mine} in data/, ${theirs ?? 'none'} in ${where}`);
  }
}

function parseEntities(src) {
  const out = new Map();
  const re = /addMapping\((\w+)\.class,\s*"([^"]+)",\s*(\d+)\)/g;
  let m;
  while ((m = re.exec(src))) out.set(m[2], { name: m[2], cls: m[1], networkId: Number(m[3]) });
  return out;
}

/** Resolve `Block.foo.blockID` / `Item.bar.shiftedIndex` / a bare literal. */
function resolveRef(text, blockFields, itemFields) {
  let m = /Block\.(\w+)\.blockID/.exec(text);
  if (m) return blockFields.has(m[1]) ? { block: blockFields.get(m[1]) } : null;
  m = /Item\.(\w+)\.shiftedIndex/.exec(text);
  if (m) return itemFields.has(m[1]) ? { item: itemFields.get(m[1]) } : null;
  m = /new ItemStack\(\s*Block\.(\w+)/.exec(text);
  if (m) return blockFields.has(m[1]) ? { block: blockFields.get(m[1]) } : null;
  m = /new ItemStack\(\s*Item\.(\w+)/.exec(text);
  if (m) return itemFields.has(m[1]) ? { item: itemFields.get(m[1]) } : null;
  return null;
}

function parseSmelting(src, blockFields, itemFields) {
  const out = [];
  const re = /addSmelting\(([^,]+),\s*(new ItemStack\([^;]*?\))\)\s*;/g;
  let m;
  while ((m = re.exec(src))) {
    const input = resolveRef(m[1], blockFields, itemFields);
    const output = resolveRef(m[2], blockFields, itemFields);
    if (input && output) out.push({ input, output });
  }
  return out;
}

// ---------------------------------------------------------------------------
// Constructor arithmetic
//
// A stack size, a durability, a hit, a meal and a mob's health are all set in
// constructors, and several are computed there: `4 + var2.getDamageVsEntity() * 2`
// for a sword, `maxDamageArray[var4] * 3 << var2` for armour, `this.health *= 10`
// for the giant. So the check evaluates Java expressions -- literals, the
// constructor's parameters, `this.` fields, a class's static int arrays, and an
// enum constant's getters -- and gives up with undefined on anything else.
// ---------------------------------------------------------------------------

const THIS = Symbol('this');

function tokenize(text) {
  const re = /\s*(?:(\d+(?:\.\d+)?)[FfDdLl]?|("[^"]*")|([A-Za-z_]\w*)|(<<|>>|[-+*/%()[\].,]))/y;
  const out = [];
  re.lastIndex = 0;
  while (re.lastIndex < text.length) {
    const at = re.lastIndex;
    const m = re.exec(text);
    if (!m) return /^\s*$/.test(text.slice(at)) ? out : null;
    if (m[1] !== undefined) out.push({ num: parseFloat(m[1]) });
    else if (m[2] !== undefined) out.push({ str: m[2].slice(1, -1) });
    else if (m[3] !== undefined) out.push({ id: m[3] });
    else out.push({ op: m[4] });
  }
  return out;
}

function arith(op, a, b) {
  if (typeof a !== 'number' || typeof b !== 'number') return undefined;
  switch (op) {
    case '+': return a + b;
    case '-': return a - b;
    case '*': return a * b;
    case '/': return b ? Math.trunc(a / b) : undefined;
    case '%': return b ? a % b : undefined;
    case '<<': return a << b;
    case '>>': return a >> b;
    default: return undefined;
  }
}

/** A Java expression's value in `scope`, or undefined if it is not plain arithmetic. */
function evaluate(text, scope) {
  const toks = tokenize(text.trim());
  if (!toks || !toks.length) return undefined;
  let i = 0;
  const peek = (op) => toks[i] && toks[i].op === op;
  const binary = (ops, sub) => () => {
    let left = sub();
    while (toks[i] && ops.includes(toks[i].op)) {
      const op = toks[i++].op;
      left = arith(op, left, sub());
    }
    return left;
  };
  const primary = () => {
    const t = toks[i++];
    if (!t) throw new Error('end of expression');
    if (t.num !== undefined) return t.num;
    if (t.str !== undefined) return t.str;
    if (t.op === '(') {
      // A cast: (float)x is x, for the arithmetic done here.
      if (toks[i]?.id && /^(int|float|double|byte|short|long)$/.test(toks[i].id) && toks[i + 1]?.op === ')') {
        i += 2;
        return unary();
      }
      const v = expr();
      if (!peek(')')) throw new Error('unclosed (');
      i++;
      return v;
    }
    if (t.id) return scope.name(t.id);
    throw new Error(`unexpected ${t.op}`);
  };
  const postfix = () => {
    let v = primary();
    for (;;) {
      if (peek('.')) {
        i++;
        const name = toks[i++]?.id;
        if (peek('(')) {
          i++;
          const args = [];
          while (!peek(')')) {
            args.push(expr());
            if (peek(',')) i++;
            else if (!peek(')')) throw new Error('bad argument list');
          }
          i++;
          v = scope.call(v, name, args);
        } else {
          v = scope.member(v, name);
        }
      } else if (peek('[')) {
        i++;
        const idx = expr();
        if (!peek(']')) throw new Error('unclosed [');
        i++;
        v = Array.isArray(v) && typeof idx === 'number' ? v[idx] : undefined;
      } else {
        return v;
      }
    }
  };
  const unary = () => {
    if (peek('-')) {
      i++;
      const v = unary();
      return typeof v === 'number' ? -v : undefined;
    }
    return postfix();
  };
  const mul = binary(['*', '/', '%'], unary);
  const add = binary(['+', '-'], mul);
  const expr = binary(['<<', '>>'], add);
  try {
    const v = expr();
    return i === toks.length ? v : undefined;
  } catch {
    return undefined;
  }
}

/** Primitive field initialisers declared on a class: `protected int maxStackSize = 64;`. */
function fieldDefaults(src) {
  const out = {};
  const re = /^ {4}(?:(?:public|protected|private|final|transient|volatile)\s+)*(?:int|float|double|boolean|byte|short|long)\s+(\w+)\s*=\s*([^;]+);/gm;
  let m;
  while ((m = re.exec(src))) out[m[1]] = evaluate(m[2], plainScope());
  return out;
}

/** A class's static int arrays: `private static final int[] maxDamageArray = new int[]{11, 16, 15, 13};`. */
function staticArrays(src) {
  const out = {};
  const re = /^ {4}(?:(?:public|protected|private|final)\s+)*static\s+(?:final\s+)?int\[\]\s+(\w+)\s*=\s*new int\[\]\s*\{([^}]*)\};/gm;
  let m;
  while ((m = re.exec(src))) out[m[1]] = splitArgs(m[2]).map(Number);
  return out;
}

/** Scope with nothing in it, for literals. */
function plainScope() {
  return { name: () => undefined, member: () => undefined, call: () => undefined };
}

/**
 * The scope a constructor body runs in: its parameters, `this`, the static
 * arrays of the classes it belongs to, and enum constants by `Enum.NAME`.
 */
function ctorScope(readCls, params, args, state, srcs) {
  const statics = Object.assign({}, ...srcs.map(staticArrays));
  const bound = Object.fromEntries(params.map((p, n) => [p, args[n]]));
  return {
    name(id) {
      if (id === 'this') return THIS;
      if (id in bound) return bound[id];
      if (id in statics) return statics[id];
      if (/^[A-Z]/.test(id)) return { cls: id };
      return undefined;
    },
    member(v, name) {
      if (v === THIS) return state[name];
      if (v && v.cls && enumOf(readCls, v.cls)?.constants[name]) return { enumCls: v.cls, constant: name };
      return undefined;
    },
    call(v, name) {
      if (!v || !v.enumCls) return undefined;
      const e = enumOf(readCls, v.enumCls);
      const field = e.getters[name];
      return field === undefined ? undefined : e.constants[v.constant][field];
    },
  };
}

const enums = new Map();

/** An enum's constants as field values: EnumToolMaterial.IRON -> {maxUses: 250, ...}. */
function enumOf(readCls, cls) {
  if (enums.has(cls)) return enums.get(cls);
  const src = readCls(cls);
  let out = null;
  if (src && new RegExp(`\\benum\\s+${cls}\\b`).test(src)) {
    const ctor = new RegExp(`${cls}\\s*\\(([^)]*)\\)\\s*\\{`).exec(src);
    const params = ctor ? splitArgs(ctor[1]).map((p) => p.split(/\s+/).pop()) : [];
    const body = ctor ? block(src, ctor.index) : '';
    const assigns = [...body.matchAll(/this\.(\w+)\s*=\s*(\w+);/g)];
    const constants = {};
    for (const m of src.matchAll(/^ {4}([A-Z][A-Z0-9_]*)\(([^)]*)\)[,;]/gm)) {
      const args = splitArgs(m[2]).map((a) => evaluate(a, plainScope()));
      constants[m[1]] = Object.fromEntries(assigns.map(([, field, p]) => [field, args[params.indexOf(p)]]));
    }
    const getters = {};
    for (const m of src.matchAll(/public\s+\w+\s+(\w+)\(\)\s*\{\s*return this\.(\w+);\s*\}/g)) getters[m[1]] = m[2];
    out = { constants, getters };
  }
  enums.set(cls, out);
  return out;
}

/** Statements of a method body, split on the semicolons at its own level. */
function bodyStatements(body) {
  const out = [];
  let depth = 0;
  let buf = '';
  for (const c of body) {
    if (c === '(' || c === '{') depth++;
    else if (c === ')' || c === '}') depth--;
    if (c === ';' && depth === 0) {
      out.push(buf.trim());
      buf = '';
    } else if (c !== '{' && c !== '}') {
      buf += c;
    }
  }
  if (buf.trim()) out.push(buf.trim());
  return out;
}

/** The body of a method declared in `src`, by name. */
function methodBody(src, name) {
  const re = new RegExp(`(?:public|protected|private)[^;{}()]*\\b${name}\\s*\\([^)]*\\)\\s*\\{`);
  const m = re.exec(src);
  return m ? block(src, m.index) : null;
}

/**
 * The field a one-argument builder writes: `setMaxDamage(int var1) { this.maxDamage = var1; return this; }`.
 * Looked for across the chain, nearest class first, so an override wins.
 */
function setterField(srcs, name) {
  for (const src of srcs) {
    const re = new RegExp(`\\b${name}\\s*\\(\\s*\\w+\\s+(\\w+)\\s*\\)\\s*\\{\\s*this\\.(\\w+)\\s*=\\s*(\\w+);\\s*return this;\\s*\\}`);
    const m = re.exec(src);
    if (m) return m[1] === m[3] ? m[2] : null;
    if (methodBody(src, name) !== null) return null;
  }
  return null;
}

/** Class sources from `cls` up to and including `stop`, nearest first. */
function classChain(readCls, cls, stop) {
  const out = [];
  let current = cls;
  while (current && out.length < 12) {
    const src = readCls(current);
    if (!src) return null;
    out.push({ cls: current, src });
    if (current === stop) return out;
    current = new RegExp(`class\\s+${current}\\s+extends\\s+(\\w+)`).exec(src)?.[1];
  }
  return null;
}

/**
 * The fields an item holds once constructed and its builder chain has run.
 *
 * Constructor frames are replayed base class first, each applying its own
 * field initialisers, then its body. A super() argument is evaluated in the
 * calling frame, so `super(var1, 2, var2, blocksEffectiveAgainst)` hands the
 * pickaxe's 2 on to ItemTool.
 */
function itemState(readCls, cls, args, builders) {
  const frames = [];
  let current = cls;
  let callArgs = args;
  while (current && frames.length < 8) {
    const src = readCls(current);
    const ctor = src && ctorOf(src, current, callArgs.length);
    if (!ctor) return null;
    frames.push({ cls: current, src, ctor, args: callArgs });
    if (current === 'Item') break;
    const scope = ctorScope(readCls, ctor.params, callArgs, {}, [src]);
    callArgs = ctor.superArgs.map((a) => evaluate(a, scope));
    current = ctor.superName;
  }
  if (current !== 'Item') return null;
  const srcs = frames.map((f) => f.src);
  const state = {};
  for (const f of [...frames].reverse()) {
    Object.assign(state, fieldDefaults(f.src));
    const scope = ctorScope(readCls, f.ctor.params, f.args, state, srcs);
    for (const stmt of bodyStatements(f.ctor.body)) applyStatement(stmt, scope, state, srcs);
  }
  const scope = ctorScope(readCls, [], [], state, srcs);
  for (const [name, arg] of builders) applyStatement(`this.${name}(${arg})`, scope, state, srcs);
  return { state, chain: frames.map(({ cls: c, src }) => ({ cls: c, src })) };
}

function applyStatement(stmt, scope, state, srcs) {
  let m = /^this\.(\w+)\s*([-+*/]?)=\s*([\s\S]+)$/.exec(stmt);
  if (m) {
    const v = evaluate(m[3], scope);
    state[m[1]] = m[2] ? arith(m[2], state[m[1]], v) : v;
    return;
  }
  m = /^(?:this\.)?(\w+)\(([\s\S]*)\)$/.exec(stmt);
  if (m && m[1] !== 'super') {
    const field = setterField(srcs, m[1]);
    if (field) state[field] = evaluate(m[2], scope);
  }
}

/** A scope that knows only `this`, for reading a finished object's fields. */
function fieldScope(state) {
  return {
    ...plainScope(),
    name: (id) => (id === 'this' ? THIS : undefined),
    member: (v, f) => (v === THIS ? state[f] : undefined),
  };
}

/**
 * What the nearest override of a getter returns, as { cls, value }: the class
 * declaring it, and `return this.x;` or a literal evaluated against the item.
 */
function getterValue(chain, name, state) {
  for (const { cls, src } of chain) {
    const body = methodBody(src, name);
    if (body === null) continue;
    const m = /^\s*return\s+([^;]+);\s*$/.exec(body);
    return { cls, value: m ? evaluate(m[1], fieldScope(state)) : undefined };
  }
  return null;
}

/**
 * What eating an item restores, as { value }: the argument onItemRightClick
 * passes to heal(), following super.onItemRightClick() up the chain. Null for
 * an item whose use never heals.
 */
function healValue(chain, state) {
  for (const { src } of chain) {
    const body = methodBody(src, 'onItemRightClick');
    if (body === null) continue;
    const heal = /\.heal\(([^;]*)\);/.exec(body);
    if (heal) return { value: evaluate(heal[1], fieldScope(state)) };
    if (!/super\.onItemRightClick\(/.test(body)) return null;
  }
  return null;
}

/** Method names a body calls on `this`, bare or qualified. */
function selfCalls(body) {
  return [...body.matchAll(/(?<![\w.])(?:this\.)?(\w+)\s*\(/g)]
    .map((m) => m[1]).filter((n) => !/^(super|this|if|for|while|switch|return|new)$/.test(n));
}

/** Whether the nearest override of `name` in the chain can assign health. */
function writesHealth(chain, name, seen) {
  if (seen.has(name)) return false;
  seen.add(name);
  for (const { src } of chain) {
    const body = methodBody(src, name);
    if (body === null) continue;
    if (/this\.health\s*[-+*/]?=[^=]/.test(body)) return true;
    return selfCalls(body).some((n) => writesHealth(chain, n, seen));
  }
  return false;
}

/**
 * The health a mob starts with: EntityLiving's initialiser, then each
 * constructor's `this.health = n` or `this.health *= n`, base class first.
 * Returns { health } or { unknown: why }, and null for a non-living entity.
 */
function mobHealth(readCls, cls) {
  const chain = classChain(readCls, cls, 'Entity');
  if (!chain) return { unknown: `the class chain of ${cls} could not be read` };
  if (!chain.some((c) => c.cls === 'EntityLiving')) return null;
  const state = {};
  for (const { cls: c, src } of [...chain].reverse()) {
    Object.assign(state, fieldDefaults(src));
    const ctor = ctorOf(src, c, 1);
    if (!ctor) return { unknown: `${c} has no constructor taking a World` };
    const scope = ctorScope(readCls, ctor.params, [undefined], state, [src]);
    for (const stmt of bodyStatements(ctor.body)) {
      const m = /^this\.health\s*([-+*/]?)=\s*([\s\S]+)$/.exec(stmt);
      if (m) {
        const v = evaluate(m[2], scope);
        state.health = m[1] ? arith(m[1], state.health, v) : v;
        if (typeof state.health !== 'number') return { unknown: `${c} computes its health` };
        continue;
      }
      for (const n of selfCalls(stmt)) {
        if (writesHealth(chain, n, new Set())) return { unknown: `${c} calls ${n}, which sets health` };
      }
    }
  }
  return { health: state.health };
}

// ---------------------------------------------------------------------------
// Comparisons
// ---------------------------------------------------------------------------

const near = (a, b) => Math.abs((a ?? 0) - (b ?? 0)) < 0.001;
const idOf = (ref) => (ref?.item ?? ref?.block ?? null);

function compareBlocks(source, data, add) {
  const src = readClass(source, 'Block');
  if (!src) return add('warn', 'Block.java not found in the source tree');

  /** The id a no-argument subclass passes to super(), e.g. BlockCloth -> 35. */
  const superId = (cls) => {
    const sub = readClass(source, cls);
    const m = sub && new RegExp(`public ${cls}\\(\\)\\s*\\{\\s*super\\(\\s*(\\d+)`).exec(sub);
    return m ? Number(m[1]) : null;
  };
  const readCls = (cls) => readClass(source, cls);
  const { blocks, fields } = parseBlocks(src, superId, readCls, (what) =>
    add('warn', `${what} is a constructor value this check cannot read`));
  const mine = new Map(data.blocks.map((b) => [b.id, b]));

  // Every block's item form: a handful are named at the end of Block's
  // <clinit> (`Item.itemsList[cloth.blockID] = new ItemCloth(...)`), and a
  // loop gives each remaining block the class it names there.
  const forms = new Map();
  for (const m of src.matchAll(/Item\.itemsList\[(\w+)\.blockID\]\s*=\s*\(?\s*new\s+(\w+)\(/g)) {
    forms.set(m[1], m[2]);
  }
  const fallback = /Item\.itemsList\[\w+\]\s*=\s*new\s+(\w+)\(\w+\s*-\s*256\)/.exec(src)?.[1];
  if (!fallback) add('warn', 'Block.java: the loop giving blocks their item form was not found');

  let checked = 0;
  for (const [id, s] of blocks) {
    const m = mine.get(id);
    if (!m) {
      add('warn', `block ${id} (${s.field}) is in Block.java but not in data/blocks.json`);
      continue;
    }
    checked++;
    const label = `block ${id} (${m.name || s.field})`;
    if (!near(m.hardness, s.hardness)) {
      add('error', `${label}: hardness is ${m.hardness} in data/blocks.json, ${s.hardness} in Block.java`);
    }
    if (!near(m.blastResistance, s.blastResistance)) {
      add('error', `${label}: blast resistance is ${m.blastResistance} in data/blocks.json, ${s.blastResistance} in Block.java`);
    }
    if ((m.lightEmission ?? 0) !== s.lightEmission) {
      add('error', `${label}: light is ${m.lightEmission} in data/blocks.json, ${s.lightEmission} in Block.java`);
    }
    if ((m.lightOpacity ?? null) !== (s.lightOpacity ?? null)) {
      add('error', `${label}: light opacity is ${m.lightOpacity} in data/blocks.json, ${s.lightOpacity} in the source`);
    }
    const form = forms.get(s.field) ?? fallback;
    if (form) {
      const want = itemProperties(readCls, form, [String(id - 256)], []);
      checkProperty(add, label, 'stack size', m.stackSize, want ? want.stackSize : undefined,
        `its item form, ${form}`);
    }
  }
  for (const b of data.blocks) {
    if (!blocks.has(b.id)) add('warn', `block ${b.id} (${b.name}) is in data/blocks.json but was not found in Block.java`);
  }
  return { checked, fields };
}

function compareItems(source, data, add) {
  const src = readClass(source, 'Item');
  if (!src) return add('warn', 'Item.java not found in the source tree');
  const { items, fields } = parseItems(src);
  const mine = new Map(data.items.map((i) => [i.id, i]));
  const readCls = (cls) => readClass(source, cls);

  let checked = 0;
  for (const [id, s] of items) {
    const m = mine.get(id);
    if (!m) {
      add('warn', `item ${id} (${s.field}) is in Item.java but not in data/items.json`);
      continue;
    }
    checked++;
    const label = `item ${id} (${m.name || s.field})`;
    if (s.icon && m.icon && (s.icon.x !== m.icon.x || s.icon.y !== m.icon.y)) {
      add('error', `${label}: icon is ${m.icon.x},${m.icon.y} in data/items.json, ` +
        `${s.icon.x},${s.icon.y} in Item.java`);
    }
    const want = itemProperties(readCls, s.cls, s.args, s.builders);
    if (!want) {
      add('warn', `${label}: the constructor chain of ${s.cls} could not be read`);
      continue;
    }
    const where = `${s.cls}'s constructor chain`;
    checkProperty(add, label, 'stack size', m.stackSize, want.stackSize, where);
    checkProperty(add, label, 'durability', m.durability, want.durability, where);
    checkProperty(add, label, 'attack damage', m.attackDamage, want.attackDamage, where);
    checkProperty(add, label, 'heal', m.heal, want.heal, where);
  }
  for (const i of data.items) {
    if (!items.has(i.id)) add('warn', `item ${i.id} (${i.name}) is in data/items.json but was not found in Item.java`);
  }
  return { checked, fields };
}

function compareEntities(source, data, add) {
  const src = readClass(source, 'EntityList');
  if (!src) return add('warn', 'EntityList.java not found in the source tree');
  const entities = parseEntities(src);
  const mine = new Map(data.entities.map((e) => [e.name, e]));

  let checked = 0;
  for (const [name, s] of entities) {
    const m = mine.get(name);
    if (!m) {
      add('warn', `entity "${name}" is in EntityList.java but not in data/entities.json`);
      continue;
    }
    checked++;
    if (m.networkId !== s.networkId) {
      add('error', `entity "${name}": network id is ${m.networkId} in data/entities.json, ` +
        `${s.networkId} in EntityList.java`);
    }
    const want = mobHealth((cls) => readClass(source, cls), s.cls);
    const label = `entity "${name}"`;
    if (want && want.unknown) {
      if (m.health != null) {
        add('error', `${label}: health is ${m.health} in data/entities.json, but the source ` +
          `gives no single figure (${want.unknown})`);
      }
    } else {
      checkProperty(add, label, 'health', m.health, want ? want.health : null, `${s.cls}'s constructor chain`);
    }
  }
  return { checked };
}

function compareSmelting(source, data, blockFields, itemFields, add) {
  const src = readClass(source, 'FurnaceRecipes');
  if (!src) return add('warn', 'FurnaceRecipes.java not found in the source tree');
  const recipes = parseSmelting(src, blockFields, itemFields);
  const key = (r) => `${r.input.block ?? 'i' + r.input.item}>${idOf(r.output)}`;
  const mine = new Set(data.smelting.map((r) => key(r)));

  let checked = 0;
  for (const r of recipes) {
    if (mine.has(key(r))) checked++;
    else add('error', `smelting ${JSON.stringify(r.input)} -> ${JSON.stringify(r.output)} ` +
      `is in FurnaceRecipes.java but not in data/smelting.json`);
  }
  if (data.smelting.length > recipes.length) {
    add('warn', `data/smelting.json has ${data.smelting.length} recipes, FurnaceRecipes.java registers ${recipes.length}`);
  }
  return { checked };
}

/**
 * Crafting is checked by output, not by pattern: the point is to notice recipes
 * that never reached data/ at all, and outputs that reached it from nowhere.
 *
 * data/recipes.json is produced by *running* the registration bytecode (see
 * tools/extract/interp.py). Reading the decompiled Java is a genuinely separate
 * derivation, which is what makes the comparison worth anything -- so the
 * generator classes are read here too rather than waved through.
 */
const GENERATORS = ['RecipesTools', 'RecipesWeapons', 'RecipesIngots', 'RecipesFood',
                    'RecipesCrafting', 'RecipesArmor', 'RecipesDyes'];

/** Top-level `{...}` groups of a `new Object[][]{{a, b}, {c, d}}` literal. */
function tableGroups(rhs) {
  const start = rhs.indexOf('{');
  if (start < 0) return [];
  const groups = [];
  let depth = 0;
  let from = 0;
  for (let i = start; i < rhs.length; i++) {
    if (rhs[i] === '{') {
      if (++depth === 2) from = i + 1;
    } else if (rhs[i] === '}') {
      if (depth-- === 2) groups.push(rhs.slice(from, i));
      if (depth === 0) break;
    }
  }
  return groups;
}

/** Every recipe output a class names, whether written out or built in a loop. */
function recipeOutputs(src, blockFields, itemFields) {
  const outputs = new Set();
  const take = (text) => {
    const ref = resolveRef(text, blockFields, itemFields);
    if (ref) outputs.add(idOf(ref));
  };

  const re = /add(?:Shapeless)?Recipe\(\s*((?:new ItemStack\(\s*)?(?:Block|Item)\.\w+)/g;
  let m;
  while ((m = re.exec(src))) take(m[1].includes('new ItemStack') ? m[1] : `new ItemStack(${m[1]}`);

  // The loop-driven generators keep their outputs in a material table. Where
  // the class also declares recipePatterns, the table's first row is the set
  // of materials -- ingredients, not outputs -- and every later row is a row
  // of results. RecipesIngots has no patterns and both columns are outputs.
  const table = /recipeItems\s*=\s*(new Object\[\]\[\]\{[\s\S]*?\});/.exec(src);
  if (table) {
    const groups = tableGroups(table[1]);
    const rows = /recipePatterns/.test(src) ? groups.slice(1) : groups;
    for (const row of rows) {
      const rr = /(?:new ItemStack\(\s*)?(?:Block|Item)\.\w+/g;
      let g;
      while ((g = rr.exec(row))) {
        take(g[0].includes('new ItemStack') ? g[0] : `new ItemStack(${g[0]}`);
      }
    }
  }
  return outputs;
}

function compareRecipes(source, data, blockFields, itemFields, add) {
  const src = readClass(source, 'CraftingManager');
  if (!src) return add('warn', 'CraftingManager.java not found in the source tree');

  const outputs = recipeOutputs(src, blockFields, itemFields);
  const missingClasses = [];
  for (const g of GENERATORS) {
    if (!src.includes(`new ${g}()`)) continue;
    const gsrc = readClass(source, g);
    if (!gsrc) {
      missingClasses.push(g);
      continue;
    }
    for (const id of recipeOutputs(gsrc, blockFields, itemFields)) outputs.add(id);
  }
  if (missingClasses.length) {
    add('warn', `${missingClasses.join(', ')} not found in the source tree, so those ` +
      `recipes were not cross-checked`);
  }

  const mine = new Set(data.recipes.map((r) => idOf(r.output)));
  let checked = 0;
  for (const id of outputs) {
    if (mine.has(id)) checked++;
    else add('error', `the source registers a crafting recipe producing id ${id}, ` +
      `but data/recipes.json has none`);
  }
  for (const id of mine) {
    if (!outputs.has(id)) {
      add('error', `data/recipes.json has a recipe producing id ${id}, which no ` +
        `addRecipe call or material table in the source names as an output`);
    }
  }
  return { checked };
}

// ---------------------------------------------------------------------------

/**
 * Verify data/ against the source tree.
 *
 * Returns { ran, summary, problems }. When the source is not installed this is
 * a no-op with ran: false - the wiki is expected to build without it.
 */
export function verifyData(source, data) {
  const problems = [];
  const add = (level, message) => problems.push({ page: 'data/', level, message });
  if (!source.ok) return { ran: false, summary: source.reason, problems };

  const blocks = compareBlocks(source, data, add) || {};
  const items = compareItems(source, data, add) || {};
  const entities = compareEntities(source, data, add) || {};
  const blockFields = blocks.fields || new Map();
  const itemFields = items.fields || new Map();
  const smelting = compareSmelting(source, data, blockFields, itemFields, add) || {};
  const recipes = compareRecipes(source, data, blockFields, itemFields, add) || {};

  const summary = `${blocks.checked || 0} blocks, ${items.checked || 0} items, ` +
    `${entities.checked || 0} entities, ${smelting.checked || 0} smelting, ` +
    `${recipes.checked || 0} crafting outputs`;
  return { ran: true, summary, problems };
}
