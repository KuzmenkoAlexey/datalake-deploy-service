from celery import Celery

app = Celery("worker", broker="amqp://rabbit", include=["worker.tasks"])
