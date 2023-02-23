export function formatPercentage(f) {
  return (f * 100).toFixed(1) + ' %';
}

export function formatHash(h) {
  return h.slice(0, 4) + '...' + h.slice(h.length - 2);
}

function splitLastThreeCharacters(s) {
  const i = Math.max(s.length - 3, 0);
  const start = s.slice(0, i);
  const end = s.slice(i, s.length);
  return [start, end];
}

export function formatNumber(x) {
  let s = x.toString();
  let r;
  [s, r] = splitLastThreeCharacters(s);
  while (s.length > 0) {
    let part;
    [s, part] = splitLastThreeCharacters(s);
    r = part + "'" + r;
  }
  return r;
}

export function isAddress(h) {
  const pattern = /0x[0-9a-fA-F]{40}/;
  return pattern.test(h);
}
