import base64
import os
import requests
import sys
sys.path.append('/etc/apiclient')
import apiclient
from st2common.runners.base_action import Action

class RunGenerate(Action):

    def get_service_pool_info(self, broker_ip, broker_auth, broker_user, broker_pwd, pool_name):

        vdi= apiclient.Client(
            _host= broker_ip,
            _auth= broker_auth,
            _username= broker_user,
            _password= broker_pwd
        )

    try:
        vdi.login()  # Подключение к брокеру
        print(vdi.get_config())  # Вывод на экран конфигурации брокера
        vdi.logout()  # Завершение сессии
    except ValueError as e:
        print('Invalid data: {}'.format(e))
    except Exception as e:
        raise('Caught exception: {}'.format(e))

    
    def run(self, plan_name):

        data = {"broker_primary_url": self.config['01_broker_primary_url'],\
                "broker_primary_username": self.config['02_broker_primary_username'],\
                "broker_primary_auth":self.config['03_broker_primary_authenticator'],\
                "broker_primary_password": self.config['04_broker_primary_password'],\
                "broker_secondary_url": self.config['05_broker_secondary_url'],\
                "broker_secondary_username": self.config['06_broker_secondary_username'], \
                "broker_secondary_auth": self.config['07_broker_secondary_authenticator'],\
                "broker_secondary_password": self.config['08_broker_secondary_password'], \
                "service_pool_name": self.config['09_service_pool_name']}

        get_service_pool_info(
            broker_ip= data['broker_primary_url'],
            broker_user= data['broker_primary_username'],
            broker_auth= data['broker_primary_auth'],
            broker_pwd= data['broker_primary_password'],
            pool_name= data['service_pool_name']
        )

        return True
