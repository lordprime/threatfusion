/**
 * Risk Score Gauge Component
 * Displays a visual gauge for the threat risk score
 */
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const COLORS = {
    CRITICAL: '#ef4444',
    HIGH: '#f97316',
    MEDIUM: '#eab308',
    LOW: '#22c55e',
};

const RiskGauge = ({ score, severity, confidence }) => {
    const maxScore = 10;
    const percentage = (score / maxScore) * 100;

    const gaugeData = [
        { name: 'Score', value: score },
        { name: 'Remaining', value: maxScore - score },
    ];

    const getColor = () => {
        if (severity === 'CRITICAL') return COLORS.CRITICAL;
        if (severity === 'HIGH') return COLORS.HIGH;
        if (severity === 'MEDIUM') return COLORS.MEDIUM;
        return COLORS.LOW;
    };

    const getSeverityEmoji = () => {
        if (severity === 'CRITICAL') return '🔴';
        if (severity === 'HIGH') return '🟠';
        if (severity === 'MEDIUM') return '🟡';
        return '🟢';
    };

    return (
        <div className="risk-gauge">
            <div className="gauge-container">
                <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                        <Pie
                            data={gaugeData}
                            cx="50%"
                            cy="50%"
                            startAngle={180}
                            endAngle={0}
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={0}
                            dataKey="value"
                        >
                            <Cell fill={getColor()} />
                            <Cell fill="#374151" />
                        </Pie>
                    </PieChart>
                </ResponsiveContainer>
                <div className="gauge-center">
                    <span className="score-value">{score.toFixed(1)}</span>
                    <span className="score-max">/ {maxScore}</span>
                </div>
            </div>
            <div className="severity-badge" style={{ backgroundColor: getColor() }}>
                {getSeverityEmoji()} {severity}
            </div>
            <div className="confidence-bar">
                <span>Confidence: {(confidence * 100).toFixed(0)}%</span>
                <div className="progress-bar">
                    <div
                        className="progress-fill"
                        style={{ width: `${confidence * 100}%`, backgroundColor: getColor() }}
                    />
                </div>
            </div>
        </div>
    );
};

export default RiskGauge;
