import requests
from error_handler import ResourceNotFound, NsNotFound, VnfNotFound,\
    Unauthorized, BadRequest, ServerError
# from requests.packages.urllib3.exceptions import InsecureRequestWarning

# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class AgentClient(object):
    def __init__(self):
        self._host = '10.254.184.215'  # change IP , for tests only
        self._port = '8080'
        self._headers = {"Content-Type": "application/json",
                         "accept": "application/json"}
        self._base_path = 'http://{0}:{1}'.format(self._host, self._port)
        # self._test_path = 'http://jsonplaceholder.typicode.com/posts'  # for tests only
        # self._local_path = 'http://localIp:{0}'.format(self._port)  # add local IP

    def _exec_delete(self, url=None, params=None, headers=None):

        try:
            resp = requests.delete(url, params=params, headers=headers)
        except Exception as e:
            raise ServerError(str(e))

        if resp.status_code in (200, 201, 202, 204, 206):  # response code 206 was added / limit to needed
            print('response code: {}'.format(resp.status_code))  # for tests only
            return resp.json()
        elif resp.status_code == 400:
            print('response code: {}'.format(resp.status_code))  # for tests only
            raise BadRequest()
        elif resp.status_code == 401:
            print('response code: {}'.format(resp.status_code))  # for tests only
            raise Unauthorized()
        elif resp.status_code == 404:
            print('response code: {}'.format(resp.status_code))  # for tests only
            raise ResourceNotFound()
        else:
            error = resp.json()
            raise ServerError(error)

    def _exec_post(self, url=None, data=None, json=None, headers=None):

        try:
            resp = requests.post(url, data=data, json=json, headers=None)
        except Exception as e:
            raise ServerError(str(e))

        if resp.status_code in (200, 201, 202, 204, 206):
            print('response code: {}'.format(resp.status_code))  # for tests only
            return resp.json()
        elif resp.status_code == 400:
            print('response code: {}'.format(resp.status_code))  # for tests only
            raise BadRequest()
        elif resp.status_code == 401:
            print('response code: {}'.format(resp.status_code))  # for tests only
            raise Unauthorized()
        elif resp.status_code == 404:
            print('response code: {}'.format(resp.status_code))  # for tests only
            raise ResourceNotFound()
        else:
            error = resp.json()
            raise ServerError(error)

    def ns_create(self, ns_name, args=None):
        _url = '{0}/instantiate/{1}'.format(self._base_path, ns_name)
        return self._exec_post(_url, headers=self._headers)

    def ns_instantiate(self, id, ns_name, args=None):
        # _url = '{0}/instantiate/{1}'.format(self._base_path, ns_name)
        # add try except block to check if the service spec / service instance exists
        # return self._exec_post(_url, json=args, headers=self._headers)  # for dev change to json=args['payload']
        try:
            return
        except ResourceNotFound:
            raise NsNotFound(ns_id=id)

    def ns_delete(self, ns_id, args=None):
        _url = '{0}/service/{1}'.format(self._base_path, ns_id)
        return self._exec_delete(_url, headers=self._headers)

    def ns_terminate(self, ns_id, args=None):
        try:
            return
        except ResourceNotFound:
            raise NsNotFound(ns_id)

class Client(object):
    def __init__(self):

        # add a info about ONAP IP and port - current local instance
        self._host = '10.254.184.164'
        self._port = 30274
        self._nbi_ver = 4
        self._customer = 'Michal-Customer'  # when blank, default 'generic' ; IMPORTANT!
        self._headers = {"Content-Type": "application/json",
                         "accept": "application/json"}

        self._base_path = 'http://{0}:{1}//nbi/api/v{2}'.format(self._host, self._port, self._nbi_ver)

    def _exec_get(self, url=None, params=None, headers=None):

        try:
            resp = requests.get(url, params=params, headers=headers)
        except Exception as e:
            raise ServerError(str(e))

        if resp.status_code in (200, 201, 202, 204, 206):  # response code 206 was added
            print('response code: {}'.format(resp.status_code))  # for tests only
            return resp.json()
        elif resp.status_code == 400:
            print('response code: {}'.format(resp.status_code))  # for tests only
            raise BadRequest()
        elif resp.status_code == 401:
            print('response code: {}'.format(resp.status_code))  # for tests only
            raise Unauthorized()
        elif resp.status_code == 404:
            print('response code: {}'.format(resp.status_code))  # for tests only
            raise ResourceNotFound()
        else:
            error = resp.json()
            raise ServerError(error)  # (error) added
    #
    # def _exec_post(self, url=None, data=None, json=None, headers=None):
    #
    #     try:
    #         resp = requests.post(url, data=data, json=json, headers=None)
    #     except Exception as e:
    #         raise ServerError(str(e))
    #
    #     if resp.status_code in (200, 201, 202, 204, 206):
    #         return resp.json()
    #     elif resp.status_code == 400:
    #         print('response code: {}'.format(resp.status_code))  # for tests only
    #         raise BadRequest()
    #     elif resp.status_code == 401:
    #         print('response code: {}'.format(resp.status_code))  # for tests only
    #         raise Unauthorized()
    #     elif resp.status_code == 404:
    #         print('response code: {}'.format(resp.status_code))  # for tests only
    #         raise ResourceNotFound()
    #     else:
    #         error = resp.json()
    #         raise ServerError()

    def ns_list(self):
        _url = '{0}/service?relatedParty.id={1}'.format(self._base_path, self._customer)
        return self._exec_get(_url, params=None, headers=self._headers)

    def ns_get(self, ns_Id, args=None):
        _url = '{0}/service/{1}'.format(self._base_path, ns_Id)
        try:
            return self._exec_get(_url, headers=self._headers)
        except ResourceNotFound:
            raise NsNotFound(ns_id=ns_Id)
        # exception doesnt work when function is tested locally

    def check_ns_name(self, nsd_Id, args = None):
        _url = '{0}/serviceSpecification/{1}?fields=name'.format(self._base_path, nsd_Id)
        return self._exec_get(_url, headers=self._headers)



