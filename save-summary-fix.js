// Compatibility fix for expedition-22 autosaves.
// game.js calls saveSummary(auto) when an autosave exists, while its
// internal formatter is named saveDescription(). Keep the menu startup
// path alive without altering saved expedition data.
(() => {
  'use strict';
  if (typeof globalThis.saveSummary === 'function') return;
  globalThis.saveSummary = save => {
    if (!save || !save.meta) return '';
    const m = save.meta;
    const money = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(m.money || 0);
    return `${m.location || 'Arctic Ocean'} · ${m.vessel || 'Research Vessel'} · ${m.missions || 0} missions · ${money}`;
  };
})();
