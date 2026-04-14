(function () {
  const payload = {
    url: window.location.pathname,
    referrer: document.referrer,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent
  };

  fetch('http://127.0.0.1:8001/track', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
})();