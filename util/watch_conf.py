import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')
django.setup()

import consul
from order_service import consul_config
from django.conf import settings


class ConsulConfig:
    _instance = None
    config_path = os.path.join(settings.BASE_DIR, "order_service/settings.py")
    
    def __init__(self, consul_ip=None, consul_port=None):
        self.host = consul_ip if consul_ip else consul_config.CONSUL_IP
        self.port = consul_port if consul_port else consul_config.CONSUL_PORT
        self.consul = consul.Consul(host=self.host, port=self.port)
    
    def __call__(cls):
        if not cls._instance:
            cls._instance = ConsulConfig()
        return cls._instance
    
    def get_config(self):
        """
        pull config from consul
        :return:
        """
        config = self.consul.kv.get("order-settings")
        version = config[1]["ModifyIndex"]
        values = config[1]["Value"]
        values = values.decode(encoding='UTF-8', errors='strict')
        return values, version
    
    def init_config(self):
        """
        init config
        :return:
        """
        values, version = self.get_config()
        with open(self.config_path, "w") as settings_file:
            settings_file.write(values)
        consul_config.CONFIG_VERSION = version
    
    def watch_config(self):
        """
        watch consul
        :return:
        """
        values, version = self.get_config()
        if version != consul_config.CONFIG_VERSION:
            self.init_config()
            print("config is change, reload uwsgi")
            settings = object()


if __name__ == '__main__':
    obj = ConsulConfig()
    config_values = obj.init_config()
