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
                   duration_seconds: float = 0, output_files: List[str] = None, 
                   error_message: str = None, parameters: Dict = None):
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
    """Get the latest candidate results"""
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
        
        df = pd.DataFrame(candidates)
        
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

def run_scanner(limit: int = 20, symbols_file: str = None) -> Dict[str, Any]:
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
                result = run_scanner(limit, symbols_file or None)
                
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
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Candidates", len(df))
            
            with col2:
                high_score = len(df[df['score'] >= 75]) if 'score' in df.columns else 0
                st.metric("High Score (≥75)", high_score)
            
            with col3:
                mid_score = len(df[(df['score'] >= 40) & (df['score'] < 75)]) if 'score' in df.columns else 0
                st.metric("Mid Score (40-75)", mid_score)
            
            with col4:
                avg_score = df['score'].mean() if 'score' in df.columns else 0
                st.metric("Average Score", f"{avg_score:.1f}")
            
            st.divider()
            
            # Filters
            col1, col2 = st.columns(2)
            
            with col1:
                if 'signal_type' in df.columns:
                    signal_filter = st.multiselect(
                        "Filter by Signal Type",
                        options=df['signal_type'].unique(),
                        default=df['signal_type'].unique()
                    )
                    df = df[df['signal_type'].isin(signal_filter)]
            
            with col2:
                if 'score' in df.columns:
                    min_score = st.slider("Minimum Score", 0, 100, 0)
                    df = df[df['score'] >= min_score]
            
            # Display results table
            if not df.empty:
                # Select columns to display
                display_cols = ['symbol', 'date_formatted', 'close', 'signal_type', 'score']
                if 'reason_tags' in df.columns:
                    display_cols.append('reason_tags')
                
                # Rename columns for display
                display_df = df[display_cols].copy()
                display_df.columns = ['Symbol', 'Date', 'Close (₹)', 'Signal', 'Score', 'Tags']
                
                st.dataframe(
                    display_df,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "Close (₹)": st.column_config.NumberColumn(
                            format="₹%.2f"
                        ),
                        "Score": st.column_config.ProgressColumn(
                            min_value=0,
                            max_value=100
                        )
                    }
                )
                
                # Interactive charts
                st.subheader("📈 Price Charts")
                
                if 'history' in df.columns:
                    selected_symbol = st.selectbox("Select symbol for chart", df['symbol'].unique())
                    
                    if selected_symbol:
                        symbol_data = df[df['symbol'] == selected_symbol].iloc[0]
                        if symbol_data['history']:
                            fig = create_price_chart(symbol_data['history'], selected_symbol)
                            st.plotly_chart(fig, width='stretch')
    
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