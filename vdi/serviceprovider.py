import sys

sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient


class ServiceProvider:
    perm_class = 'providers'
    service_perm_class = 'service'
    __primary_broker_connection: apiclient.Client
    __secondary_broker_connection: apiclient.Client
    __old_to_new_ids_match_dict: dict
    __base_service_linked_to_servpool_name: str
    data_dict: dict
    base_services_list = []

    def restore(self):
        """
        Восстановление Сервис-провайдера, если такого (имя+тип) еще нет
        """
        print("\nCreating static provider")
        self.__old_to_new_ids_match_dict = {}
        existing_id = self.__check_if_provider_exist()
        if existing_id is not None:

            print(f'  Found already existing provider \"{self.data_dict.get("name")}\"with id: \"{existing_id}\", no need to create new one')
            self.__old_to_new_ids_match_dict.update({
                self.data_dict.get('id'): existing_id
            })

        else:
            print(f'  Not found existing provider \"{self.data_dict.get("name")}\", need to create new one')
            created_provider_id = self.__create_provider_by_type()
            if created_provider_id is not None:

                self.__old_to_new_ids_match_dict.update({
                    self.data_dict.get('id'): created_provider_id
                })

        print(f"  Created provider id match dict: {self.__old_to_new_ids_match_dict}")

        return self.__old_to_new_ids_match_dict

    def restore_base_service(self):
        """
        Восстановление привязанного базового сервиса"
        """
        
        print(f' \nRestoring base service "{self.__base_service_linked_to_servpool_name}"')
        for legacy_base_service in self.base_services_list:
            
            if legacy_base_service.get('name') == self.__base_service_linked_to_servpool_name:
                existing_id = self.__check_if_base_service_exist(legacy_base_service)
                if existing_id is None:
                    print(f"  \nCreating base service {legacy_base_service.get('name')}")
                    created_service_id = self.__create_base_service_by_type(legacy_base_service)
                else:
                    print(f'  This base service is already exist with id: {existing_id}, old id is {legacy_base_service.get("id")}')
                    created_service_id = existing_id

                '''
                old id to new
                '''
                return {legacy_base_service.get('id'):created_service_id}
        return None

    def __check_if_provider_exist(self):

        existing_providers_list = self.__secondary_broker_connection.list_providers()
        print(f'  Already existing providers list: {existing_providers_list}')
        for provider in existing_providers_list:
            if (provider.get('name') == self.data_dict.get('name')
                    and provider.get('type_name') == self.data_dict.get('type_name')):

                return provider.get('id')
        return None

    def __check_if_base_service_exist(self, legacy_base_service):

        legacy_provider_id = self.data_dict.get('id')
        created_provider_id = self.__old_to_new_ids_match_dict.get(legacy_provider_id)
        existing_base_services_list = self.__secondary_broker_connection.list_provider_services(created_provider_id)
        print(f'  Already existing base services list: {existing_base_services_list}')
        for base_service in existing_base_services_list:
            if (base_service.get('name') == legacy_base_service.get('name')
                    and base_service.get('type_name') == legacy_base_service.get('type_name')):

                return base_service.get('id')

        return None

    def __create_provider_by_type(self):

        SUPPORTED_TYPES = {"Static IP Machines Provider", "oVirt/RHEV Platform Provider"}    
        provider_type = self.data_dict.get('type_name')
        created_provider = None
        
        if provider_type in SUPPORTED_TYPES:
            print(f'  Supported provider type: {provider_type}')

            if provider_type == 'Static IP Machines Provider':                
                created_provider = (
                    self.__secondary_broker_connection.create_static_provider(**self.data_dict))         
            
            elif provider_type == 'oVirt/RHEV Platform Provider':     
                data_dict_copy = self.data_dict.copy()
                data_dict_copy.pop("id", None)
                data_dict_copy.pop("name", None)
                data_dict_copy.pop("services_count", None)
                data_dict_copy.pop("user_services_count", None)
                data_dict_copy.pop("maintenance_mode", None)
                data_dict_copy.pop("offers", None)
                data_dict_copy.pop("type_name", None)
                data_dict_copy.pop("permission", None)
                print(data_dict_copy)

                created_provider = (
                    self.__secondary_broker_connection.create_ovirt_provider(name = self.data_dict.get('name'), **data_dict_copy)) 

            print(f"  {self.data_dict.get('name')} provider restore result: {created_provider}")          
        else:

            print(f'  Unsupported provider type: {provider_type}, skipping...')
        return created_provider.get('id')

    def __create_base_service_by_type(self, legacy_base_service:dict):
        SUPPORTED_TYPES = {'IPMachinesService','oVirtLinkedService','oVirtFixedService'}
        base_service_type = legacy_base_service.get('type')
        created_provider_id = self.__old_to_new_ids_match_dict.get(self.data_dict.get('id'))

        if base_service_type in SUPPORTED_TYPES:            
            
            if created_provider_id is not None:
                base_service_copy = legacy_base_service.copy()
                fields_to_remove = [
                    "id","type_name", "type", "proxy", "deployed_services_count",
                    "user_services_count", "maintenance_mode", "permission",
                    "info", "ov", "ev"
                ]
                for field in fields_to_remove:
                    base_service_copy.pop(field, None)            

                if base_service_type == 'IPMachinesService':
                    created_base_service = self.__secondary_broker_connection.create_staticmultiple_service(provider_id=created_provider_id, **base_service_copy)
                
                elif base_service_type == 'oVirtFixedService':
                    if 'machine' in base_service_copy and isinstance(base_service_copy['machine'], list):
                        base_service_copy['machine'] = [vm['id'] for vm in base_service_copy['machine']]                
                    created_base_service = self.__secondary_broker_connection.create_ovirtfixed_service(provider_id=created_provider_id, **base_service_copy)
                
                elif base_service_type == 'oVirtLinkedService':  
                     
                    created_base_service = self.__secondary_broker_connection.create_ovirtlinked_service(provider_id=created_provider_id, **base_service_copy)  
                
                base_services_list = self.__secondary_broker_connection.list_provider_services(created_provider_id)
                print(base_services_list)
                for base_service in base_services_list:
                    print(base_service)
                    if base_service.get('name') == legacy_base_service.get('name'):
                        created_base_Service_id = base_service.get('id')
                        print(f"  Created base service id: {created_base_service}")
                        return created_base_Service_id
                print("  Warning: Cant find base service after creation")
            else:
                print(f"    Not found created provider id for legacy id {self.data_dict.get('id')}")
        else:
            print(f'  Unsupported base service: \"{legacy_base_service.get("name")}\" with type \"{legacy_base_service.get("type")}\"')    

    def __init__(self, primary_broker, service_pool_data):

        self.__primary_broker_connection = primary_broker
        self.legacy_id = service_pool_data.get('provider_id')
        self.data_dict = primary_broker.get_provider(self.legacy_id)
        self.base_services_list = self.__get_provider_base_services()
        self.__base_service_linked_to_servpool_name = service_pool_data.get('parent')

    def __get_provider_base_services(self):

        base_services_data = []
        base_services = self.__primary_broker_connection.list_provider_services(self.legacy_id)
        for base_service in base_services:

            base_service_data = self.__primary_broker_connection.get_provider_service(self.legacy_id, base_service.get('id'))
            if base_service_data is not None:

                base_services_data.append(base_service_data)

        return base_services_data

    def set_connection(self, secondary_broker_connection):
        self.__secondary_broker_connection = secondary_broker_connection

    def get_logs(self):
        print('ServiceProvider [ data ]: ', self.data_dict, '\n')
        print('ServiceProvider [ base_services ]: ', self.base_services_list, '\n')
