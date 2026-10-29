try { const t = localStorage.getItem('academic-theme'); if (t === 'dark' || t === 'light') document.documentElement.dataset.theme = t; } catch (_) {}
