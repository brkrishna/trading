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

def run_scanner(limit: int = 50, symbols_file: Optional[str] = None, refresh_cache: bool = False) -> Dict[str, Any]:
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
        
        if refresh_cache:
            cmd.append("--refresh-cache")
        
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
                parameters={"limit": limit, "symbols_file": symbols_file, "refresh_cache": refresh_cache}
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
                parameters={"limit": limit, "symbols_file": symbols_file, "refresh_cache": refresh_cache}
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
            parameters={"limit": limit, "symbols_file": symbols_file, "refresh_cache": refresh_cache}
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
        limit = st.number_input("Limit symbols (0 = all available)", min_value=0, value=50, help="Number of symbols to scan (0 for all, default 50)")
        symbols_file = st.text_input("Custom symbols file (optional)")
        
        # Refresh cache option
        refresh_cache = st.checkbox("🔄 Refresh NSE Data", value=False, help="Force fetch latest NSE stock data from online source (ignores cache)")
        
        # Run scanner button
        if st.button("🚀 Run Scanner", type="primary"):
            with st.spinner("Running scanner..."):
                # Convert 0 to None (means all symbols)
                scan_limit = None if limit == 0 else limit
                result = run_scanner(scan_limit, symbols_file if symbols_file else None, refresh_cache=refresh_cache)
                
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
            
            # Minimalist results table
            if not df.empty:
                st.subheader("📊 Scanner Results")
                
                # Simple sort control
                sort_by = st.selectbox("Sort by:", ["Score", "Price", "Symbol", "Signal"], index=0)
                
                # Sort data
                if sort_by == "Score":
                    df = df.sort_values('overall_score', ascending=False)
                elif sort_by == "Price":
                    df = df.sort_values('close', ascending=False)
                elif sort_by == "Symbol":
                    df = df.sort_values('symbol')
                elif sort_by == "Signal":
                    df = df.sort_values('signal_type')
                
                # Minimalist table header
                header_cols = st.columns([2.5, 1.2, 1, 1, 1.2, 1.5, 1.5])
                with header_cols[0]:
                    st.write("**Symbol**")
                with header_cols[1]:
                    st.write("**Price**")
                with header_cols[2]:
                    st.write("**RSI**")
                with header_cols[3]:
                    st.write("**Vol**")
                with header_cols[4]:
                    st.write("**Score**")
                with header_cols[5]:
                    st.write("**Signal**")
                with header_cols[6]:
                    st.write("**Status**")
                
                st.divider()
                
                # Compact data rows
                for idx, row in df.iterrows():
                    cols = st.columns([2.5, 1.2, 1, 1, 1.2, 1.5, 1.5])
                    
                    with cols[0]:
                        # Symbol with confidence indicator
                        overall_score = row.get('overall_score', 0)
                        tech_score = row.get('technical_score', 0)
                        fund_score = row.get('fundamental_score', 0)
                        
                        # Smart scoring: try multiple score fields
                        display_score = overall_score or (tech_score + fund_score) or row.get('score', 0)
                        
                        if display_score >= 70:
                            icon = "🟢"
                        elif display_score >= 50:
                            icon = "🟡"  
                        elif display_score > 0:
                            icon = "🔴"
                        else:
                            icon = "⚪"
                        
                        st.write(f"{icon} **{row['symbol']}**")
                    
                    with cols[1]:
                        # Right-aligned price
                        st.write(f"₹{row['close']:>7.2f}")
                    
                    with cols[2]:
                        # RSI
                        rsi = row.get('rsi14', 0)
                        if rsi > 70:
                            st.write(f"�{rsi:>4.0f}")
                        elif rsi < 30:
                            st.write(f"❄️{rsi:>4.0f}")
                        else:
                            st.write(f"{rsi:>6.1f}")
                    
                    with cols[3]:
                        # Volume ratio
                        vol = row.get('vol', 0)
                        vol_avg = row.get('vol_avg20', 1)
                        vol_ratio = vol / max(1, vol_avg) if vol_avg else 0
                        
                        if vol_ratio > 2.0:
                            st.write(f"📊{vol_ratio:>3.1f}x")
                        else:
                            st.write(f"{vol_ratio:>6.1f}x")
                    
                    with cols[4]:
                        # Validation score
                        if display_score > 0:
                            if display_score > 100:  # If it's detailed scoring, normalize
                                st.write(f"{display_score/5:>5.1f}")  # Assume max 20, normalize to 4
                            else:
                                st.write(f"{display_score:>6.0f}")
                        else:
                            st.write("  -  ")
                    
                    with cols[5]:
                        # Signal type
                        signal = row.get('signal_type', 'Unknown')
                        if signal in ['breakout', 'Breakout']:
                            st.write("📈 BO")
                        elif signal in ['pullback', 'Pullback']:
                            st.write("📉 PB")
                        elif signal in ['momentum', 'Momentum']:
                            st.write("🚀 MOM")
                        else:
                            st.write(f"{signal[:8]}")
                    
                    with cols[6]:
                        # Status - recommendation or red flags
                        recommendation = row.get('recommendation', {})
                        red_flags = row.get('red_flags', [])
                        
                        if red_flags and isinstance(red_flags, list) and len(red_flags) > 0:
                            st.write("🚩 FLAGS")
                        elif recommendation and isinstance(recommendation, dict):
                            action = recommendation.get('action', '')
                            if action == 'ENTER':
                                st.write("✅ ENTER")
                            elif action == 'SKIP':
                                st.write("❌ SKIP")
                            else:
                                st.write("⚪ EVAL")
                        else:
                            # Check basic scoring confidence
                            if display_score >= 70:
                                st.write("✅ HIGH")
                            elif display_score >= 50:
                                st.write("🟡 MED")
                            elif display_score > 0:
                                st.write("🔴 LOW")
                            else:
                                st.write("⚪ NEW")
    
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