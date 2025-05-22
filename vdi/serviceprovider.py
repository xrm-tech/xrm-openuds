import sys

sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient


class ServiceProvider:
    perm_class = 'providers'
    service_perm_class = 'service'
    __primary_broker_connection: apiclient.Client
    __secondary_broker_connection: apiclient.Client
    __old_to_new_ids_match_dict: dict
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

    def restore_base_services(self):
        """
        Восстановление базовых сервисов, которые были внутри провайдера"
        """

        created_services = {}
        for base_service in self.base_services_list:
            created_id = self.__create_base_service(base_service)
            if created_id not in created_services.values() and created_id is not None:
                created_services[base_service.get("id")] = created_id

        '''
        old id to new
        '''
        return created_services

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

        provider_type = self.data_dict.get('type_name')
        if provider_type == 'Static IP Machines Provider':

            print(f'  Supported provider type: {provider_type}')
            
            create_static_provider = (
                self.__secondary_broker_connection.create_static_provider(**self.data_dict))
            print(f"  {self.data_dict.get('name')} provider restore result: {create_static_provider}")
            created_provider_id = create_static_provider.get('id')
            return created_provider_id
        else:

            print(f'  Unsupported provider type: {provider_type}, skipping...')
            return None

    def __create_base_service(self, legacy_base_service):

        print(f"\nCreating base service \"{legacy_base_service.get('name')}\"")
        created_service_id = None
        created_service_result = "Type supported but filtered on create for some reason...Skipping"
        existing_id = self.__check_if_base_service_exist(legacy_base_service)
        if existing_id is None:

            created_provider_id, base_service_params = self.__get_base_service_params_by_type(legacy_base_service)
            if created_provider_id is not None and base_service_params is not None:

                print(f'  Creating supported base service: \"{legacy_base_service.get("name")}\" with params: {base_service_params}')
                if legacy_base_service.get('type') == 'IPMachinesService':

                    created_service_result = self.__secondary_broker_connection.create_staticmultiple_service(created_provider_id, **base_service_params)

                if created_service_result == "":

                    existing_id = self.__check_if_base_service_exist(legacy_base_service)
                    print(f'  Created \"{legacy_base_service.get("name")}\" successfully with new id {existing_id} old id is {legacy_base_service.get("id")}')
                else:
                    print(f'  {created_service_result}')

            else:

                print(f'  Unsupported base service: \"{legacy_base_service.get("name")}\" with type \"{legacy_base_service.get("type")}\"')
        else:

            print(f'  This base service is already exist with id: {existing_id}, old id is {legacy_base_service.get("id")}')
        created_service_id = existing_id
        return created_service_id

    def __get_base_service_params_by_type(self, base_service):
        supported_types = {'IPMachinesService'}
        params = None
        created_provider_id = None
        created_provider_id = self.__old_to_new_ids_match_dict.get(self.data_dict.get('id'))

        if created_provider_id is None:
            print(f"    Not found created provider id for legacy id {self.data_dict.get('id')}")

        elif base_service.get('type') in supported_types:
            params =  base_service
        return created_provider_id, params

    def __init__(self, primary_broker, service_pool_data):

        self.__primary_broker_connection = primary_broker
        self.legacy_id = service_pool_data.get('provider_id')
        self.data_dict = primary_broker.get_provider(self.legacy_id)
        self.base_services_list = self.__get_provider_base_services()

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
