##### 1.遵循PEP8规范，命名规范，见名知意

​		落地方案可参考：pre-commit



##### 2.不要硬编码，尽量可配置化

​		增加配置表，常用的配置读数据库



##### 3.尽可能使用纯函数，函数之间解耦，功能单一

​		不要把大量的逻辑放在一个函数里，尽量让函数的功能单一，输入输出类型尽可能的说明

​		输出尽可能统一类型，不要一会return bool，一会return 字符串

```python
def trap_http_exception(self, e: Exception) -> bool:
        if self.config["TRAP_HTTP_EXCEPTIONS"]:
            return True

        trap_bad_request = self.config["TRAP_BAD_REQUEST_ERRORS"]

        # if unset, trap key errors in debug mode
        if (
            trap_bad_request is None
            and self.debug
            and isinstance(e, BadRequestKeyError)
        ):
            return True

        if trap_bad_request:
            return isinstance(e, BadRequest)

        return False
    

```

​		

##### 4.不要做重复的事情, 参考django的ORM源码

​		当一部分代码重复的时候，需要抽离出一个基类，基类用来做底层实现，工具类继承基类，用来做差异化处理

```python
class ConnectionHandler:
  	"""
  	操作数据库
  	"""
    def __init__(self, databases=None):
        """
        databases is an optional dictionary of database definitions (structured
        like settings.DATABASES).
        """
        self._databases = databases
        self._connections = local()

    @cached_property
    def databases(self):
        if self._databases is None:
            self._databases = settings.DATABASES
        if self._databases == {}:
            self._databases = {
                DEFAULT_DB_ALIAS: {
                    'ENGINE': 'django.db.backends.dummy',
                },
            }
        if DEFAULT_DB_ALIAS not in self._databases:
            raise ImproperlyConfigured("You must define a '%s' database." % DEFAULT_DB_ALIAS)
        if self._databases[DEFAULT_DB_ALIAS] == {}:
            self._databases[DEFAULT_DB_ALIAS]['ENGINE'] = 'django.db.backends.dummy'
        return self._databases
      

class Model(metaclass=ModelBase):
		"""
		操作模型
		"""
    def __init__(self, *args, **kwargs):
        # Alias some things as locals to avoid repeat global lookups
   	def save(self, *args, **kwargs):
      pass
    
    def update(self, *args, **kwargs):
      pass
      
class BaseModel(models.Model):
    """
    标准抽象模型模型
    """
    update_time = UpdateDateTimeField()  # 修改时间
    create_time = CreateDateTimeField()  # 创建时间

    class Meta:
        abstract = True
        verbose_name = '基本模型'
        verbose_name_plural = verbose_name
        
        
class TaskMapAnalysis(BaseModel):
  	"""
    差异化模型
    """
    shop_id = models.CharField(max_length=32, verbose_name='门店id')
    shop_map_id = JSONField(verbose_name='门店json地图id', default=[])
    local = models.CharField(max_length=32, verbose_name='本地或出差')

    class Meta:
        db_table = 'work_map_analysis'
        verbose_name = '门店地图解析表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.task_no
```



##### 5. 约定大于一切，定自己规则，让别人遵循, 比如一些SDK，OpenApi，一些组件

```python
# 先注册消息，这个消息是干嘛的
<?xml version="1.0" encoding="UTF-8" ?>
<openerp>
    <data noupdate="1">
        <record id="mq_nt_invoice_callback_api" model="ir.message_queue">
            <field name="name">开票完成回调</field>
            <field name="code">NT#INVOICE#INFO#CALLBACK</field>
        </record>
    </data>
</openerp>

# 发送消息
class invoice_api(osv.osv_memory):
    _inherit = 'nt.invoice.api'

    # 开票完成回调
    @decorator.route("/api/v6/invoice/invoice_info/post", methods=['post'])
    @decorator.login_required()
    @decorator.api_validate("nt_invoice_starbucks_api/api_define/push_starbucks_invoice_callback_info.yml", validation=True)
    def api_invoice_callback_info(pool, cr, uid, context=None):
        data = request.json
        _logger.info('traceId: {};[API_INVOICE_CALLBACK_INFO] {}'.format(context.get('X-Request-Id'), json.dumps(data)))
        MQConnection.send(cr.dbname, 'NT#INVOICE#INFO#CALLBACK', data)

        return {}

@subscribe('NT#INVOICE#INFO#CALLBACK', 'nt.invoice.api', 'nt_mq_invoice_info_callback')
    def nt_mq_invoice_info_callback(self, cr, uid, data):
    		"异步处理逻辑"
        pass
      

```



push_starbucks_invoice_callback_info.yml文件，用来定义入参类型

```yaml
Starbucks 申请开票backend
---
tags:
  - Starbucks 申请开票backend

summary: Starbucks 申请开票backend
description: Starbucks 申请开票backend

parameters:
- name: request_invoice_backend
  in: body
  description:
  required: True
  schema:
    id: request_invoice_backend
    required:
    - order_list
    properties:
      data:
        type: array
        description: 申请开票backend

```



##### 6.统一风格，统一异常处理，统一log打印规范， 统一response，让整个项目看上去就像一个人编写的

```python
class BaseResponse(Response):
  """
  统一response
  """
    def __init__(self, code=CODE_SUCCESS, message=MSG_SUCCESS, data={}, status=status.HTTP_200_OK,
                 template_name=None, headers=None, exception=False, content_type='application/json'):
        super(Response, self).__init__(None, status=status)
        self._code = code
        self._message = message
        self._data = data

        self.data = {"code": code, "message": message, "data": data}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value
 
    @code.setter
    def code(self, value):
        self._code = value

    @message.setter
    def message(self, value):
        self._message = value

    @data.setter
    def data(self, value):
        self._data = value
        
        
 def common_exception_handler(ex, context):
    """
        统一异常拦截处理
        目的:(1)取消所有的500异常响应,统一响应为标准错误返回
            (2)准确显示错误信息
        :param ex:
        :param context:
        :return:
        """
    msg = ''
    code = '201'

    if isinstance(ex, AuthenticationFailed):
        code = 401
        msg = ex.detail
    elif isinstance(ex, DRFAPIException):
        set_rollback()
        msg = ex.detail
    elif isinstance(ex, exceptions.APIException):
        set_rollback()
        msg = ex.detail
    elif isinstance(ex, Exception):
        logger.error(traceback.format_exc())
        msg = str(ex)
    return BaseResponse(message=msg, code=code)
  
  
  class invoice_api(osv.osv_memory):
    _inherit = 'nt.invoice.api'

    
    # 开票完成回调
    @decorator.route("/api/v6/invoice/invoice_info/post", methods=['post'])
    @decorator.login_required()
    @decorator.api_validate("nt_invoice_starbucks_api/api_define/push_starbucks_invoice_callback_info.yml", validation=True)
    def api_invoice_callback_info(pool, cr, uid, context=None):
        data = request.json
        _logger.info('traceId: {};[API_INVOICE_CALLBACK_INFO] {}'.format(context.get('X-Request-Id'), json.dumps(data)))
        MQConnection.send(cr.dbname, 'NT#INVOICE#INFO#CALLBACK', data)

        return {}
```



##### 7.尽量的使用设计模式，单列，工厂，代理类等等

```
多看源码，学习模仿
```





​		

​		