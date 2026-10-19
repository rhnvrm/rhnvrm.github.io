(() => {
  const rows = [...document.querySelectorAll('[data-project]')];
  if (!rows.length) return;
  document.querySelector('.project-filters').hidden = false;
  const query = document.getElementById('project-query');
  const language = document.getElementById('project-language');
  const status = document.getElementById('project-status');
  const owner = document.getElementById('project-owner');
  const update = () => {
    const words = query.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const row of rows) {
      const text = row.textContent.toLowerCase();
      row.hidden = !words.every(word => text.includes(word)) ||
        (language.value && row.dataset.language !== language.value) ||
        (status.value && row.dataset.status !== status.value) ||
        (owner.value && row.dataset.owner !== owner.value);
      if (!row.hidden) count++;
    }
    document.getElementById('project-count').textContent = `${count} of ${rows.length} projects · ordered by last push`;
    document.getElementById('project-empty').hidden = count !== 0;
  };
  [query, language, status, owner].forEach(el => el.addEventListener('input', update));
})();
