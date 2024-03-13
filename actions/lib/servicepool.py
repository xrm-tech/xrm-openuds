import base64
import os
import requests
import sys
import base64
import os
import requests
sys.path.append('/etc/apiclient')
import apiclient

class ServicePool():

    def __init__(self, broker_ip, broker_auth, broker_user, broker_pwd, pool_name):

        primary_broker= apiclient.Client(
            host= broker_ip,
            auth= broker_auth,
            username= broker_user,
            password= broker_pwd
        )

        try:

            primary_broker.login()
            print(primary_broker.get_config())

            pool_id= primary_broker.get_pool_id(pool_name)

            pool_data= primary_broker.get_pool(pool_id)

            pool_groups_list= primary_broker.list_pool_groups(pool_id)
            pool_transports_list= primary_broker.list_pool_transports(pool_id)
            pool_assigned_services_list= primary_broker.list_pool_assigned_services(pool_id)
            pool_assignables_list= primary_broker.list_pool_assignables(pool_id)

            provider_id= pool_data['provider_id']
            service_id= pool_data['service_id']
            auth_id= pool_groups_list

            provider_data= primary_broker.get_provider(provider_id)
            service_data= primary_broker.get_provider_service(provider_id, service_id)




        except ValueError as e:
            print('Invalid data: {}'.format(e))
        except Exception as e:
            raise Exception('Caught exception: {}'.format(e))

        finally:

            try:

                primary_broker.logout()

            except Exception as e:
                pass