# 📈 Trading Scanner Streamlit Dashboard

A modern, interactive web interface for the trading scanner with real-time updates, comprehensive run logs, and data visualization.

## 🚀 Quick Start

### Windows Users
```bash
# Double-click to start
start_dashboard.bat
```

### Linux/Mac Users
```bash
# Make executable and run
chmod +x start_dashboard.sh
./start_dashboard.sh
```

### Manual Launch
```bash
# Activate virtual environment
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start dashboard
python -m streamlit run streamlit_app.py --server.port 8501
```

## 🎯 Features

### 📊 Latest Results Tab
- **Interactive Data Table**: View latest scanner results with filtering
- **Summary Metrics**: Candidate counts and score distributions  
- **Advanced Filtering**: By signal type, minimum score, and tags
- **Price Charts**: Interactive Plotly charts for price history
- **Real-time Updates**: Auto-refresh capability

### 📝 Run Logs Tab
- **Historical Tracking**: Complete log of all scanner runs
- **Performance Metrics**: Success rates, average duration, total runs
- **Error Tracking**: Detailed error messages and diagnostics
- **Status Visualization**: Color-coded status indicators

### ⚙️ System Status Tab
- **Database Health**: Connection status and record counts
- **File System**: Output directory and file tracking
- **System Information**: Python version and working directory
- **Activity Monitoring**: Last activity timestamps

### 🎛️ Scanner Controls
- **Run Scanner**: Execute scans directly from the dashboard
- **Parameter Control**: Adjust symbol limits and file inputs
- **Auto-refresh**: Configurable automatic updates (10-300 seconds)
- **Real-time Feedback**: Success/failure notifications

## 📱 User Interface

### Dashboard Layout
```
📈 Trading Scanner Dashboard
├── 🎛️ Sidebar Controls
│   ├── Scanner Parameters (limit, symbols file)
│   ├── Run Scanner Button
│   └── Auto-refresh Settings
└── 📊 Main Content (Tabs)
    ├── 📊 Latest Results
    │   ├── Summary Metrics (4 columns)
    │   ├── Filtering Controls
    │   ├── Interactive Results Table
    │   └── Price History Charts
    ├── 📝 Run Logs
    │   ├── Performance Statistics
    │   └── Historical Runs Table
    └── ⚙️ System Status
        ├── Database Status
        └── System Information
```

### Key Metrics Displayed
- **Candidates Found**: Total from latest run
- **High/Mid/Low Scores**: Score-based categorization
- **Success Rate**: Historical success percentage  
- **Average Duration**: Typical scan execution time
- **Database Records**: Total historical data points

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit (Python web framework)
- **Visualization**: Plotly for interactive charts
- **Data Storage**: SQLite databases for logs and scanner data
- **Real-time Updates**: Auto-refresh with configurable intervals
- **Responsive Design**: Works on desktop and mobile devices

### Database Schema

#### Run Logs (`trading/data/run_logs.db`)
```sql
CREATE TABLE run_logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL,          -- SUCCESS, FAILED, ERROR
    run_id TEXT,                   -- Unique run identifier
    candidates_count INTEGER,      -- Number found
    symbols_scanned INTEGER,       -- Symbols processed
    duration_seconds REAL,         -- Execution time
    output_files TEXT,             -- JSON array of files
    error_message TEXT,            -- Error details
    parameters TEXT                -- JSON run parameters
);
```

#### Scanner Data (`trading/data/trading_data.db`)
```sql
CREATE TABLE history (
    symbol TEXT,
    date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    -- ... additional columns
);
```

### File Structure
```
trading/
├── streamlit_app.py          # Main dashboard application
├── trading/
│   ├── run_logger.py         # Run logging functionality
│   ├── scan.py               # Enhanced with logging
│   └── data/
│       ├── run_logs.db       # Run history database
│       └── trading_data.db   # Scanner data database
├── outputs/                  # Generated reports and data
├── start_dashboard.bat       # Windows launcher
├── start_dashboard.sh        # Linux/Mac launcher
└── requirements.txt          # Updated with Streamlit
```

## 🎨 Customization

### Styling
The dashboard uses Streamlit's default theme with custom enhancements:
- **Color Coding**: Green (high scores), Yellow (mid scores), Red (low scores)
- **Progress Bars**: Visual score representation
- **Status Indicators**: Success/failure color coding

### Configuration
Key settings can be modified in `streamlit_app.py`:
```python
# Dashboard settings
DB_PATH = Path("trading/data/trading_data.db")
LOGS_PATH = Path("trading/data/run_logs.db")
OUTPUTS_PATH = Path("outputs")

# Score thresholds (matches scanner defaults)
threshold_high = 75  # Green background
threshold_mid = 40   # Yellow background
# < 40 = Red background
```

## 🚨 Troubleshooting

### Common Issues

1. **"No module named streamlit"**
   ```bash
   # Ensure virtual environment is activated
   source .venv/Scripts/activate
   pip install -r requirements.txt
   ```

2. **"Database not found"**
   ```bash
   # Run scanner first to create databases
   python -m trading.scan --outdir outputs --limit 5
   ```

3. **"Port 8501 already in use"**
   ```bash
   # Use different port
   python -m streamlit run streamlit_app.py --server.port 8502
   ```

4. **Auto-refresh not working**
   - Check browser console for JavaScript errors
   - Ensure stable network connection
   - Try refreshing the page manually

### Debug Mode
To run with detailed logging:
```bash
python -m streamlit run streamlit_app.py --logger.level debug
```

## 🔒 Security Notes

- Dashboard runs on localhost by default (secure)
- No external API calls from the frontend
- All data stored locally in SQLite databases
- Scanner credentials/API keys handled by backend only

## 📊 Performance

### Optimizations
- **Lazy Loading**: Data loaded only when tabs are accessed
- **Caching**: Streamlit caching for database queries
- **Pagination**: Limited results for faster loading
- **Background Processing**: Scanner runs don't block UI

### Scalability
- **SQLite Limits**: Suitable for single-user applications
- **Memory Usage**: ~50-100MB for typical datasets
- **Concurrent Users**: Single-user design (localhost)

## 🆙 Future Enhancements

### Planned Features
- [ ] **Email Alerts**: Notification system for high-score candidates
- [ ] **Advanced Charts**: Candlestick charts with technical indicators
- [ ] **Export Functionality**: PDF reports and Excel exports
- [ ] **Theme Customization**: Light/dark mode toggle
- [ ] **Mobile Optimization**: Responsive design improvements
- [ ] **Historical Comparison**: Side-by-side run comparisons

### Integration Opportunities
- [ ] **Slack/Teams**: Send alerts to messaging platforms
- [ ] **Cloud Storage**: Backup results to cloud services
- [ ] **REST API**: Expose dashboard data via API
- [ ] **Multi-user Support**: Authentication and user management

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the scanner logs in the "Run Logs" tab
3. Check the "System Status" tab for database connectivity
4. Examine terminal output when starting the dashboard

The dashboard provides real-time visibility into your trading scanner operations with professional visualizations and comprehensive logging! 🎯