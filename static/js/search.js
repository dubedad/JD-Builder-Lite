// Per-section text filtering
const initSectionSearch = () => {
    // Event delegation for search inputs
    const jdSections = document.querySelector('.jd-sections');
    if (!jdSections) {
        console.warn('initSectionSearch: .jd-sections not found');
        return;
    }
    jdSections.addEventListener('input', (e) => {
        if (e.target.classList.contains('jd-section__search')) {
            filterSection(e.target);
        }
    });
};

const filterSection = (searchInput) => {
    const sectionId = searchInput.dataset.sectionId;
    const section = document.querySelector(`[data-section-id="${sectionId}"]`);
    if (!section) return;

    const term = searchInput.value.toLowerCase().trim();
    const statements = section.querySelectorAll('.statement');

    statements.forEach(stmt => {
        const text = stmt.querySelector('.statement__text').textContent.toLowerCase();
        const source = stmt.querySelector('.statement__source').textContent.toLowerCase();
        const matches = !term || text.includes(term) || source.includes(term);
        stmt.classList.toggle('hidden', !matches);
    });
};

// Export
window.initSectionSearch = initSectionSearch;
