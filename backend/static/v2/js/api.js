/* API — fetch wrapper for Casa Biônica backend */

const API = {
  // Base URL — auto-detects Railway or localhost
  baseUrl: (() => {
    if (window.location.hostname.includes('railway.app')) {
      return ''; // Same origin on Railway
    }
    return 'https://backend-production-607f.up.railway.app';
  })(),

  async get(path) {
    const url = `${this.baseUrl}${path}`;
    const res = await fetch(url, {
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`API ${res.status}: ${text}`);
    }
    return res.json();
  },

  async post(path, body) {
    const url = `${this.baseUrl}${path}`;
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`API ${res.status}: ${text}`);
    }
    return res.json();
  },

  async healthCheck() {
    try {
      const res = await fetch(`${this.baseUrl}/health`);
      return res.ok;
    } catch {
      return false;
    }
  }
};
