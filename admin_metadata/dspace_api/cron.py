from celery import shared_task
from .services import fetch_and_update_collections

@shared_task
def sync_collections_task():
    result = fetch_and_update_collections()
    return result
