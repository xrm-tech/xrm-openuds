import sys
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient

class Permissions:

    service_pool:list
    service_provider:list
    service_provider_service:list
    authenticators:list
    transports:list

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
            uuid= service_provider_param.base_services_list[0]['id'] #TODO: Rework, учет нескольких базовых сервисов,
            #сейчас просто заглушка, берем первый из списка. А надо обрабатывать каждый элемент
        )

        self.__get_all_auth_perm(
            broker_connection= primary_broker,
            authenticator= authenticator_param    
        )

        self._get_all_transport_perm(
            broker_connection= primary_broker,
            transport= transport_param
        )

    def __get_all_auth_perm(self, broker_connection, authenticator):
        self.authenticators=[]
        
        for auth_id in authenticator.auths_list:

            auth_perm= broker_connection.get_permissions(
                cls= authenticator.perm_class,
                uuid= auth_id['auth_id']
            )
            auth_dct= {auth_id['auth_id']:auth_perm}
            self.authenticators.append(auth_dct)
    
    def _get_all_transport_perm(self, broker_connection, transport):
        self.transports=[]

        for id in transport.ids_list:

            trans_perm= broker_connection.get_permissions(
                cls=transport.perm_class,
                uuid=id
            )

            trans_dct= {id:trans_perm}
            self.transports.append(trans_dct)

    def get_logs(self):

        print('Permissions [ service_pool ]: ', self.service_pool, '\n')
        print('Permissions [ service_provider ]: ', self.service_provider, '\n')
        print('Permissions [ service_provider_service ]: ', self.service_provider_service, '\n')
        print('Permissions [ authenticator ]: ', self.authenticators, '\n')
        print('Permissions [ transport ]: ', self.transports, '\n')
