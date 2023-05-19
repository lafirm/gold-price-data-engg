from airflow.decorators import dag, task
from datetime import datetime
import gold_price_script as gs


@dag(schedule="@daily", start_date=datetime(2023, 1, 1), catchup=False, tags=["taskflow-api-demo"])
def gold_price_dag() -> None:
    extract_goldrate_data = task(multiple_outputs=False)(gs.extract_goldrate_data)
    extract_inr_conv_rate = task(multiple_outputs=False)(gs.extract_inr_conv_rate)
    transform = task(multiple_outputs=False)(gs.transform)
    load = task(multiple_outputs=False)(gs.load)
    send_discord_message = task()(gs.send_discord_message)
    data = transform(goldrate_raw=extract_goldrate_data(), inr_data_raw=extract_inr_conv_rate())
    load(data)
    send_discord_message(data)
    return None

gold_price_dag()
