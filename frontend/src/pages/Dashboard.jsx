/**
 * Dashboard Page
 * Main page for ThreatFusion web interface
 */
import { useState, useEffect } from 'react';
import { Settings, HelpCircle, Shield, AlertTriangle as Alert } from 'lucide-react';
import SearchInput from '../components/SearchInput';
import RiskGauge from '../components/RiskGauge';
import ResultsTabs from '../components/ResultsTabs';
import ExportButtons from '../components/ExportButtons';
import { enrichIndicator, getConfig } from '../services/api';

const Dashboard = () => {
    const [indicator, setIndicator] = useState('');
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [configStatus, setConfigStatus] = useState(null);
    const [showConfig, setShowConfig] = useState(false);

    useEffect(() => {
        // Check API configuration on mount
        const checkConfig = async () => {
            try {
                const config = await getConfig();
                setConfigStatus(config);
            } catch (err) {
                setError('Failed to connect to API server. Is the backend running?');
            }
        };
        checkConfig();
    }, []);

    const handleSearch = async () => {
        if (!indicator.trim()) return;

        setLoading(true);
        setError(null);
        setResults(null);

        try {
            const data = await enrichIndicator(indicator.trim());
            setResults(data);
        } catch (err) {
            if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Failed to analyze indicator. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard">
            <header className="dashboard-header">
                <div className="logo">
                    <Shield className="logo-icon" size={32} />
                    <h1>ThreatFusion</h1>
                </div>
                <div className="header-actions">
                    <button
                        className="icon-btn"
                        onClick={() => setShowConfig(!showConfig)}
                        title="Configuration"
                    >
                        <Settings size={20} />
                    </button>
                    <button className="icon-btn" title="Help">
                        <HelpCircle size={20} />
                    </button>
                </div>
            </header>

            {showConfig && configStatus && (
                <div className="config-panel">
                    <h3>API Configuration</h3>
                    <p>{configStatus.configured_count} / {configStatus.total_services} services configured</p>
                    <div className="config-services">
                        {Object.entries(configStatus.services).map(([service, configured]) => (
                            <div key={service} className={`config-service ${configured ? 'active' : 'inactive'}`}>
                                <span className="config-dot" />
                                <span>{service}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <main className="dashboard-main">
                <div className="search-section">
                    <h2>Threat Intelligence Lookup</h2>
                    <p>Enter an IP address, domain, or file hash to analyze</p>
                    <SearchInput
                        value={indicator}
                        onChange={setIndicator}
                        onSearch={handleSearch}
                        loading={loading}
                    />
                </div>

                {error && (
                    <div className="error-banner">
                        <Alert size={20} />
                        <span>{error}</span>
                    </div>
                )}

                {loading && (
                    <div className="loading-section">
                        <div className="loading-spinner" />
                        <p>Querying threat intelligence sources...</p>
                        <p className="loading-hint">This may take up to 30 seconds</p>
                    </div>
                )}

                {results && !loading && (
                    <div className="results-section">
                        <div className="results-header">
                            <div className="indicator-info">
                                <h3>{results.indicator}</h3>
                                <span className="indicator-type">{results.indicator_type}</span>
                                {results.is_private && (
                                    <span className="private-badge">Private IP</span>
                                )}
                            </div>
                            <span className="execution-time">⏱️ {results.execution_time}s</span>
                        </div>

                        <div className="results-grid">
                            <div className="risk-section">
                                <h4>Risk Assessment</h4>
                                <RiskGauge
                                    score={results.risk_score.score}
                                    severity={results.risk_score.severity}
                                    confidence={results.risk_score.confidence}
                                />
                            </div>

                            <div className="sources-section">
                                <h4>Intelligence Sources</h4>
                                <ResultsTabs results={results.results} />
                            </div>
                        </div>

                        <ExportButtons results={results} indicator={results.indicator} />
                    </div>
                )}

                {!results && !loading && !error && (
                    <div className="empty-state">
                        <Shield size={64} className="empty-icon" />
                        <h3>Ready to Analyze</h3>
                        <p>Enter an indicator above to get started</p>
                        <div className="example-queries">
                            <p>Examples:</p>
                            <code onClick={() => setIndicator('8.8.8.8')}>8.8.8.8</code>
                            <code onClick={() => setIndicator('example.com')}>example.com</code>
                            <code onClick={() => setIndicator('44d88612fea8a8f36de82e1278abb02f')}>44d88612...</code>
                        </div>
                    </div>
                )}
            </main>

            <footer className="dashboard-footer">
                <p>ThreatFusion v0.1.0 • Threat Intelligence Aggregator</p>
            </footer>
        </div>
    );
};

export default Dashboard;
