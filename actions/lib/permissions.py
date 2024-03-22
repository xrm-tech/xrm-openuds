import sys
sys.path.append('/etc/apiclient')
import apiclient

class Permissions:

    service_pool:list
    service_provider:list
    service_provider_service:list
    authenticator:list
    transport:list

    def __init__(self, primary_broker, service_pool_param, service_provider_param, authenticator_param, transport_param):
        
        self.service_pool= primary_broker.get_permissions(
            cls= service_pool_param.perm_class, 
            uuid= service_pool_param.id                                                        
        )

        self.service_provider= primary_broker.get_permissions(
            cls= service_provider_param.perm_class,
            uuid= service_provider_param.data_dict['id']
        )
        
        self.service_provider_service= primary_broker.get_permissions(
            cls= service_provider_param.service_perm_class,
            uuid= service_provider_param.service_dict['id']
        )

    def get_logs(self):

        print('Permissions [ service_pool ]: ', self.service_pool , '\n')
        print('Permissions [ service_provider ]: ', self.service_provider , '\n')
        print('Permissions [ service_provider_service ]: ', self.service_provider_service , '\n')
        #print('Permissions [ authenticator ]: ', self.authenticator , '\n')
        #print('Permissions [ transport ]: ', self.transport , '\n')    