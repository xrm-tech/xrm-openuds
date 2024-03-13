import ./lib/servicepool import ServicePool
from st2common.runners.base_action import Action

class RunGenerate(Action):
    def run(self, plan_name):

        data = {"broker_primary_ip": self.config['01_broker_primary_ip'],\
                "broker_primary_username": self.config['02_broker_primary_username'],\
                "broker_primary_auth":self.config['03_broker_primary_authenticator'],\
                "broker_primary_password": self.config['04_broker_primary_password'],\
                "broker_secondary_ip": self.config['05_broker_secondary_ip'],\
                "broker_secondary_username": self.config['06_broker_secondary_username'], \
                "broker_secondary_auth": self.config['07_broker_secondary_authenticator'],\
                "broker_secondary_password": self.config['08_broker_secondary_password'], \
                "service_pool_name": self.config['09_service_pool_name']}

        self.get_service_pool_info(
            broker_ip= data['broker_primary_ip'],
            broker_user= data['broker_primary_username'],
            broker_auth= data['broker_primary_auth'],
            broker_pwd= data['broker_primary_password'],
            pool_name= data['service_pool_name']
        )

        return True
