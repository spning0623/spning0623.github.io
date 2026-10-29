const menuButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('#primary-nav');
menuButton?.addEventListener('click', () => {
  const open = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('is-open', open);
});
const themeButton = document.querySelector('.theme-toggle');
function updateThemeLabel() {
  themeButton?.setAttribute('aria-label', document.documentElement.dataset.theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
}
updateThemeLabel();
themeButton?.addEventListener('click', () => {
  const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = theme;
  try { localStorage.setItem('academic-theme', theme); } catch (_) {}
  updateThemeLabel();
});
const search = document.querySelector('#publication-search');
if (search) {
  let category = 'all';
  const papers = [...document.querySelectorAll('.publication')];
  const filters = [...document.querySelectorAll('.filter-button')];
  function filterPublications() {
    const words = search.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    papers.forEach(p => {
      const matches = (category === 'all' || p.dataset.category === category) && words.every(w => p.dataset.search.includes(w));
      p.hidden = !matches;
      if (matches) visible++;
    });
    document.querySelectorAll('.publication-group').forEach(g => { g.hidden = ![...g.querySelectorAll('.publication')].some(p => !p.hidden); });
    document.querySelector('#publication-status').textContent = `${visible} of ${papers.length} publications`;
    document.querySelector('#no-results').hidden = visible !== 0;
  }
  search.addEventListener('input', filterPublications);
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.category;
    filters.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    filterPublications();
  }));
}
