from lib.servicepool import ServicePool
from st2common.runners.base_action import Action
sys.path.append('/etc/apiclient')
import apiclient

class RunGenerate(Action):
    def run(self, plan_name):
        data = {"broker_primary_ip": self.config['01_broker_primary_ip'],
                "broker_primary_username": self.config['02_broker_primary_username'],
                "broker_primary_auth": self.config['03_broker_primary_authenticator'],
                "broker_primary_password": self.config['04_broker_primary_password'],
                "broker_secondary_ip": self.config['05_broker_secondary_ip'],
                "broker_secondary_username": self.config['06_broker_secondary_username'],
                "broker_secondary_auth": self.config['07_broker_secondary_authenticator'],
                "broker_secondary_password": self.config['08_broker_secondary_password'],
                "service_pool_name": self.config['09_service_pool_name']}

        primary_broker_connection = apiclient.Client(
            host=data['broker_primary_ip'],
            username=data['broker_primary_username'],
            auth=data['broker_primary_auth'],
            password=data['broker_primary_password']
        )    

        service_pool = ServicePool(
            primary_broker= primary_broker_connection,
            pool_name=data['service_pool_name']
        )

        return True
