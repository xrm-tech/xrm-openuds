import pickle
import sys, os

sys.path.append(os.path.abspath('.'))
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
from st2common.runners.base_action import Action
from vdi import *
from apiclient import Client


class RunFailOver(Action):
    __result = None
    packs_path = '/opt/stackstorm/packs/saved/'

    def __send_data(self, plan_data_list_param):

        for plan_data_dict in plan_data_list_param:

            try:
                service_name = plan_data_dict['service_name']
                service_pool = plan_data_dict['service_pool']
                service_provider = plan_data_dict['service_provider']
                authenticator = plan_data_dict['authenticator']
                transport = plan_data_dict['transport']
                permissions = plan_data_dict['permissions']

                dst_broker_ip = plan_data_dict['dst_broker_ip']
                dst_broker_user = plan_data_dict['dst_broker_user']
                dst_broker_auth = plan_data_dict['dst_broker_auth']
                dst_broker_pwd = plan_data_dict['dst_broker_pwd']

                print(f'\nTrying to send "{service_name}" data to secondary broker')

                dst_broker_connection = Client(
                    host=dst_broker_ip,
                    auth=dst_broker_auth,
                    username=dst_broker_user,
                    password=dst_broker_pwd
                )
                dst_broker_connection.login()

                print("\nCreating static provider")

                params = {
                    'name': service_provider.data_dict['name'],
                    'comments': service_provider.data_dict['comments'],
                    'tags': service_provider.data_dict['tags'],
                    'config': service_provider.data_dict['config']
                }
                not_none_static_provider_params = {k: v for k, v in params.items() if v is not None}
                create_static_provider = dst_broker_connection.create_static_provider(**not_none_static_provider_params)

                created_provider_id = create_static_provider['id']
                print(f'  {create_static_provider}')

                #TODO: обработка нескольких базовых сервисов, в текущей реализации - только один.
                print("\nCreating static multiple service")

                params = {
                    'provider_id': created_provider_id,
                    'name': service_provider.service_dict['name'],
                    'comments': service_provider.service_dict['comments'],
                    'tags': service_provider.service_dict['tags'],
                    'iplist': service_provider.service_dict['ipList'],
                    'token': service_provider.service_dict['token'],
                    'port': service_provider.service_dict['port'],
                    'skipTimeOnFailure': service_provider.service_dict['skipTimeOnFailure'],
                    'maxSessionForMachine': service_provider.service_dict['maxSessionForMachine'],
                    'lockByExternalAccess': service_provider.service_dict['lockByExternalAccess'],
                }
                not_none_staticmultiple_service_params = {k: v for k, v in params.items() if v is not None}

                create_staticmultiple_service = dst_broker_connection.create_staticmultiple_service(
                    **not_none_staticmultiple_service_params)
                created_provider_services_list = dst_broker_connection.list_provider_services(created_provider_id)

                '''
                Создание сервис-пулов         TODO: перепроверить.
                '''
                for created_provider_service in created_provider_services_list:
                    print(f'  {created_provider_service}')

                    created_service_id = created_provider_service['id']
                    servicepool_name = service_pool.data_dict['name']
                    print(f'\nCreating service pool {servicepool_name}')

                    params = {
                        'name': service_pool.data_dict['name'],
                        'service_id': created_service_id,
                        'short_name': service_pool.data_dict['short_name'],
                        'comments': service_pool.data_dict['comments'],
                        'tags': service_pool.data_dict['tags'],
                        'visible': service_pool.data_dict['visible'],
                        'image_id': service_pool.data_dict['image_id'],
                        'pool_group_id': service_pool.data_dict['pool_group_id'],
                        'calendar_message': service_pool.data_dict['calendar_message'],
                        'allow_users_remove': service_pool.data_dict['allow_users_remove'],
                        'allow_users_reset': service_pool.data_dict['allow_users_reset'],
                        'ignores_unused': service_pool.data_dict['ignores_unused'],
                        'show_transports': service_pool.data_dict['show_transports'],
                        'account_id': service_pool.data_dict['account_id'],
                        'initial_srvs': service_pool.data_dict['initial_srvs'],
                        'cache_l1_srvs': service_pool.data_dict['cache_l1_srvs'],
                        'cache_l2_srvs': service_pool.data_dict['cache_l2_srvs'],
                        'max_srvs': service_pool.data_dict['max_srvs'],
                    }
                    not_none_auth_params = {k: v for k, v in params.items() if v is not None}

                    created_service_pool = dst_broker_connection.create_pool(**not_none_auth_params)
                    print(f'  {created_service_pool}')

                    '''
                    Создание аутентификаторов  TODO: остальные типы аутентификаторов
                    '''
                    print(f'\nCreating authenticators')

                    for auth in authenticator.data_list:
                        name = auth['name']
                        legacy_id = auth['id']
                        type_name = auth['type_name']
                        auth_name_str = f'{name} as {type_name}'
                        supported = True

                        if (auth['type'] == 'ActiveDirectoryAuthenticator'):
                            print(f'\n  Creating {auth_name_str}')

                            params = {
                                'name': auth.get('name'),
                                'label': auth.get('small_name'),
                                'host': auth.get('host'),
                                'username': auth.get('username'),
                                'password': auth.get('password'),
                                'ldapBase': auth.get('ldapBase'),
                                'comments': auth.get('comments'),
                                'tags': auth.get('tags'),
                                'priority': auth.get('priority'),
                                'ssl': auth.get('ssl'),
                                'timeout': auth.get('timeout'),
                                'groupBase': auth.get('groupBase'),
                                'defaultDomain': auth.get('defaultDomain'),
                                'nestedGroups': auth.get('nestedGroups'),
                                'visible': auth.get('visible'),
                            }
                            not_none_auth_params = {k: v for k, v in params.items() if v is not None}
                            created_auth = dst_broker_connection.create_ad_auth(**not_none_auth_params)
                            print(f'    Result: {created_auth}')

                        elif (auth['type'] == 'InternalDBAuth'):
                            print(f'\n  Creating {auth_name_str}')

                            params = {
                                'name': auth.get('name'),
                                'comments': auth.get('comments'),
                                'tags': auth.get('tags'),
                                'priority': auth.get('priority'),
                                'label': auth.get('small_name'),
                                'differentForEachHost': auth.get('differentForEachHost'),
                                'reverseDns': auth.get('reverseDns'),
                                'acceptProxy': auth.get('acceptProxy'),
                                'visible': auth.get('visible')
                            }
                            not_none_auth_params = {k: v for k, v in params.items() if v is not None}
                            created_auth = dst_broker_connection.create_internal_auth(**not_none_auth_params)
                            print(f'  Result: {created_auth}')

                        else:
                            supported = False
                            print(f'\n!!! Warning: skipping unsupported authenticator {auth_name_str}')

                        if (supported):
                            '''
                            Создание групп аутентификатора
                            '''
                            print(f'\n    Creating authenticator groups')

                            '''legacy_group_id: new_group_data'''
                            group_id_comparison = {}

                            for group in authenticator.groups_list:
                                #TODO: если у одной группы несколько пулов, то группы, скорее-всего, задаблятся                       
                                if str(legacy_id) in group:
                                    group_data = group[str(legacy_id)]
                                    params = {
                                        'auth_id': created_auth.get('id'),
                                        'name': group_data.get('name'),
                                        'comments': group_data.get('comments'),
                                        'state': group_data.get('state'),
                                        'meta_if_any': group_data.get('meta_if_any'),
                                        'pools': str(created_service_pool.get('id'))
                                    }
                                    not_none_group_params = {k: v for k, v in params.items() if v is not None}

                                    not_none_group_params['pools'] = [not_none_group_params['pools']]
                                    created_auth_group = dst_broker_connection.create_auth_group(
                                        **not_none_group_params)
                                    group_name = group_data.get('name')
                                    if (created_auth_group == ''):
                                        print(f'      Created {group_name} group succesfully')
                                        '''
                                        Получение информации о новосозданной группе и сопоставление одной группы между src и dst брокерами
                                        '''
                                        pool_groups_list= dst_broker_connection.list_pool_groups(created_service_pool.get('id'))
                                        created_group = next(group for group in pool_groups_list if (
                                            group.get('auth_id') == created_auth.get('id') and group.get('name') == group_name
                                        ))
                                        group_id_comparison.update({group_data.get('id'): created_group})

                                    else:
                                        print(f'\n{created_auth_group}')

                            '''
                            Создание пользователей
                            TODO: проверить, что это корректно для AD
                            '''
                            print(f'\n    Creating authenticator users')
                            for user in authenticator.users_list:
                                legacy_groups_list= user.get('groups')
                                created_groups_list=[]
                                print(created_groups_list)
                                if legacy_groups_list is not None:
                                    for legacy_group_id in legacy_groups_list:
                                        created_group_id= group_id_comparison.get(legacy_group_id)
                                        if created_group_id is not None:
                                            created_groups_list.append(created_group_id)

                                params= {
                                    'auth_id': created_auth.get('id'),
                                    'username': user.get('name'),
                                    'realname': user.get('real_name'),
                                    'comments': user.get('comments'),
                                    'state': user.get('state'),
                                    'password': user.get('password'),
                                    'role': user.get('role'),
                                    'groups': created_groups_list,
                                }
                                not_none_user_params = {k: v for k, v in params.items() if v is not None}
                                created_auth_user_result= dst_broker_connection.create_auth_user(**not_none_user_params)
                                if not created_auth_user_result:
                                    print(f'      Created {user.get("name")} user succesfully')
                                else:
                                    print(f'!!! Warning: {created_auth_user_result}')

                    '''
                    Создание транспортов
                    '''
                    print(f'\nCreating transports')

                    #TODO: добавить туннельный rdp
                    print(transport)
                    for trans in transport.data:
                        trans_name_str = str(trans['name'])

                        if (trans['type'] == 'RDPTransport'):
                            params = {
                                'name': trans.get('name'),
                                'type': trans.get('type'),
                                'pools': created_service_pool.get('id'),
                                'useEmptyCreds': trans.get('useEmptyCreds'),
                                'fixedName': trans.get('fixedName'),
                                'fixedPassword': trans.get('fixedPassword'),
                                'withoutDomain': trans.get('withoutDomain'),
                                'fixedDomain': trans.get('fixedDomain'),
                                'allowSmartcards': trans.get('allowSmartcards'),
                                'allowPrinters': trans.get('allowPrinters'),
                                'allowDrives': trans.get('allowDrives'),
                                'enforceDrives': trans.get('enforceDrives'),
                                'allowSerials': trans.get('allowSerials'),
                                'allowClipboard': trans.get('allowClipboard'),
                                'allowAudio': trans.get('allowAudio'),
                                'allowWebcam': trans.get('allowWebcam'),
                                'usbRedirection': trans.get('usbRedirection'),
                                'wallpaper': trans.get('wallpaper'),
                                'multimon': trans.get('multimon'),
                                'aero': trans.get('aero'),
                                'smooth': trans.get('smooth'),
                                'showConnectionBar': trans.get('showConnectionBar'),
                                'credssp': trans.get('credssp'),
                                'rdpPort': trans.get('rdpPort'),
                                'screenSize': trans.get('screenSize'),
                                'colorDepth': trans.get('colorDepth'),
                                'alsa': trans.get('alsa'),
                                'multimedia': trans.get('multimedia'),
                                'printerString': trans.get('printerString'),
                                'smartcardString': trans.get('smartcardString'),
                                'customParameters': trans.get('customParameters'),
                                'allowMacMSRDC': trans.get('allowMacMSRDC'),
                                'customParametersMAC': trans.get('customParametersMAC'),
                            }
                            not_none_transport_params = {k: str(v) for k, v in params.items() if v is not None}
                            not_none_transport_params['pools'] = [not_none_transport_params['pools']]

                            created_transport = dst_broker_connection.create_rdpdirect_transport(
                                **not_none_transport_params)
                            print(f'\n{created_transport}\nCreated {trans_name_str} succesfully.')

                        else:
                            print(f'\nWarning: skipping unsupported transport {trans_name_str}')

                        #TODO: permissions


            except KeyError as k:
                print(f'\nError: no field {k} found at saved data!')

            except Exception as e:
                print(f"\nError: {e}")

            finally:
                try:
                    dst_broker_connection.logout()

                except Exception as e:
                    print(f"\nError: {e}")

    def __load_plan_data(self, plan):

        plan_ending = '.plandata'
        os.makedirs(os.path.dirname(self.packs_path), exist_ok=True)
        plan_full_name = os.path.join(self.packs_path, plan + plan_ending)
        print(f'\nTrying to read saved data from "{plan_full_name}" config file\n')
        plan_data_list = []

        with open(plan_full_name, 'rb') as f:
            plan_data_list = pickle.load(f)

        return plan_data_list

    def run(self, plan_name):

        try:
            plan_data_list = self.__load_plan_data(plan=plan_name)
            print(plan_data_list)

            if (plan_data_list):
                self.__send_data(plan_data_list_param=plan_data_list)
                self.__result = True
            else:
                print('\nError: read data is empty... Skipping!')

        except Exception as e:
            print(f"\nError: {e}")

        finally:
            return self.__result
