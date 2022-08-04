import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "order_service.settings")
django.setup()
from order.tasks import async_func

if __name__ == '__main__':
    result = async_func.delay()
    print(f'product send message: {result}')
