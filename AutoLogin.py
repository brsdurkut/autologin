import requests
from ConfigParser import ConfigParser


class AutoLogin(object):
    _config_file = None
    _check_url = None
    _config = None
    _args = None

    def __init__(self, config_file='config.ini'):
        self._config_file = config_file
        self._session = requests.Session()  # To logout in future

    def run(self):
        if self._parse_configfile() and \
                self._prepare_args():
            attempt = [0, 3]
            while attempt[0] < attempt[1] and \
                    self._login() is False:
                print('[{0}] Attempt is failed. Trying again..'.format(
                    attempt[0]))
                attempt[0] += 1
            else:
                if(attempt[0] == attempt[1]):
                    print('ERROR: Login fail')
                    return False
                if(self._check_connection()):
                    print('Login success')
                    return True
                return False

    def _parse_configfile(self):
        config = ConfigParser()
        configs = {}

        config.read(self._config_file)
        if(len(config._sections) > 0):
            configs_raw = config._sections
            for i in configs_raw:
                label = ''
                for j in configs_raw[i]:
                    if(j is '__name__'):
                        label = i
                        configs[i] = {}
                    else:
                        configs[label][j] = configs_raw[i][j]
            self._config = configs
            return True
        else:
            print('ERROR: Config file is empty or not exist')
            return False

    def _prepare_args(self):
        if(self._config is not None):
            params = {'url', 'data', 'check'}
            params = {'url': '{0}{1}'.format(
                self._config['url']['url'],
                self._config['url']['extra'])}

            params['data'] = {
                self._config['params']['username']:
                self._config['content']['username']}

            params['data'][self._config['params']['password']] = \
                self._config['content']['password']

            params['data'][self._config['params']['submit']] = \
                self._config['content']['submit']

            params['check'] = self._config['url']['check']

            self._args = params
            return True
        else:
            print('Config params are not ready')
            return False

    def _login(self):
        self._req_post = requests.Request(
            'POST', url=self._args['url'], data=self._args['data'])
        response = self._session.send(
            self._session.prepare_request(self._req_post))

        if(response.status_code is not requests.codes.ok):
            print('ERROR: response-code: {0}'.format(response.status_code))
            return False
        print('Response-Code: {0}'.format(response.status_code))
        return True

    def _check_connection(self):
        self._check_url = self._args['check']
        self._req_get = requests.Request('GET', url=self._check_url)
        response = self._session.send(
            self._session.prepare_request(self._req_get))
        if(response.content.find('Success') >= 0):
            return True
        return False
