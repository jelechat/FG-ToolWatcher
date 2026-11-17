// Adaptateur pywebview -> contrat Electron `window.toolwatcher`.
(function () {
  'use strict';
  var ready = new Promise(function (resolve, reject) {
    if (window.pywebview && window.pywebview.api) return resolve();
    var timeout = setTimeout(function () {
      reject(new Error('pywebview API not available after 5s'));
    }, 5000);
    window.addEventListener('pywebviewready', function () {
      clearTimeout(timeout);
      resolve();
    }, { once: true });
  });
  window.toolwatcher = {
    getInfo: function () { return ready.then(function () { return window.pywebview.api.get_info(); }); },
    openExternal: function (url) { return ready.then(function () { return window.pywebview.api.open_external(url); }); },
    onNavigate: function (callback) {
      var handler = function (event) {
        if (typeof event.detail === 'string') callback(event.detail);
      };
      window.addEventListener('toolwatcher:navigate', handler);
      return function () { window.removeEventListener('toolwatcher:navigate', handler); };
    }
  };
})();
