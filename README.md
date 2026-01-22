# JD-Builder-Lite

A lightweight, browser-based Job Description Builder with Open Data Oasis API support.

## Features

### 🎨 Modern UI
- Clean, responsive design with gradient styling
- Mobile-friendly interface
- Intuitive form-based input

### 🔄 Workflow Management
- Three-stage workflow: Draft → Review → Published
- Visual workflow indicator
- Easy status transitions

### 📝 Comprehensive Job Description Builder
- **Basic Information**: Job title, company, location, type, salary range
- **Responsibilities**: Dynamic list management
- **Qualifications**: Easy add/remove functionality
- **Skills**: Tag-based skill management with visual chips

### 🔍 Provenance Tracking
- Automatic timestamp tracking (created/modified)
- Version control
- Author attribution
- Status history

### 📤 Multiple Export Formats
- **Preview**: Human-readable text format
- **OData Schema**: OpenAPI/OData compliant JSON schema
- **JSON Export**: Complete data structure
- **Markdown**: Formatted markdown document

### 🌐 Open Data Oasis API Integration
- Compliant with OData/OASIS standards
- OpenAPI schema generation
- RESTful API structure
- Standard metadata format

## Usage

### Quick Start

1. **Open the Application**
   ```bash
   # Simply open index.html in your web browser
   open index.html
   # Or use a local server (recommended)
   python -m http.server 8000
   # Then navigate to http://localhost:8000
   ```

2. **Fill in Job Details**
   - Enter basic job information (title, company, location, etc.)
   - Add responsibilities one by one
   - List required qualifications
   - Add skills as tags

3. **Manage Workflow**
   - Start in "Draft" mode
   - Move to "Review" when ready
   - Publish when finalized

4. **Export Your Job Description**
   - Click "Generate Output" to create exports
   - Switch between Preview, OData Schema, JSON, and Markdown tabs
   - Download or copy to clipboard

### OData Schema

The application generates OpenAPI/OData compliant schemas that include:
- JSON Schema definitions
- Property descriptions and types
- Enumerated values for job types and statuses
- Sample data from your input
- Provenance metadata

Example OData endpoint structure:
```
GET /odata/JobDescriptions
GET /odata/JobDescriptions(id)
POST /odata/JobDescriptions
PUT /odata/JobDescriptions(id)
DELETE /odata/JobDescriptions(id)
```

## Architecture

### Single-Page Application
- No dependencies - pure HTML, CSS, and JavaScript
- Client-side only - no server required
- All data processing in-browser

### Data Structure
```javascript
{
  basicInfo: {
    title, company, location, jobType,
    salaryRange: { min, max },
    description
  },
  responsibilities: [],
  qualifications: [],
  skills: [],
  provenance: {
    author, created, modified,
    version, status
  }
}
```

## Technical Details

### Standards Compliance
- **OData Protocol**: OASIS standard for RESTful APIs
- **OpenAPI**: Industry-standard API description format
- **JSON Schema**: Validation and documentation

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ JavaScript features
- CSS Grid and Flexbox layouts

## Demo Highlights

This demo showcases:
1. **UI/UX**: Intuitive, gradient-styled interface with clear sections
2. **Workflow**: Visual three-stage progression system
3. **Provenance**: Comprehensive tracking of creation and modification history
4. **Job Description Format**: Multiple export formats including OData-compliant schemas

## License

MIT License - Feel free to use and modify as needed.

## Contributing

This is a demo project showcasing Open Data Oasis API integration for job description management. Feel free to fork and extend!