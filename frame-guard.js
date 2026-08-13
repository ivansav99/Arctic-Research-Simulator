(() => {
  'use strict';

  const nativeRAF = window.requestAnimationFrame.bind(window);
  let lastError = '';
  let errorCount = 0;

  function report(error, source = 'MAIN MAP') {
    const message = String(error?.message || error || 'Unknown error').slice(0, 180);
    const signature = `${source}: ${message}`;
    if (signature !== lastError) {
      lastError = signature;
      console.error(signature, error);
    }
    errorCount += 1;
    document.documentElement.dataset.arMapError = signature;
    const warning = document.getElementById('resource-warning');
    if (warning) {
      warning.textContent = `MAP ERROR · ${message}`;
      warning.classList.add('show');
    }
  }

  window.addEventListener('error', event => {
    if (event?.error) report(event.error, 'WINDOW');
  });
  window.addEventListener('unhandledrejection', event => {
    report(event?.reason || 'Unhandled promise rejection', 'PROMISE');
  });

  window.requestAnimationFrame = callback => {
    const run = time => {
      try {
        callback(time);
      } catch (error) {
        report(error, 'FRAME');
        nativeRAF(run);
      }
    };
    return nativeRAF(run);
  };

  window.ARFrameGuard = {
    get errorCount() { return errorCount; },
    get lastError() { return lastError; }
  };
})();
