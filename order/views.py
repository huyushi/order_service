from django.shortcuts import HttpResponse
from order.tasks import async_func


# Create your views here.
def login(request):
    result = async_func.delay()
    print('开始处理请求啦', result)
    return HttpResponse("hello world")


