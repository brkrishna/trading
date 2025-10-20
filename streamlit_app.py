"""
Streamlit Frontend for Trading Scanner

A modern web interface for the trading scanner with real-time updates,
run logs, and interactive data visualization.
"""

import streamlit as st
import pandas as pd
import sqlite3
import json
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import logging
import os
import subprocess
import sys
from typing import List, Dict, Any, Optional

# Import our validation system
sys.path.append(str(Path(__file__).parent))
from trading.validator import validator

# Configure page
st.set_page_config(
    page_title="Trading Scanner Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
DB_PATH = Path("trading/data/trading_data.db")
LOGS_PATH = Path("trading/data/run_logs.db")
OUTPUTS_PATH = Path("outputs")

# Ensure directories exist
OUTPUTS_PATH.mkdir(exist_ok=True)
(Path("trading/data")).mkdir(parents=True, exist_ok=True)

def init_logs_db():
    """Initialize the run logs database"""
    conn = sqlite3.connect(LOGS_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS run_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            candidates_count INTEGER DEFAULT 0,
            symbols_scanned INTEGER DEFAULT 0,
            duration_seconds REAL DEFAULT 0,
            output_files TEXT,
            error_message TEXT,
            parameters TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_scanner_run(status: str, candidates_count: int = 0, symbols_scanned: int = 0, 
                   duration_seconds: float = 0, output_files: Optional[List[str]] = None, 
                   error_message: Optional[str] = None, parameters: Optional[Dict] = None):
    """Log a scanner run to the database"""
    init_logs_db()
    conn = sqlite3.connect(LOGS_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO run_logs 
        (timestamp, status, candidates_count, symbols_scanned, duration_seconds, 
         output_files, error_message, parameters)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        status,
        candidates_count,
        symbols_scanned,
        duration_seconds,
        json.dumps(output_files or []),
        error_message,
        json.dumps(parameters or {})
    ))
    
    conn.commit()
    conn.close()

def get_latest_candidates() -> pd.DataFrame:
    """Get the latest candidate results with validation scoring"""
    try:
        # Look for the most recent candidates JSON file
        json_files = list(OUTPUTS_PATH.glob("candidates_*.json"))
        if not json_files:
            return pd.DataFrame()
        
        # Get the most recent file
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_file, 'r') as f:
            candidates = json.load(f)
        
        if not candidates:
            return pd.DataFrame()
        
        # Enhance each candidate with validation scores
        enhanced_candidates = []
        for candidate in candidates:
            try:
                # Run validation scoring
                validation_result = validator.validate_symbol(candidate)
                
                # Merge validation results with original data
                enhanced_candidate = {**candidate, **validation_result}
                enhanced_candidates.append(enhanced_candidate)
            except Exception as e:
                print(f"Validation failed for {candidate.get('symbol', 'unknown')}: {e}")
                # Add candidate without validation scores
                enhanced_candidates.append(candidate)
        
        df = pd.DataFrame(enhanced_candidates)
        
        # Format the data for display
        if 'close' in df.columns:
            df['close'] = df['close'].round(2)
        if 'date' in df.columns:
            df['date_formatted'] = pd.to_datetime(df['date']).dt.strftime('%d/%b/%y')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading candidates: {e}")
        return pd.DataFrame()

def get_run_logs() -> pd.DataFrame:
    """Get run logs from database"""
    try:
        init_logs_db()
        conn = sqlite3.connect(LOGS_PATH)
        
        df = pd.read_sql_query('''
            SELECT timestamp, status, candidates_count, symbols_scanned, 
                   duration_seconds, error_message, parameters
            FROM run_logs 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''', conn)
        
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['formatted_time'] = df['timestamp'].dt.strftime('%d/%b/%y %H:%M:%S')
        
        return df
        
    except Exception as e:
        st.error(f"Error loading run logs: {e}")
        return pd.DataFrame()

def run_scanner(limit: int = 20, symbols_file: Optional[str] = None) -> Dict[str, Any]:
    """Run the trading scanner"""
    import time
    start_time = time.time()
    
    try:
        # Prepare command
        cmd = [sys.executable, "-m", "trading.scan", "--outdir", str(OUTPUTS_PATH)]
        
        if limit:
            cmd.extend(["--limit", str(limit)])
        
        if symbols_file:
            cmd.extend(["--symbols-file", symbols_file])
        
        # Run the scanner
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        duration = time.time() - start_time
        
        if result.returncode == 0:
            # Parse output to get candidate count
            output_text = result.stdout
            candidates_count = 0
            symbols_scanned = limit or 50  # Default estimate
            
            # Try to extract candidate count from output
            for line in output_text.split('\n'):
                if 'Found' in line and 'candidates' in line:
                    try:
                        candidates_count = int(line.split('Found')[1].split('candidates')[0].strip())
                    except:
                        pass
            
            # Get output files
            output_files = list(OUTPUTS_PATH.glob(f"*{datetime.now().strftime('%Y%m%d')}*"))
            output_files = [str(f.name) for f in output_files[-10:]]  # Last 10 files
            
            # Log successful run
            log_scanner_run(
                status="SUCCESS",
                candidates_count=candidates_count,
                symbols_scanned=symbols_scanned,
                duration_seconds=duration,
                output_files=output_files,
                parameters={"limit": limit, "symbols_file": symbols_file}
            )
            
            return {
                "success": True,
                "candidates_count": candidates_count,
                "duration": duration,
                "output": output_text
            }
        else:
            # Log failed run
            log_scanner_run(
                status="FAILED",
                duration_seconds=duration,
                error_message=result.stderr,
                parameters={"limit": limit, "symbols_file": symbols_file}
            )
            
            return {
                "success": False,
                "error": result.stderr,
                "duration": duration,
                "output": result.stdout
            }
            
    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)
        
        # Log error
        log_scanner_run(
            status="ERROR",
            duration_seconds=duration,
            error_message=error_msg,
            parameters={"limit": limit, "symbols_file": symbols_file}
        )
        
        return {
            "success": False,
            "error": error_msg,
            "duration": duration
        }

def create_price_chart(history: List[float], symbol: str) -> go.Figure:
    """Create a price history chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(history))),
        y=history,
        mode='lines',
        name='Close Price',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.update_layout(
        title=f"{symbol} - Price History (Last 30 Days)",
        xaxis_title="Days",
        yaxis_title="Price (₹)",
        height=400,
        showlegend=False,
        template="plotly_white"
    )
    
    return fig

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("📈 Trading Scanner Dashboard")
    st.markdown("Real-time stock scanner with technical analysis and breakout detection")
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎛️ Scanner Controls")
        
        # Scanner parameters
        limit = st.number_input("Limit symbols", min_value=1, max_value=100, value=20)
        symbols_file = st.text_input("Custom symbols file (optional)")
        
        # Run scanner button
        if st.button("🚀 Run Scanner", type="primary"):
            with st.spinner("Running scanner..."):
                result = run_scanner(limit, symbols_file if symbols_file else None)
                
                if result["success"]:
                    st.success(f"✅ Scanner completed! Found {result['candidates_count']} candidates in {result['duration']:.1f}s")
                else:
                    st.error(f"❌ Scanner failed: {result.get('error', 'Unknown error')}")
        
        st.divider()
        
        # Auto-refresh settings
        st.header("🔄 Auto Refresh")
        auto_refresh = st.checkbox("Enable auto-refresh")
        refresh_interval = st.slider("Refresh interval (seconds)", 10, 300, 60)
        
        if auto_refresh:
            st.write(f"⏰ Auto-refreshing every {refresh_interval}s")
            # Use st.rerun() for auto-refresh
            import time
            time.sleep(refresh_interval)
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📊 Latest Results", "📝 Run Logs", "⚙️ System Status"])
    
    with tab1:
        st.header("Latest Scanner Results")
        
        # Get latest candidates
        df = get_latest_candidates()
        
        if df.empty:
            st.info("No recent results found. Run the scanner to generate new data.")
        else:
            # Display summary metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Candidates", len(df))
            
            with col2:
                high_confidence = 0
                if 'recommendation' in df.columns:
                    high_confidence = len(df[df['recommendation'].apply(lambda x: isinstance(x, dict) and x.get('confidence') == 'HIGH')])
                st.metric("High Confidence", high_confidence)
            
            with col3:
                enter_signals = 0
                if 'recommendation' in df.columns:
                    enter_signals = len(df[df['recommendation'].apply(lambda x: isinstance(x, dict) and x.get('action') == 'ENTER')])
                st.metric("Entry Signals", enter_signals)
            
            with col4:
                avg_validation_score = df['overall_score'].mean() if 'overall_score' in df.columns else 0
                st.metric("Avg Validation Score", f"{avg_validation_score:.1f}")
            
            with col5:
                red_flags_count = 0
                if 'red_flags' in df.columns:
                    red_flags_count = len(df[df['red_flags'].apply(lambda x: isinstance(x, list) and len(x) > 0)])
                st.metric("🚩 Red Flags", red_flags_count)
            
            st.divider()
            
            # Enhanced Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'signal_type' in df.columns:
                    signal_filter = st.multiselect(
                        "📊 Signal Type",
                        options=df['signal_type'].unique(),
                        default=df['signal_type'].unique()
                    )
                    df = df[df['signal_type'].isin(signal_filter)]
            
            with col2:
                if 'recommendation' in df.columns:
                    action_filter = st.selectbox(
                        "💡 Recommendation",
                        options=['All', 'ENTER', 'SKIP'],
                        index=0
                    )
                    if action_filter != 'All':
                        df = df[df['recommendation'].apply(lambda x: isinstance(x, dict) and x.get('action') == action_filter)]
            
            with col3:
                if 'overall_score' in df.columns:
                    min_validation_score = st.slider("🎯 Min Validation Score", 0, 100, 0)
                    df = df[df['overall_score'] >= min_validation_score]
            
            # Display enhanced results table
            if not df.empty:
                st.subheader("📊 Validation Results")
                
                # Create enhanced display with validation scores
                for idx, row in df.iterrows():
                    with st.container():
                        # Main row with key info
                        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 2, 1])
                        
                        with col1:
                            st.write(f"**{row['symbol']}**")
                            st.caption(f"Signal: {row.get('signal_type', 'Unknown')}")
                        
                        with col2:
                            st.metric("Price", f"₹{row['close']:.2f}")
                            st.caption(row.get('date_formatted', ''))
                        
                        with col3:
                            overall_score = row.get('overall_score', 0)
                            if overall_score > 0:
                                st.metric("Validation", f"{overall_score:.0f}/100")
                                
                                # Color coding
                                if overall_score >= 70:
                                    st.success("High Confidence")
                                elif overall_score >= 50:
                                    st.warning("Medium Confidence") 
                                else:
                                    st.error("Low Confidence")
                            else:
                                st.metric("Score", f"{row.get('score', 0)}")
                                st.info("Basic Scoring")
                        
                        with col4:
                            tech_score = row.get('technical_score', 0)
                            fund_score = row.get('fundamental_score', 0)
                            st.metric("Technical", f"{tech_score:.1f}/20")
                            st.metric("Fundamental", f"{fund_score:.1f}/20")
                        
                        with col5:
                            recommendation = row.get('recommendation', {})
                            if recommendation and isinstance(recommendation, dict):
                                action = recommendation.get('action', 'Unknown')
                                reason = recommendation.get('reason', 'No reason provided')
                                
                                if action == 'ENTER':
                                    st.success(f"✅ {action}")
                                    position_size = recommendation.get('position_size', '')
                                    if position_size:
                                        st.caption(f"Position: {position_size}")
                                else:
                                    st.error(f"❌ {action}")
                                
                                st.caption(reason)
                            else:
                                # Fallback to basic signal info
                                signal_type = row.get('signal_type', 'Unknown')
                                st.info(f"📊 {signal_type}")
                                tags = row.get('reason_tags', [])
                                if tags:
                                    st.caption(f"Tags: {', '.join(tags)}")
                        
                        with col6:
                            # Red flags
                            red_flags = row.get('red_flags', [])
                            if red_flags and isinstance(red_flags, list) and len(red_flags) > 0:
                                st.error("🚩 Red Flags")
                                for flag in red_flags:
                                    st.caption(f"• {flag}")
                            else:
                                st.success("✅ Clean")
                        
                        # Expandable detailed analysis
                        with st.expander(f"📋 Detailed Analysis - {row['symbol']}", expanded=False):
                            tech_details = row.get('technical_details', {})
                            fund_details = row.get('fundamental_details', {})
                            explanations = row.get('explanations', {})
                            checklist = row.get('checklist_summary', {})
                            
                            if tech_details or fund_details:
                                tcol1, tcol2 = st.columns(2)
                                
                                with tcol1:
                                    # Technical breakdown
                                    st.write("**🔧 Technical Analysis**")
                                    if tech_details:
                                        for key, score in tech_details.items():
                                            indicator_name = key.replace('_score', '').replace('_', ' ').title()
                                            progress_val = max(0, min(1, score / 4.0))  # Clamp to 0-1
                                            st.write(f"**{indicator_name}**: {score:.1f}/4")
                                            st.progress(progress_val)
                                            
                                            # Show explanation on hover (help icon)
                                            if key in explanations:
                                                st.help(explanations[key])
                                    else:
                                        st.info("Technical analysis not available")
                                
                                with tcol2:
                                    # Fundamental breakdown
                                    st.write("**📊 Fundamental Analysis**")
                                    if fund_details:
                                        for key, score in fund_details.items():
                                            indicator_name = key.replace('_score', '').replace('_', ' ').title()
                                            progress_val = max(0, min(1, score / 4.0))
                                            st.write(f"**{indicator_name}**: {score:.1f}/4")
                                            st.progress(progress_val)
                                            
                                            if key in explanations:
                                                st.help(explanations[key])
                                    else:
                                        st.info("Fundamental analysis not available")
                                
                                # Checklist summary
                                if checklist:
                                    st.write("**📝 Validation Checklist**")
                                    ccol1, ccol2 = st.columns(2)
                                    
                                    checklist_items = list(checklist.items())
                                    mid_point = len(checklist_items) // 2
                                    
                                    with ccol1:
                                        for check, status in checklist_items[:mid_point]:
                                            st.write(f"{status} {check}")
                                    
                                    with ccol2:
                                        for check, status in checklist_items[mid_point:]:
                                            st.write(f"{status} {check}")
                            else:
                                # Show basic analysis for non-validated candidates
                                st.info("**Enhanced validation not available for this candidate**")
                                
                                # Show available basic metrics
                                basic_cols = st.columns(3)
                                with basic_cols[0]:
                                    st.metric("RSI", f"{row.get('rsi14', 0):.1f}")
                                with basic_cols[1]:
                                    st.metric("Volume Ratio", f"{row.get('vol', 0) / max(1, row.get('vol_avg20', 1)):.2f}x")
                                with basic_cols[2]:
                                    st.metric("SMA20", f"₹{row.get('sma20', 0):.2f}")
                                
                                # Show reason tags
                                tags = row.get('reason_tags', [])
                                if tags:
                                    st.write("**Tags:**", ", ".join(tags))
                        
                        st.divider()
                
                # Interactive charts
                st.subheader("📈 Price Charts")
                
                if 'history' in df.columns:
                    selected_symbol = st.selectbox("Select symbol for chart", df['symbol'].unique())
                    
                    if selected_symbol:
                        symbol_data = df[df['symbol'] == selected_symbol].iloc[0]
                        if symbol_data['history']:
                            fig = create_price_chart(symbol_data['history'], selected_symbol)
                            st.plotly_chart(fig, config={'displayModeBar': True, 'responsive': True})
    
    with tab2:
        st.header("Scanner Run Logs")
        
        logs_df = get_run_logs()
        
        if logs_df.empty:
            st.info("No run logs found.")
        else:
            # Summary stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_runs = len(logs_df)
                st.metric("Total Runs", total_runs)
            
            with col2:
                success_rate = (logs_df['status'] == 'SUCCESS').mean() * 100
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            with col3:
                avg_duration = logs_df['duration_seconds'].mean()
                st.metric("Avg Duration", f"{avg_duration:.1f}s")
            
            st.divider()
            
            # Logs table
            display_logs = logs_df[['formatted_time', 'status', 'candidates_count', 
                                   'symbols_scanned', 'duration_seconds', 'error_message']].copy()
            display_logs.columns = ['Timestamp', 'Status', 'Candidates', 'Symbols', 'Duration (s)', 'Error']
            
            # Color code status
            def color_status(val):
                if val == 'SUCCESS':
                    return 'background-color: #d4edda'
                elif val == 'FAILED':
                    return 'background-color: #f8d7da'
                elif val == 'ERROR':
                    return 'background-color: #f8d7da'
                return ''
            
            st.dataframe(
                display_logs.style.map(color_status, subset=['Status']),
                width='stretch',
                hide_index=True
            )
    
    with tab3:
        st.header("System Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 File System")
            
            # Check database
            db_exists = DB_PATH.exists()
            st.write(f"📊 Trading Database: {'✅ Connected' if db_exists else '❌ Missing'}")
            
            if db_exists:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM history")
                    record_count = cursor.fetchone()[0]
                    st.write(f"📈 Historical Records: {record_count:,}")
                    conn.close()
                except Exception as e:
                    st.write(f"⚠️ Database Error: {e}")
            
            # Check output directory
            output_files = list(OUTPUTS_PATH.glob("*"))
            st.write(f"📂 Output Files: {len(output_files)}")
        
        with col2:
            st.subheader("🔧 System Info")
            
            # Python version
            st.write(f"🐍 Python: {sys.version.split()[0]}")
            
            # Working directory
            st.write(f"📍 Directory: {Path.cwd().name}")
            
            # Recent activity
            if output_files:
                latest_file = max(output_files, key=lambda x: x.stat().st_mtime)
                latest_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
                st.write(f"🕒 Last Activity: {latest_time.strftime('%d/%b/%y %H:%M:%S')}")

if __name__ == "__main__":
    main()