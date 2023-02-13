export function formatPercentage(f) {
  return (f * 100).toFixed(1) + ' %';
}

export function formatHash(h) {
  return h.slice(0, 4) + '...' + h.slice(h.length - 2);
}

export function formatNumber(x) {
  return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, "'");
}

export function isAddress(h) {
  const pattern = /0x[0-9a-fA-F]{40}/;
  return pattern.test(h);
}
