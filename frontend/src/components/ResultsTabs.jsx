/**
 * Results Tabs Component
 * Displays enrichment results in tabbed interface
 */
import { useState } from 'react';
import { Shield, Globe, Server, AlertTriangle, Database } from 'lucide-react';

const AGENT_ICONS = {
    VirusTotal: Shield,
    Shodan: Server,
    Censys: Globe,
    OTX: Database,
    AbuseIPDB: AlertTriangle,
};

const AGENT_COLORS = {
    VirusTotal: '#4f8af7',
    Shodan: '#ea3126',
    Censys: '#5c33be',
    OTX: '#00d4aa',
    AbuseIPDB: '#f97316',
};

const ResultsTabs = ({ results }) => {
    const [activeTab, setActiveTab] = useState(null);

    // Filter out metadata key
    const agents = Object.keys(results).filter(key => key !== '_metadata');

    // Set first agent as active on mount
    if (activeTab === null && agents.length > 0) {
        setActiveTab(agents[0]);
    }

    const renderAgentResult = (agentName, data) => {
        if (data.status === 'error') {
            return (
                <div className="result-error">
                    <AlertTriangle size={20} />
                    <span>Error: {data.error}</span>
                </div>
            );
        }

        // Render different content based on agent
        if (agentName === 'VirusTotal' && data.data) {
            const vtData = data.data;
            return (
                <div className="result-content">
                    <div className="stat-row">
                        <span className="stat-label">Detection Ratio</span>
                        <span className="stat-value" style={{
                            color: vtData.detection_ratio?.malicious > 0 ? '#ef4444' : '#22c55e'
                        }}>
                            {vtData.detection_ratio?.malicious || 0} / {vtData.detection_ratio?.total || 0}
                        </span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">Community Score</span>
                        <span className="stat-value">{vtData.community_score || 'N/A'}</span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">Reputation</span>
                        <span className="stat-value">{vtData.reputation || 'Unknown'}</span>
                    </div>
                    {vtData.last_analysis_date && (
                        <div className="stat-row">
                            <span className="stat-label">Last Analysis</span>
                            <span className="stat-value">{vtData.last_analysis_date}</span>
                        </div>
                    )}
                </div>
            );
        }

        if (agentName === 'Shodan' && data.data) {
            const shodanData = data.data;
            return (
                <div className="result-content">
                    <div className="stat-row">
                        <span className="stat-label">Organization</span>
                        <span className="stat-value">{shodanData.org || 'Unknown'}</span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">Country</span>
                        <span className="stat-value">{shodanData.country || 'Unknown'}</span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">ASN</span>
                        <span className="stat-value">{shodanData.asn || 'Unknown'}</span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">Open Ports</span>
                        <span className="stat-value">
                            {shodanData.ports?.join(', ') || 'None detected'}
                        </span>
                    </div>
                </div>
            );
        }

        if (agentName === 'AbuseIPDB' && data.data) {
            const abuseData = data.data;
            return (
                <div className="result-content">
                    <div className="stat-row">
                        <span className="stat-label">Abuse Confidence</span>
                        <span className="stat-value" style={{
                            color: (abuseData.abuse_confidence_score || 0) > 50 ? '#ef4444' : '#22c55e'
                        }}>
                            {abuseData.abuse_confidence_score || 0}%
                        </span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">Total Reports</span>
                        <span className="stat-value">{abuseData.total_reports || 0}</span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">ISP</span>
                        <span className="stat-value">{abuseData.isp || 'Unknown'}</span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">Country</span>
                        <span className="stat-value">{abuseData.country_code || 'Unknown'}</span>
                    </div>
                </div>
            );
        }

        if (agentName === 'OTX' && data.data) {
            const otxData = data.data;
            return (
                <div className="result-content">
                    <div className="stat-row">
                        <span className="stat-label">Pulses</span>
                        <span className="stat-value">{otxData.pulse_count || 0}</span>
                    </div>
                    <div className="stat-row">
                        <span className="stat-label">Reputation</span>
                        <span className="stat-value">{otxData.reputation || 'Unknown'}</span>
                    </div>
                    {otxData.tags && otxData.tags.length > 0 && (
                        <div className="stat-row">
                            <span className="stat-label">Tags</span>
                            <div className="tags-container">
                                {otxData.tags.slice(0, 5).map((tag, i) => (
                                    <span key={i} className="tag">{tag}</span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            );
        }

        // Generic render for unknown agents
        return (
            <div className="result-content">
                <pre className="raw-data">{JSON.stringify(data.data || data, null, 2)}</pre>
            </div>
        );
    };

    return (
        <div className="results-tabs">
            <div className="tabs-header">
                {agents.map(agent => {
                    const Icon = AGENT_ICONS[agent] || Database;
                    const color = AGENT_COLORS[agent] || '#6b7280';
                    const hasError = results[agent]?.status === 'error';

                    return (
                        <button
                            key={agent}
                            className={`tab-button ${activeTab === agent ? 'active' : ''} ${hasError ? 'error' : ''}`}
                            onClick={() => setActiveTab(agent)}
                            style={{ '--tab-color': color }}
                        >
                            <Icon size={16} />
                            <span>{agent}</span>
                            {hasError && <AlertTriangle size={12} className="error-icon" />}
                        </button>
                    );
                })}
            </div>

            <div className="tab-content">
                {activeTab && renderAgentResult(activeTab, results[activeTab])}
            </div>
        </div>
    );
};

export default ResultsTabs;
