/**
 * Export module for PDF and Word document generation.
 * Handles: building export request, preview navigation, file downloads.
 */

const exportModule = {
  // Cached export data for downloads
  currentExportData: null,

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
            source_url: stmt.source_url,
            // Use stored timestamp or current time
            selected_at: state.selectionTimestamps?.[stmtId] || now
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

    return {
      noc_code: profile.noc_code,
      job_title: profile.title,
      general_overview: overview?.generated ? overview.text : null,
      selections: selections,
      ai_metadata: aiMetadata,
      source_metadata: {
        noc_code: profile.metadata.noc_code,
        profile_url: profile.metadata.profile_url,
        scraped_at: profile.metadata.scraped_at,
        version: profile.metadata.version
      }
    };
  },

  /**
   * Navigate to preview page
   */
  async showPreview() {
    try {
      const exportData = this.buildExportRequest();

      if (exportData.selections.length === 0) {
        alert('Select at least one statement before creating the job description.');
        return;
      }

      // Store for downloads
      this.currentExportData = exportData;

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

      // Replace page content with preview
      const html = await response.text();
      document.open();
      document.write(html);
      document.close();

      // Re-attach event listeners after page replacement
      this.attachPreviewListeners();

    } catch (error) {
      console.error('Preview error:', error);
      alert('Failed to generate preview: ' + error.message);
    }
  },

  /**
   * Attach event listeners on preview page
   */
  attachPreviewListeners() {
    document.getElementById('download-pdf-btn')?.addEventListener('click', () => this.downloadPDF());
    document.getElementById('download-docx-btn')?.addEventListener('click', () => this.downloadDOCX());
    document.getElementById('back-to-edit-btn')?.addEventListener('click', () => window.location.reload());
  },

  /**
   * Download PDF
   */
  async downloadPDF() {
    const btn = document.getElementById('download-pdf-btn');
    if (!btn || !this.currentExportData) return;

    btn.disabled = true;
    btn.classList.add('btn--loading');
    btn.textContent = 'Generating...';

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

      // Get filename from Content-Disposition header or generate one
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `JD-${this.currentExportData.noc_code}.pdf`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }

      // Download the blob
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

    } catch (error) {
      console.error('PDF download error:', error);
      alert('Failed to download PDF: ' + error.message);
    } finally {
      btn.disabled = false;
      btn.classList.remove('btn--loading');
      btn.textContent = 'Download PDF';
    }
  },

  /**
   * Download Word document
   */
  async downloadDOCX() {
    const btn = document.getElementById('download-docx-btn');
    if (!btn || !this.currentExportData) return;

    btn.disabled = true;
    btn.classList.add('btn--loading');
    btn.textContent = 'Generating...';

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

      // Get filename from Content-Disposition header or generate one
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `JD-${this.currentExportData.noc_code}.docx`;
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }

      // Download the blob
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

    } catch (error) {
      console.error('DOCX download error:', error);
      alert('Failed to download Word document: ' + error.message);
    } finally {
      btn.disabled = false;
      btn.classList.remove('btn--loading');
      btn.textContent = 'Download Word';
    }
  }
};

// Export for other modules
window.exportModule = exportModule;

/**
 * Initialize export functionality
 */
function initExport() {
  // Listen for Create button click
  const createBtn = document.getElementById('create-btn');
  if (createBtn) {
    createBtn.addEventListener('click', () => exportModule.showPreview());
  }
}

window.initExport = initExport;
