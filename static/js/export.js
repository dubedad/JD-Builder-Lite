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
            // Use stored timestamp or current time
            selected_at: state.selectionTimestamps?.[stmtId] || now,
            // Include description and proficiency for export display
            description: stmt.description || null,
            proficiency: stmt.proficiency || null
          });
        }
      });
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
    const btn = document.getElementById('preview-export-btn');
    if (!btn || !this.currentExportData) return;

    btn.classList.add('export-btn--loading');
    const btnText = btn.querySelector('.export-btn-text');
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
      btn.classList.remove('export-btn--loading');
      const btnText = btn.querySelector('.export-btn-text');
      if (btnText) btnText.textContent = 'Export Job Description';
    }
  },

  /**
   * Download Word document
   */
  async downloadDOCX() {
    const btn = document.getElementById('preview-export-btn');
    if (!btn || !this.currentExportData) return;

    btn.classList.add('export-btn--loading');
    const btnText = btn.querySelector('.export-btn-text');
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
      btn.classList.remove('export-btn--loading');
      const btnText = btn.querySelector('.export-btn-text');
      if (btnText) btnText.textContent = 'Export Job Description';
    }
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
}

window.initExport = initExport;
