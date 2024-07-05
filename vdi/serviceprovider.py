import sys
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient

class ServiceProvider:
    
    perm_class= 'providers'
    service_perm_class= 'service'
    
    data_dict: dict
    service_dict: dict

    def __init__(self, primary_broker, service_pool_data):

        provider_id= service_pool_data['provider_id']
        service_id= service_pool_data['service_id']

        self.data_dict= primary_broker.get_provider(provider_id)
        self.service_dict= primary_broker.get_provider_service(provider_id, service_id)

    def get_logs(self):

        print('ServiceProvider [ data ]: ', self.data_dict , '\n')
        print('ServiceProvider [ service ]: ', self.service_dict, '\n')