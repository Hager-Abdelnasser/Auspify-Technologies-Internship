import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOGS = BASE / "outputs" / "console_logs"
LOGS.mkdir(parents=True, exist_ok=True)

SCRIPTS = [
    "task1_data_cleaning.py",
    "task2_content_type_dashboard.py",
    "task3_country_analysis.py",
    "task4_release_year_trends.py",
    "task5_rating_genre_analysis.py",
    "task6_business_insights_report.py",
]

for script in SCRIPTS:
    result = subprocess.run([sys.executable, "-W", "ignore", str(BASE / script)], capture_output=True, text=True, cwd=BASE)
    (LOGS / f"{Path(script).stem}_output.txt").write_text(result.stdout, encoding="utf-8")
    status = "OK" if result.returncode == 0 else "FAILED"
    print(f"{status:7} {script}")
    if result.returncode != 0:
        print(result.stderr)
        break
