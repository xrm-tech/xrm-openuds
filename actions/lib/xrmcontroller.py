from st2common.runners.base_action import Action
import requests


class XRMBaseAction(Action):
    def __init__(self, config):
        super(XRMBaseAction, self).__init__(config=config)
        #self.user = config['username']
        #self.password = config['password']
        #self.url = config['host']
        self.session = requests.session()

    def login(self):
        pass
        '''self.session.get(self.url)
        data = {"z_csrf_protection": "off",
                "z_username": self.user,
                "z_password": self.password}
        login = self.session.post("{}/z_security_check".format(self.url), data=data)

        if login.status_code != 200:
            raise Exception("Could not login to mmonit {}.".format(login.reason))
'''
    def logout(self):
        #self.session.get("{}/login/logout.csp".format(self.url))
        self.session.close()