(() => {
  const items = [...document.querySelectorAll('[data-research-item]')];
  const search = document.querySelector('#research-search');
  const year = document.querySelector('#research-year');
  const type = document.querySelector('#research-type');
  const count = document.querySelector('#research-count');
  if (!items.length || !search || !year || !type || !count) return;

  const filter = () => {
    const query = search.value.trim().toLowerCase();
    let visible = 0;
    for (const item of items) {
      const match = (!query || item.dataset.search.includes(query))
        && (!year.value || item.dataset.year === year.value)
        && (!type.value || item.dataset.type === type.value);
      item.hidden = !match;
      if (match) visible += 1;
    }
    count.textContent = `${visible} ${visible === 1 ? 'work' : 'works'} shown`;
  };

  search.addEventListener('input', filter);
  year.addEventListener('change', filter);
  type.addEventListener('change', filter);
  filter();
})();

