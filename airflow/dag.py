from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 13),
    'catchup': False,
}

# DAG 1: Customer Profile
create_customer_dag = DAG(
    dag_id='customer_profile',
    default_args=default_args,
    schedule_interval='*/15 * * * *',
)

create_customer_task = BashOperator(
    task_id='customer_profile',
    bash_command='python3 /opt/airflow/python/synthetic_data_generator/ecommerce/services/user_management/customer_profile.py',
    dag=create_customer_dag,
)

customer_order_dag = DAG(
    dag_id='customer_order',
    default_args=default_args,
    schedule_interval='*/1 * 13 5 2',
)

# Customer order task (BashOperator)
customer_order_task = BashOperator(
    task_id='customer_order',
    bash_command='python3 /opt/airflow/python/synthetic_data_generator/ecommerce/services/order_management/producer.py',
    dag=customer_order_dag,
)
