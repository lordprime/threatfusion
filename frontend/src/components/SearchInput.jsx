/**
 * Search Input Component
 * Input field for entering indicators with search button
 */
import { Search, Loader2 } from 'lucide-react';

const SearchInput = ({ value, onChange, onSearch, loading, placeholder }) => {
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !loading) {
            onSearch();
        }
    };

    return (
        <div className="search-container">
            <div className="search-input-wrapper">
                <Search className="search-icon" size={20} />
                <input
                    type="text"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder || "Enter IP, Hash, or Domain..."}
                    className="search-input"
                    disabled={loading}
                />
            </div>
            <button
                className="search-button"
                onClick={onSearch}
                disabled={loading || !value.trim()}
            >
                {loading ? (
                    <>
                        <Loader2 className="spin" size={18} />
                        <span>Analyzing...</span>
                    </>
                ) : (
                    <>
                        <Search size={18} />
                        <span>Analyze</span>
                    </>
                )}
            </button>
        </div>
    );
};

export default SearchInput;
