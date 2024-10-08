import sys
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient

class Transport:

    perm_class= 'transports'
    
    data: list = []
    ids_list: list = []

    def __init__ (self, primary_broker, pool_transports_list):      

        ids_list=[]       
        for elem in pool_transports_list:
            ids_list.append(elem['id'])
    
        self.ids_list= ids_list.copy()

        data=[]
        for id in self.ids_list:
            data.append(
                primary_broker.get_transport(id)
            )
        self.data= data.copy()    

    def restore(self):
        '''
        Создание транспортов
        '''
        print(f'\nCreating transports')

        # TODO: добавить туннельный rdp, отдельный метод
        for trans in self.data:
            trans_name_str = trans.get('name')

            if trans.get('type') == 'RDPTransport':
                params = {
                    'name': trans.get('name'),
                    'type': trans.get('type'),
                    '''
                    pools - по листу соотвествия, а не по созданным
                    '''
                    'pools': [],
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

            # TODO: permissions
    def get_logs(self):
        
        print('Transport [ id ]: ', self.data , '\n')
        print('Transport [ data ]: ', self.data , '\n')

    