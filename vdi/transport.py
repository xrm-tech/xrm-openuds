import sys
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient

DIRECT_RDP_TYPE = "RDPTransport"
TUNNELED_RDP_TYPE = "TSRDPTransport"
class Transport:

    perm_class= 'transports'

    data: list = []
    ids_list: list = []
    __secondary_broker_connection: apiclient.Client

    def __init__ (self, primary_broker, pool_transports_list):      

        ids_list = []
        for elem in pool_transports_list:
            ids_list.append(elem['id'])
    
        self.ids_list = ids_list.copy()

        data = []
        for id in self.ids_list:
            data.append(
                primary_broker.get_transport(id)
            )
        self.data= data.copy()

    def __get_params_by_type(self, trans):
        not_none_transport_params = None
        if trans.get('type') == DIRECT_RDP_TYPE:

            params = {
                'name': trans.get('name'),
                'type': trans.get('type'),
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

        if trans.get('type') == TUNNELED_RDP_TYPE:
            params = {
                'name': trans.get('name'),
                'type': trans.get('type'),
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

                'tunnelServer': trans.get('tunnelServer'),
                'tunnelWait': trans.get('tunnelWait'),
                'verifyCertificate': trans.get('verifyCertificate'),
            }
            not_none_transport_params = {k: str(v) for k, v in params.items() if v is not None}

        return not_none_transport_params

    def __create_transport_by_type(self, transport_type, params):
        print(f"  Trying to create with params: {params}")
        supported = False
        result = None

        if transport_type == DIRECT_RDP_TYPE:
            supported = True
            result = self.__secondary_broker_connection.create_rdpdirect_transport(**params)

        if transport_type == TUNNELED_RDP_TYPE:
            supported = True
            result = self.__secondary_broker_connection.create_rdptunnel_transport(**params)

        if supported:
            if type(result) is dict:
                return result.get('id')
            else:
                print(f"  Error: {str(result)}...skipping")
                return None

        else:
            print(f"  Cannot create unsupported type: \"{transport_type}\"... Skipping...")
            return None

    def __get_id_if_exist(self, name, t_type):
        existing_id = None

        transports_list = self.__secondary_broker_connection.list_transports()
        for trans in transports_list:

            if trans.get('name') == name and trans.get('type') == t_type:
                existing_id = trans.get('id')
                break

        return existing_id


    def restore(self):
        '''
        Создание транспортов
        '''
        print("\nCreating transports")
        created_transport_ids = {}

        for trans in self.data:
            print(f"  Creating \"{trans.get('name')}\" transport")
            params = self.__get_params_by_type(trans)

            if params is not None:
                created_transport_id = self.__get_id_if_exist(name=trans.get('name'), t_type=trans.get('type'))

                if created_transport_id is None:
                    print("  Not found existing transport, need to create new one")
                    created_transport_id = self.__create_transport_by_type(
                        transport_type=trans.get('type'),
                        params=params
                    )

                    if created_transport_id is not None:
                        print(f"  Successfully created, old id: {trans.get('id')} new id: {created_transport_id}")
                        created_transport_ids[trans.get('id')] = created_transport_id

                    else:
                        print(f"  Error when creating transport, \"created_transport_id\" is None")

                else:
                    print(f"  Transport is already exist, old id: \"{trans.get('id')}, new id: {created_transport_id}\" no need to create")
                    created_transport_ids[trans.get('id')] = created_transport_id

            else:
                print(f"  Skipping transport because of unsupported type \"{trans.get('type')}\"")

        print(f"\n  Result of all created service pool transports old to new ids: {created_transport_ids}")
        return created_transport_ids

    def set_connection(self, secondary_broker_connection):
        self.__secondary_broker_connection = secondary_broker_connection

    def get_logs(self):
        
        print('Transport [ id ]: ', self.data, '\n')
        print('Transport [ data ]: ', self.data, '\n')

    