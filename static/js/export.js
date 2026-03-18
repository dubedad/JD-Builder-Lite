/**
 * Export module for PDF and Word document generation.
 * Handles: building export request, preview navigation, file downloads.
 */

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast--${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button class="toast-dismiss" aria-label="Dismiss">
      <svg width="16" height="16" viewBox="0 0 16 16">
        <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="2"/>
      </svg>
    </button>
  `;

  // Dismiss on click
  toast.querySelector('.toast-dismiss').addEventListener('click', () => toast.remove());

  container.appendChild(toast);

  // Auto-dismiss after 5 seconds
  setTimeout(() => toast.remove(), 5000);
}

const exportModule = {
  // Cached export data for downloads
  currentExportData: null,
  // Saved page state for back navigation
  savedPageContent: null,
  savedPageStyles: null,
  // Export options (classification inclusion)
  _exportOptions: null,

  /**
   * Build export request from current state
   */
  buildExportRequest() {
    const state = store.getState();
    const profile = window.currentProfile;
    const overview = window.generation?.getOverview();

    if (!profile) {
      throw new Error('No profile loaded');
    }

    // Build selections with metadata
    const selections = [];
    const now = new Date().toISOString();

    Object.entries(state.selections).forEach(([sectionId, selectedIds]) => {
      if (!selectedIds || selectedIds.length === 0) return;
      const now_ts = state.selectionTimestamps || {};

      if (sectionId === 'core_competencies') {
        // Plain strings at profile.reference_attributes.core_competencies[]
        const ccItems = profile.reference_attributes?.core_competencies || [];
        selectedIds.forEach(stmtId => {
          const index = parseInt(stmtId.split('-').pop(), 10);
          const text = ccItems[index];
          if (text !== undefined && text !== '') {
            selections.push({
              id: stmtId,
              text: text,
              jd_element: 'core_competencies',
              source_attribute: 'Core Competencies',
              source_url: null,
              selected_at: now_ts[stmtId] || now,
              description: null,
              proficiency: null
            });
          }
        });

      } else if (sectionId === 'abilities' || sectionId === 'knowledge') {
        // Filtered sub-array of profile.skills.statements by source_attribute
        const sourceAttr = sectionId === 'abilities' ? 'Abilities' : 'Knowledge';
        const filtered = (profile.skills?.statements || []).filter(s => s.source_attribute === sourceAttr);
        selectedIds.forEach(stmtId => {
          const index = parseInt(stmtId.split('-').pop(), 10);
          const stmt = filtered[index];
          if (stmt) {
            selections.push({
              id: stmtId,
              text: stmt.text,
              jd_element: 'skills',
              source_attribute: sourceAttr,
              source_url: stmt.source_url || null,
              selected_at: now_ts[stmtId] || now,
              description: stmt.description || null,
              proficiency: stmt.proficiency || null
            });
          }
        });

      } else {
        // Standard path: profile[sectionId].statements[]
        const sectionData = profile[sectionId];
        if (!sectionData || !sectionData.statements) return;
        selectedIds.forEach(stmtId => {
          const index = parseInt(stmtId.split('-').pop(), 10);
          const stmt = sectionData.statements[index];
          if (stmt) {
            selections.push({
              id: stmtId,
              text: stmt.text,
              jd_element: sectionId,
              source_attribute: stmt.source_attribute,
              source_url: stmt.source_url || null,
              selected_at: now_ts[stmtId] || now,
              description: stmt.description || null,
              proficiency: stmt.proficiency || null
            });
          }
        });
      }
    });

    // Build AI metadata from session if available
    let aiMetadata = null;
    if (overview?.generated && window.aiGenerationMetadata) {
      aiMetadata = {
        model: window.aiGenerationMetadata.model,
        timestamp: window.aiGenerationMetadata.timestamp,
        prompt_version: window.aiGenerationMetadata.prompt_version,
        input_statement_ids: window.aiGenerationMetadata.input_statement_ids,
        modified: overview.modified
      };
    }

    // Convert scraped_at to ISO format if needed (API returns RFC 2822 format)
    let scrapedAt = profile.metadata.scraped_at;
    if (scrapedAt && !scrapedAt.includes('T')) {
      // Parse RFC 2822 format and convert to ISO 8601
      scrapedAt = new Date(scrapedAt).toISOString();
    }

    const request = {
      noc_code: profile.noc_code,
      job_title: profile.title,
      general_overview: overview?.generated ? overview.text : null,
      selections: selections,
      ai_metadata: aiMetadata,
      source_metadata: {
        noc_code: profile.metadata.noc_code,
        profile_url: profile.metadata.profile_url,
        scraped_at: scrapedAt,
        version: profile.metadata.version,
        // Per-section provenance for TBS Directive 32592 compliance (Phase 22)
        section_sources: {
          key_activities: profile.key_activities?.data_source || 'oasis',
          skills: profile.skills?.data_source || 'oasis',
          effort: profile.effort?.data_source || 'oasis',
          responsibility: profile.responsibility?.data_source || 'oasis',
          working_conditions: profile.working_conditions?.data_source || 'oasis',
        }
      }
    };

    // Add classification data if export options specify
    if (this._exportOptions?.include_classification && this._exportOptions?.classification_result) {
      request.classification_result = this._exportOptions.classification_result;
      request.include_classification = true;
    }

    return request;
  },

  /**
   * Show export options modal if classification exists, else go straight to preview
   */
  showExportOptions() {
    // Check if classification data exists (from classify.js)
    const allocation = typeof classifyModule !== 'undefined' ? classifyModule.getCurrentAllocation() : null;

    // If no classification exists, export JD only (no checkboxes needed)
    if (!allocation) {
      this.showPreview();
      return;
    }

    // Create checkbox modal
    const overlay = document.createElement('div');
    overlay.className = 'export-options-overlay';
    overlay.innerHTML = `
      <div class="export-options-modal">
        <h3>Export Options</h3>
        <p>Choose what to include in your export:</p>
        <label class="export-option-checkbox">
          <input type="checkbox" id="export-include-jd" checked>
          <span>Include Job Description</span>
        </label>
        <label class="export-option-checkbox">
          <input type="checkbox" id="export-include-classification" checked>
          <span>Include Classification Results</span>
        </label>
        <div class="export-options-actions">
          <button class="btn btn--primary" id="export-options-confirm">Continue to Preview</button>
          <button class="btn btn--text" id="export-options-cancel">Cancel</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    overlay.querySelector('#export-options-confirm').addEventListener('click', () => {
      const includeJd = overlay.querySelector('#export-include-jd').checked;
      const includeClassification = overlay.querySelector('#export-include-classification').checked;
      overlay.remove();

      // Store choices for export request
      this._exportOptions = {
        include_classification: includeClassification,
        classification_result: includeClassification ? allocation : null,
        include_jd: includeJd
      };
      this.showPreview();
    });

    overlay.querySelector('#export-options-cancel').addEventListener('click', () => {
      overlay.remove();
    });
  },

  /**
   * Navigate to preview page
   */
  async showPreview() {
    console.log('[DEBUG export.js] showPreview called');
    try {
      console.log('[DEBUG export.js] Building export request...');
      const exportData = this.buildExportRequest();
      console.log('[DEBUG export.js] Export data built:', exportData);

      // Store for downloads
      this.currentExportData = exportData;

      // Track if we should show empty warning after preview loads
      this._showEmptyWarning = exportData.selections.length === 0;

      // Save current page state before showing preview
      this.savedPageContent = document.body.innerHTML;
      this.savedPageStyles = document.head.innerHTML;

      // Fetch preview HTML
      const response = await fetch('/api/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(exportData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.error || 'Preview failed');
      }

      // Parse preview HTML and extract body content
      const html = await response.text();
      const parser = new DOMParser();
      const previewDoc = parser.parseFromString(html, 'text/html');

      // Add preview styles to head (keeping original styles)
      const previewStyles = previewDoc.querySelectorAll('link[rel="stylesheet"]');
      previewStyles.forEach(style => {
        if (!document.querySelector(`link[href="${style.getAttribute('href')}"]`)) {
          document.head.appendChild(style.cloneNode(true));
        }
      });

      // Replace body content with preview
      document.body.innerHTML = previewDoc.body.innerHTML;
      document.body.className = previewDoc.body.className;

      // Re-attach event listeners after content replacement
      this.attachPreviewListeners();

      // Show empty selection warning after preview loads (per CONTEXT.md - warning, not blocking)
      if (this._showEmptyWarning) {
        showToast('Warning: No statements selected. Export will contain only header information.', 'warning');
        this._showEmptyWarning = false;
      }

    } catch (error) {
      console.error('[DEBUG export.js] Preview error:', error);
      console.error('[DEBUG export.js] Error stack:', error.stack);
      showToast('Failed to generate preview: ' + error.message, 'error');
    }
  },

  /**
   * Attach event listeners on preview page
   */
  attachPreviewListeners() {
    // Bind Return to Builder button
    const returnBtn = document.getElementById('return-to-builder-btn');
    if (returnBtn) {
      returnBtn.addEventListener('click', () => this.returnToBuilder());
    }

    // Bind Classify button
    const classifyBtn = document.getElementById('preview-classify-btn');
    if (classifyBtn) {
      classifyBtn.addEventListener('click', () => this.classifyFromPreview());
    }

    // Bind breadcrumb "Builder" step click
    const builderStep = document.querySelector('.step--completed.step--clickable');
    if (builderStep) {
      builderStep.addEventListener('click', () => this.returnToBuilder());
    }

    // Dropdown toggle
    const exportBtn = document.getElementById('preview-export-btn');
    const dropdown = document.getElementById('export-dropdown');
    const menu = dropdown?.querySelector('.export-dropdown-menu');

    if (exportBtn && menu) {
      exportBtn.addEventListener('click', () => {
        const isOpen = menu.getAttribute('data-open') === 'true';
        menu.setAttribute('data-open', !isOpen);
        exportBtn.setAttribute('aria-expanded', !isOpen);
      });

      // Close on click outside
      document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) {
          menu.setAttribute('data-open', 'false');
          exportBtn.setAttribute('aria-expanded', 'false');
        }
      });

      // Handle export option clicks
      menu.querySelectorAll('.export-option').forEach(option => {
        option.addEventListener('click', (e) => {
          const format = option.dataset.format;
          menu.setAttribute('data-open', 'false');
          exportBtn.setAttribute('aria-expanded', 'false');

          if (format === 'pdf') {
            this.downloadPDF();
          } else if (format === 'docx') {
            this.downloadDOCX();
          }
        });
      });
    }
  },

  /**
   * Return to builder (profile page) with state preserved
   *
   * Note: We reload the page because innerHTML restoration doesn't properly
   * reinitialize the stepper, tabs, and accordion modules. State is preserved
   * in localStorage so selections will be restored.
   */
  returnToBuilder() {
    // Set flag so page reload restores to profile (Step 3) instead of search
    sessionStorage.setItem('jdb_return_to_profile', '1');
    window.location.reload();
  },

  /**
   * Navigate to classification from preview screen
   */
  classifyFromPreview() {
    // Set flag so main.js knows to navigate to Step 5 on reload
    sessionStorage.setItem('jdb_return_to_classify', '1');
    window.location.reload();
  },

  /**
   * Generate filename per CONTEXT.md format:
   * {NOC code} - {Title} - {date} - Job Description.{ext}
   */
  _generateFilename(ext) {
    const data = this.currentExportData;
    const date = new Date().toISOString().split('T')[0];
    const safeTitle = data.job_title.replace(/[<>:"/\\|?*]/g, '').substring(0, 50);
    return `${data.noc_code} - ${safeTitle} - ${date} - Job Description.${ext}`;
  },

  /**
   * Download blob as file
   */
  _downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  /**
   * Download PDF
   */
  async downloadPDF() {
    if (!this.currentExportData) {
      showToast('No export data available. Open preview first.', 'warning');
      return;
    }
    // btn may be null when called from modal (old preview-export-btn only exists on preview page)
    const btn = document.getElementById('preview-export-btn');

    if (btn) btn.classList.add('export-btn--loading');
    const btnText = btn?.querySelector('.export-btn-text');
    if (btnText) btnText.textContent = 'Generating PDF...';

    try {
      const response = await fetch('/api/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.currentExportData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.error || 'PDF generation failed');
      }

      // Get filename from header or generate
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = this._generateFilename('pdf');
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }

      // Download
      const blob = await response.blob();
      this._downloadBlob(blob, filename);
      showToast('PDF downloaded successfully', 'success');

    } catch (error) {
      console.error('PDF download error:', error);
      showToast('Failed to generate PDF: ' + error.message, 'error');
    } finally {
      if (btn) btn.classList.remove('export-btn--loading');
      const btnTextFinal = btn?.querySelector('.export-btn-text');
      if (btnTextFinal) btnTextFinal.textContent = 'Export Job Description';
    }
  },

  /**
   * Download Word document
   */
  async downloadDOCX() {
    if (!this.currentExportData) {
      showToast('No export data available. Open preview first.', 'warning');
      return;
    }
    // btn may be null when called from modal (old preview-export-btn only exists on preview page)
    const btn = document.getElementById('preview-export-btn');

    if (btn) btn.classList.add('export-btn--loading');
    const btnText = btn?.querySelector('.export-btn-text');
    if (btnText) btnText.textContent = 'Generating Word...';

    try {
      const response = await fetch('/api/export/docx', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.currentExportData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.error || 'Word generation failed');
      }

      // Get filename from header or generate
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = this._generateFilename('docx');
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }

      // Download
      const blob = await response.blob();
      this._downloadBlob(blob, filename);
      showToast('Word document downloaded successfully', 'success');

    } catch (error) {
      console.error('DOCX download error:', error);
      showToast('Failed to generate Word document: ' + error.message, 'error');
    } finally {
      if (btn) btn.classList.remove('export-btn--loading');
      const btnTextFinal = btn?.querySelector('.export-btn-text');
      if (btnTextFinal) btnTextFinal.textContent = 'Export Job Description';
    }
  },

  /**
   * Assemble JD preview HTML from current selections and profile data (client-side, no API call)
   */
  assembleJDPreview() {
    const state = store.getState();
    const profile = window.currentProfile;
    if (!profile) return '<p>No profile loaded.</p>';

    // All 8 sections in display order
    const ALL_SECTIONS = [
      { key: 'core_competencies', label: 'Core Competencies' },
      { key: 'key_activities', label: 'Key Activities' },
      { key: 'skills', label: 'Skills' },
      { key: 'abilities', label: 'Abilities' },
      { key: 'knowledge', label: 'Knowledge' },
      { key: 'effort', label: 'Effort' },
      { key: 'responsibility', label: 'Responsibility' },
      { key: 'working_conditions', label: 'Working Conditions' }
    ];

    let html = '';

    // Title and NOC code header
    html += `<div class="preview-jd__header">`;
    html += `<h3 class="preview-jd__title">${this._escapeHtml(profile.title)}</h3>`;
    html += `<span class="preview-jd__noc">NOC ${this._escapeHtml(profile.noc_code)}</span>`;
    if (profile.reference_attributes?.lead_statement) {
      html += `<p class="preview-jd__lead">${this._escapeHtml(profile.reference_attributes.lead_statement)}</p>`;
    }
    html += `</div>`;

    // Position title if set
    const posTitle = state.positionTitle;
    if (posTitle) {
      html += `<div class="preview-jd__position"><strong>Position Title:</strong> ${this._escapeHtml(posTitle)}</div>`;
    }

    // Overview text if generated
    const overview = window.generation?.getOverview ? window.generation.getOverview() : null;
    if (overview?.generated && overview.text) {
      html += `<div class="preview-jd__section">`;
      html += `<h4>Position Overview</h4>`;
      html += `<p>${this._escapeHtml(overview.text)}</p>`;
      html += `</div>`;
    }

    // Each section with selected items
    ALL_SECTIONS.forEach(({ key, label }) => {
      const selectedIds = state.selections[key] || [];
      if (selectedIds.length === 0) return;

      html += `<div class="preview-jd__section">`;
      html += `<h4>${label} <span class="preview-jd__count">(${selectedIds.length})</span></h4>`;
      html += `<ul class="preview-jd__list">`;

      selectedIds.forEach(stmtId => {
        const index = parseInt(stmtId.split('-').pop(), 10);
        let text = '';

        // PITFALL: core_competencies items are plain strings in profile.reference_attributes.core_competencies[idx]
        if (key === 'core_competencies') {
          const ccItems = profile.reference_attributes?.core_competencies || [];
          text = ccItems[index] || '';
        }
        // PITFALL: abilities/knowledge use filtered sub-arrays by source_attribute
        else if (key === 'abilities' || key === 'knowledge') {
          const sourceAttr = key === 'abilities' ? 'Abilities' : 'Knowledge';
          const filtered = (profile.skills?.statements || []).filter(s => s.source_attribute === sourceAttr);
          text = filtered[index]?.text || '';
        } else {
          const sectionData = profile[key];
          if (sectionData?.statements?.[index]) {
            text = sectionData.statements[index].text;
          }
        }

        if (text) {
          html += `<li>${this._escapeHtml(text)}</li>`;
        }
      });

      html += `</ul></div>`;
    });

    if (Object.values(state.selections).every(arr => arr.length === 0)) {
      html += `<p class="preview-jd__empty">No statements selected yet. Return to the builder to make selections.</p>`;
    }

    return html;
  },

  /**
   * Escape HTML special characters to prevent XSS
   */
  _escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
  },

  /**
   * Download JSON audit trail
   */
  async downloadJSON() {
    if (!this.currentExportData) {
      showToast('No export data available. Please complete your selections first.', 'warning');
      return;
    }
    const btn = document.getElementById('export-download-json');
    const btnSpan = btn?.querySelector('span');
    if (btn) btn.disabled = true;
    if (btnSpan) btnSpan.textContent = 'Generating…';

    try {
      const response = await fetch('/api/export/json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.currentExportData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.error || 'JSON export failed');
      }

      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = this._generateFilename('json').replace('Job Description', 'Audit Trail');
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }

      const blob = await response.blob();
      this._downloadBlob(blob, filename);
      showToast('Audit trail downloaded successfully', 'success');

    } catch (error) {
      console.error('JSON export error:', error);
      showToast('Failed to export audit trail: ' + error.message, 'error');
    } finally {
      if (btn) btn.disabled = false;
      if (btnSpan) btnSpan.textContent = 'Download Full Audit Trail (JSON)';
    }
  },

  /**
   * Open the JD preview modal and assemble content
   */
  openPreviewModal() {
    const modal = document.getElementById('jd-preview-modal');
    const body = document.getElementById('preview-modal-body');
    if (!modal || !body) return;

    // Assemble JD content
    body.innerHTML = this.assembleJDPreview();

    // Prepare export data for PDF/Word buttons
    try {
      this.currentExportData = this.buildExportRequest ? this.buildExportRequest() : null;
    } catch (e) {
      console.warn('[export.js] Could not build export data:', e.message);
    }

    // Show modal
    modal.classList.remove('hidden');
    document.body.classList.add('modal-open');

    // Focus trap: focus the close button
    document.getElementById('preview-return-btn')?.focus();
  },

  /**
   * Close the JD preview modal
   */
  closePreviewModal() {
    const modal = document.getElementById('jd-preview-modal');
    if (!modal) return;
    modal.classList.add('hidden');
    document.body.classList.remove('modal-open');
  }
};

// Export for other modules
window.exportModule = exportModule;

/**
 * Global click handler for Create button (backup for event listener)
 */
function handleCreateClick() {
  console.log('[DEBUG export.js] handleCreateClick called via onclick');
  const createBtn = document.getElementById('create-btn');
  if (createBtn && createBtn.disabled) {
    console.log('[DEBUG export.js] Button is disabled, returning');
    alert('Please select some statements first by checking the checkboxes.');
    return;
  }
  console.log('[DEBUG export.js] Calling showExportOptions...');
  try {
    exportModule.showExportOptions();
  } catch (error) {
    console.error('[DEBUG export.js] Error in showExportOptions:', error);
    alert('Error: ' + error.message);
  }
}

// Make it globally available
window.handleCreateClick = handleCreateClick;

/**
 * Initialize export functionality
 */
function initExport() {
  console.log('[DEBUG export.js] initExport called');
  // Listen for Create button click
  const createBtn = document.getElementById('create-btn');
  console.log('[DEBUG export.js] createBtn found:', !!createBtn);
  if (createBtn) {
    createBtn.addEventListener('click', () => {
      console.log('[DEBUG export.js] Create button clicked via addEventListener!');
      console.log('[DEBUG export.js] Button disabled:', createBtn.disabled);
      if (!createBtn.disabled) {
        exportModule.showExportOptions();
      }
    });
  }

  // Listen for open-preview-modal event (dispatched by nav bar button in main.js)
  document.addEventListener('open-preview-modal', () => {
    exportModule.openPreviewModal();
  });

  // Preview modal buttons
  const previewReturnBtn = document.getElementById('preview-return-btn');
  if (previewReturnBtn) {
    previewReturnBtn.addEventListener('click', () => exportModule.closePreviewModal());
  }

  const previewAdvanceBtn = document.getElementById('preview-advance-classify');
  if (previewAdvanceBtn) {
    previewAdvanceBtn.addEventListener('click', () => {
      exportModule.closePreviewModal();
      window.jdStepper.goToStep(3);
    });
  }

  const previewPdfBtn = document.getElementById('preview-export-pdf');
  if (previewPdfBtn) {
    previewPdfBtn.addEventListener('click', () => exportModule.downloadPDF());
  }

  const previewWordBtn = document.getElementById('preview-export-word');
  if (previewWordBtn) {
    previewWordBtn.addEventListener('click', () => exportModule.downloadDOCX());
  }

  // Close modal on overlay click
  const modalOverlay = document.querySelector('.jd-preview-modal__overlay');
  if (modalOverlay) {
    modalOverlay.addEventListener('click', () => exportModule.closePreviewModal());
  }

  // Close modal on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const modal = document.getElementById('jd-preview-modal');
      if (modal && !modal.classList.contains('hidden')) {
        exportModule.closePreviewModal();
      }
    }
  });

  // Export page (Step 5) download buttons
  const exportPagePdfBtn = document.getElementById('export-download-pdf');
  if (exportPagePdfBtn) {
    exportPagePdfBtn.addEventListener('click', () => exportModule.downloadPDF());
  }
  const exportPageDocxBtn = document.getElementById('export-download-docx');
  if (exportPageDocxBtn) {
    exportPageDocxBtn.addEventListener('click', () => exportModule.downloadDOCX());
  }
  const exportPageJsonBtn = document.getElementById('export-download-json');
  if (exportPageJsonBtn) {
    exportPageJsonBtn.addEventListener('click', () => exportModule.downloadJSON());
  }
}

window.initExport = initExport;

/**
 * Populate the Export page (Step 5) preview card and wire download buttons.
 * Called by navigateToStep(5) in main.js each time the user arrives at step 5.
 */
function initExportPage() {
  const profile = window.currentProfile;
  const state = store.getState();

  // Title + NOC
  const titleEl = document.getElementById('export-preview-title');
  const nocEl = document.getElementById('export-preview-noc');
  if (titleEl) titleEl.textContent = profile ? profile.title : '—';
  if (nocEl) nocEl.textContent = profile ? `NOC ${profile.noc_code}` : '';

  // Classification badge (if a result exists)
  const classificationBadges = document.getElementById('export-preview-classification');
  if (classificationBadges) {
    const allocation = typeof classifyModule !== 'undefined' ? classifyModule.getCurrentAllocation() : null;
    if (allocation?.recommendations?.length) {
      const top = allocation.recommendations[0];
      const pct = Math.round((top.confidence || 0) * 100);
      classificationBadges.innerHTML =
        `<span class="badge badge--classification">${top.group_code} — ${pct}%</span>`;
      classificationBadges.classList.remove('hidden');
    } else {
      classificationBadges.classList.add('hidden');
    }
  }

  // Overview text (if generated)
  const overviewSection = document.getElementById('export-preview-overview');
  const overviewText = document.getElementById('export-preview-overview-text');
  const overview = window.generation?.getOverview ? window.generation.getOverview() : null;
  if (overview?.generated && overview.text && overviewSection && overviewText) {
    overviewText.textContent = overview.text;
    overviewSection.classList.remove('hidden');
  } else if (overviewSection) {
    overviewSection.classList.add('hidden');
  }

  // Selected statements summary (max 3 per section)
  const selectionsEl = document.getElementById('export-preview-selections');
  if (selectionsEl && profile) {
    const ALL_SECTIONS = [
      { key: 'core_competencies', label: 'Core Competencies' },
      { key: 'key_activities', label: 'Key Activities' },
      { key: 'skills', label: 'Skills' },
      { key: 'abilities', label: 'Abilities' },
      { key: 'knowledge', label: 'Knowledge' },
      { key: 'effort', label: 'Effort' },
      { key: 'responsibility', label: 'Responsibility' },
    ];
    let html = '';
    ALL_SECTIONS.forEach(({ key, label }) => {
      const ids = state.selections[key] || [];
      if (!ids.length) return;
      html += `<p class="export-preview-card__sel-heading">${label} (${ids.length})</p><ul>`;
      ids.slice(0, 3).forEach(stmtId => {
        const index = parseInt(stmtId.split('-').pop(), 10);
        let text = '';
        if (key === 'core_competencies') {
          text = (profile.reference_attributes?.core_competencies || [])[index] || '';
        } else if (key === 'abilities' || key === 'knowledge') {
          const attr = key === 'abilities' ? 'Abilities' : 'Knowledge';
          const filtered = (profile.skills?.statements || []).filter(s => s.source_attribute === attr);
          text = filtered[index]?.text || '';
        } else {
          text = profile[key]?.statements?.[index]?.text || '';
        }
        if (text) html += `<li>${exportModule._escapeHtml(text)}</li>`;
      });
      if (ids.length > 3) {
        html += `<li style="color:#888;font-style:italic;">…and ${ids.length - 3} more</li>`;
      }
      html += '</ul>';
    });
    if (!html) {
      html = '<p style="color:#888;font-style:italic;">No statements selected yet.</p>';
    }
    selectionsEl.innerHTML = html;
  }

  // Build export data for downloads (cached on exportModule)
  try {
    exportModule.currentExportData = exportModule.buildExportRequest();
  } catch (e) {
    console.warn('[export.js] initExportPage: could not build export data:', e.message);
  }
}

window.initExportPage = initExportPage;
