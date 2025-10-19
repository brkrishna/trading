from pathlib import Path
from typing import List, Dict
import json
import logging
import re

logger = logging.getLogger('trading.report')


# prefer loading a template file from trading/templates/report.html if present
from pathlib import Path as _Path

TEMPLATE_FILE = _Path(__file__).parent / 'templates' / 'report.html'

# minimal inline template fallback (kept simple because external template is preferred)
INLINE_TEMPLATE = '''
<!doctype html><html><head><meta charset="utf-8"><title>Scan Report</title></head><body>
<pre>Template file not found. Install `trading/templates/report.html` for the full report.</pre>
</body></html>
'''



def generate_html_report(candidates: List[Dict], path: Path, threshold_high: int = 75, threshold_mid: int = 40):
    """Render an interactive HTML report from candidates and write to path.

    Candidates should be a list of JSON-serializable dict-like objects.
    """
    # Ensure every candidate is JSON-serializable for embedding
    def _safe(obj):
        # convert any non-serializable fields if needed
        o = dict(obj)
        # ensure lists for tags/history
        o['reason_tags'] = o.get('reason_tags') or []
        o['history'] = o.get('history') or []
        o['metrics'] = o.get('metrics') or {}
        return o

    data = [_safe(c) for c in candidates]
    candidates_json = json.dumps(data)

    # compute some quick stats for the report header
    from datetime import datetime, timedelta, timezone
    # Try to format timestamp in India Standard Time (Asia/Kolkata). Use zoneinfo if available.
    try:
        try:
            from zoneinfo import ZoneInfo  # Python 3.9+
            ist = ZoneInfo('Asia/Kolkata')
            generated_at = datetime.now(tz=ist).strftime('%Y-%m-%d %H:%M:%S %Z')
        except Exception:
            # Fallback: apply +5:30 offset to UTC
            ist_offset = timezone(timedelta(hours=5, minutes=30))
            generated_at = datetime.now(tz=ist_offset).strftime('%Y-%m-%d %H:%M:%S IST')
    except Exception:
        # Last resort: UTC with Z
        generated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ')
    total_candidates = len(data)
    count_high = sum(1 for c in data if int(c.get('score') or 0) >= threshold_high)
    count_mid = sum(1 for c in data if threshold_mid <= int(c.get('score') or 0) < threshold_high)
    count_low = total_candidates - count_high - count_mid
    # best-effort last data date from candidates
    last_data_date = None
    try:
        dates = [c.get('date') for c in data if c.get('date')]
        last_data_date = max(dates) if dates else None
    except Exception:
        last_data_date = None

    # Choose template source: external file preferred
    if TEMPLATE_FILE.exists():
        template_text = TEMPLATE_FILE.read_text(encoding='utf-8')
    else:
        template_text = INLINE_TEMPLATE

    # Try to render with Jinja2 if available using a safe Environment
    try:
        import jinja2
        try:
            env = jinja2.Environment(
                loader=jinja2.BaseLoader(),
                autoescape=jinja2.select_autoescape(['html', 'xml'])
            )
            # ensure tojson is available
            env.filters['tojson'] = jinja2.filters.do_tojson
            tpl = env.from_string(template_text)
            html = tpl.render(
                candidates=data,
                threshold_high=threshold_high,
                threshold_mid=threshold_mid,
                generated_at=generated_at,
                total_candidates=total_candidates,
                count_high=count_high,
                count_mid=count_mid,
                count_low=count_low,
                last_data_date=last_data_date,
            )
        except Exception:
            logger.exception('Jinja2 rendering failed, falling back to raw template insertion')
            html = template_text.replace('%%CANDIDATES_JSON%%', candidates_json)
    except Exception:
        # Jinja2 not available; fallback to basic replacement
        html = template_text.replace('%%CANDIDATES_JSON%%', candidates_json)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding='utf-8')

