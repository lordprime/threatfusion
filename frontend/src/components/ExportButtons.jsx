/**
 * Export Buttons Component
 * Buttons to export results in different formats
 */
import { FileJson, FileText, Download } from 'lucide-react';

const ExportButtons = ({ results, indicator }) => {
    const exportJSON = () => {
        const dataStr = JSON.stringify(results, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
        const filename = `threatfusion_${indicator.replace(/[^a-z0-9]/gi, '_')}.json`;

        const link = document.createElement('a');
        link.setAttribute('href', dataUri);
        link.setAttribute('download', filename);
        link.click();
    };

    const exportHTML = () => {
        const html = generateHTMLReport(results, indicator);
        const dataUri = 'data:text/html;charset=utf-8,' + encodeURIComponent(html);
        const filename = `threatfusion_${indicator.replace(/[^a-z0-9]/gi, '_')}.html`;

        const link = document.createElement('a');
        link.setAttribute('href', dataUri);
        link.setAttribute('download', filename);
        link.click();
    };

    const generateHTMLReport = (data, ind) => {
        return `<!DOCTYPE html>
<html>
<head>
  <title>ThreatFusion Report - ${ind}</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #e2e8f0; padding: 2rem; }
    .container { max-width: 800px; margin: 0 auto; }
    h1 { color: #38bdf8; }
    .card { background: #1e293b; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .score { font-size: 2rem; font-weight: bold; }
    pre { background: #0f172a; padding: 1rem; border-radius: 4px; overflow-x: auto; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🔍 ThreatFusion Report</h1>
    <div class="card">
      <h2>Indicator: ${ind}</h2>
      <p>Type: ${data.indicator_type}</p>
      <p class="score">Risk Score: ${data.risk_score?.score?.toFixed(1) || 'N/A'} / 10</p>
      <p>Severity: ${data.risk_score?.severity || 'Unknown'}</p>
    </div>
    <div class="card">
      <h2>Raw Results</h2>
      <pre>${JSON.stringify(data.results, null, 2)}</pre>
    </div>
    <p>Generated: ${new Date().toISOString()}</p>
  </div>
</body>
</html>`;
    };

    return (
        <div className="export-buttons">
            <button className="export-btn" onClick={exportJSON}>
                <FileJson size={16} />
                <span>Export JSON</span>
            </button>
            <button className="export-btn" onClick={exportHTML}>
                <FileText size={16} />
                <span>Export HTML</span>
            </button>
        </div>
    );
};

export default ExportButtons;
