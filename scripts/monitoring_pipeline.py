import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.monitoring.drift_monitoring import *
from prefect import flow, task

@task(name="Get_total_rows_from_prod", retries=3, retry_delay_seconds=10)
def get_total_rows_from_prod_task():
    return get_record_count()

@task(name="Get_last_monitored_rows", retries=3, retry_delay_seconds=10)
def get_last_monitored_rows_task():
    return get_last_monitored_count()

@task(name="Fetch_production_data", retries=3, retry_delay_seconds=10)
def fetch_production_data_task(offset: int, limit: int = 100):
    return fetch_production_data(offset=offset, limit=limit)

@task(name="Generate_and_log_drift_report", retries=3, retry_delay_seconds=10)
def generate_and_log_drift_report_task(df, report_index: int):
    generate_and_log_drift_report(df, report_index=report_index)

@task(name="Log_monitoring_checkpoint", retries=3, retry_delay_seconds=10)
def log_monitoring_checkpoint_task(records_count: int):
    log_monitoring_checkpoint(records_count=records_count)

@flow(name="drift_monitoring")
def monitoring_flow():
    total_count = get_total_rows_from_prod_task()
    last_monitored = get_last_monitored_rows_task()

    new_records = total_count - last_monitored 

    if new_records < 100:
        print(f"Za mało nowych rekordów: {new_records}/100")
        return

    batches = new_records // 100
    print(f"Generuję {batches} raport")

    for i in range(batches):
        offset = last_monitored + (i * 100)
        report_index = (last_monitored // 100) + i + 1
        df = fetch_production_data_task(offset=offset, limit=100)
        generate_and_log_drift_report_task(df, report_index=report_index)
        log_monitoring_checkpoint_task(records_count=offset + 100)

if __name__ == "__main__":
    while True:
        monitoring_flow()
        time.sleep(10)