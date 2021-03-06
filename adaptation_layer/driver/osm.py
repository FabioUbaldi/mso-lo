#  Copyright 2019 CNIT, Francesco Lombardo, Matteo Pergolesi
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import copy
import os
import re
from datetime import datetime
from functools import wraps
from typing import Dict, Tuple, List
from urllib.parse import urlencode

import requests
import urllib3
import yaml as YAML
from urllib3.exceptions import InsecureRequestWarning

from error_handler import ResourceNotFound, NsNotFound, VnfNotFound, \
    Unauthorized, BadRequest, ServerError, NsOpNotFound, VnfPkgNotFound, \
    VimNotFound, NsdNotFound
from .interface import Driver, Headers, BodyList, Body

urllib3.disable_warnings(InsecureRequestWarning)
TESTING = os.getenv('TESTING', 'false').lower()
PRISM_ALIAS = os.getenv("PRISM_ALIAS", "prism-osm")


def _authenticate(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if TESTING == 'true':
            pass
        elif not self._token or datetime.utcfromtimestamp(
                self._token["expires"]) < datetime.utcnow():
            auth_payload = {'username': self._user,
                            'password': self._password,
                            'project_id': self._project}
            token_url = "{0}/{1}".format(self._base_path,
                                         self._token_endpoint)
            self._token, headers = self._exec_post(token_url,
                                                   json=auth_payload)
            self._headers["Authorization"] = 'Bearer {}'.format(
                self._token['id'])
        return func(self, *args, **kwargs)

    return wrapper


class OSM(Driver):

    def __init__(self, nfvo_cred):
        self._nfvoId = nfvo_cred["nfvo_id"]
        self._token_endpoint = 'admin/v1/tokens'
        self._user_endpoint = 'admin/v1/users'
        self._host = nfvo_cred["host"]
        self._so_port = nfvo_cred["port"] if "port" in nfvo_cred else 9999
        self._user = nfvo_cred["user"]
        self._password = nfvo_cred["password"]
        self._project = nfvo_cred["project"]
        self._headers = {"Content-Type": "application/json",
                         "Accept": "application/json"}
        self._token = None
        if TESTING == 'true':
            self._base_path = 'http://{0}:{1}/osm'.format(PRISM_ALIAS,
                                                          self._so_port)
        else:
            self._base_path = 'https://{0}:{1}/osm'.format(self._host,
                                                           self._so_port)

    def _exec_get(self, url=None, params=None, headers=None):
        try:
            resp = requests.get(url, params=params,
                                verify=False, stream=True, headers=headers)
        except Exception as e:
            raise ServerError(str(e))
        if resp.status_code in (200, 201, 202):
            if 'application/json' in resp.headers['content-type']:
                return resp.json(), resp.headers
            elif 'application/yaml' in resp.headers['content-type']:
                return YAML.load(resp.text, Loader=YAML.SafeLoader), \
                    resp.headers
            else:
                return resp.text, resp.headers
        elif resp.status_code == 204:
            return None, resp.headers
        elif resp.status_code == 400:
            raise BadRequest()
        elif resp.status_code == 401:
            raise Unauthorized()
        elif resp.status_code == 404:
            raise ResourceNotFound()
        else:
            if 'application/json' in resp.headers['content-type']:
                error = resp.json()
            elif 'application/yaml' in resp.headers['content-type']:
                error = YAML.load(resp.text, Loader=YAML.SafeLoader)
            else:
                error = resp.text
            raise ServerError(error)

    def _exec_post(self, url=None, data=None, json=None, headers=None):
        try:
            resp = requests.post(url, data=data, json=json,
                                 verify=False, headers=headers)
        except Exception as e:
            raise ServerError(str(e))
        if resp.status_code in (200, 201, 202):
            if 'application/json' in resp.headers['content-type']:
                return resp.json(), resp.headers
            elif 'application/yaml' in resp.headers['content-type']:
                return YAML.load(resp.text, Loader=YAML.SafeLoader), \
                    resp.headers
            else:
                return resp.text, resp.headers
        elif resp.status_code == 204:
            return None, resp.headers
        elif resp.status_code == 400:
            raise BadRequest()
        elif resp.status_code == 401:
            raise Unauthorized()
        elif resp.status_code == 404:
            raise ResourceNotFound()
        else:
            if 'application/json' in resp.headers['content-type']:
                error = resp.json()
            elif 'application/yaml' in resp.headers['content-type']:
                error = YAML.load(resp.text, Loader=YAML.SafeLoader)
            else:
                error = resp.text
            raise ServerError(error)

    def _exec_delete(self, url=None, params=None, headers=None):
        try:
            resp = requests.delete(
                url, params=params, verify=False, headers=headers)
        except Exception as e:
            raise ServerError(str(e))
        if resp.status_code in (200, 201, 202):
            if 'application/json' in resp.headers['content-type']:
                return resp.json(), resp.headers
            elif 'application/yaml' in resp.headers['content-type']:
                return YAML.load(resp.text, Loader=YAML.SafeLoader), \
                    resp.headers
            else:
                return resp.text, resp.headers
        elif resp.status_code == 204:
            return None, resp.headers
        elif resp.status_code == 400:
            raise BadRequest()
        elif resp.status_code == 401:
            raise Unauthorized()
        elif resp.status_code == 404:
            raise ResourceNotFound()
        else:
            if 'application/json' in resp.headers['content-type']:
                error = resp.json()
            elif 'application/yaml' in resp.headers['content-type']:
                error = YAML.load(resp.text, Loader=YAML.SafeLoader)
            else:
                error = resp.text
            raise ServerError(error)

    @_authenticate
    def _get_vnf_list(self, args=None):
        _url = "{0}/nslcm/v1/vnf_instances".format(self._base_path)
        _url = self._build_url_query(_url, args)
        return self._exec_get(_url, headers=self._headers)

    @_authenticate
    def _get_vnf(self, vnfId: str, args=None):
        _url = "{0}/nslcm/v1/vnf_instances/{1}".format(self._base_path, vnfId)
        _url = self._build_url_query(_url, args)
        try:
            return self._exec_get(_url, headers=self._headers)
        except ResourceNotFound:
            raise VnfNotFound(vnf_id=vnfId)

    @_authenticate
    def get_vim_list(self):
        _url = "{0}/admin/v1/vims".format(self._base_path)
        _url = self._build_url_query(_url, None)
        return self._exec_get(_url, headers=self._headers)

    @_authenticate
    def _get_vnfpkg(self, vnfPkgId, args=None):
        _url = "{0}/vnfpkgm/v1/vnf_packages/{1}".format(
            self._base_path, vnfPkgId)
        _url = self._build_url_query(_url, args)
        try:
            return self._exec_get(_url, headers=self._headers)
        except ResourceNotFound:
            raise VnfPkgNotFound(vnfpkg_id=vnfPkgId)

    @_authenticate
    def _get_nsdpkg(self, args=None):
        _url = "{0}/nsd/v1/ns_descriptors".format(self._base_path)
        _url = self._build_url_query(_url, args)
        nsdpkg_list, headers = self._exec_get(_url, headers=self._headers)
        if not nsdpkg_list:
            raise NsdNotFound(nsd_id=args["args"]["id"])
        elif len(nsdpkg_list) > 1:
            raise ServerError(
                description="Multiple NSD with id={} found in OSM".format(
                    args["args"]["id"]))
        return nsdpkg_list[0], headers

    @_authenticate
    def get_ns_list(self, args=None) -> Tuple[BodyList, Headers]:
        _url = "{0}/nslcm/v1/ns_instances".format(self._base_path)
        _url = self._build_url_query(_url, args)
        osm_ns_list, osm_headers = self._exec_get(_url, headers=self._headers)
        sol_ns_list = []
        for osm_ns in osm_ns_list:
            sol_ns_list.append(self._ns_im_converter(osm_ns))
        headers = self._build_headers(osm_headers)
        return sol_ns_list, headers

    @_authenticate
    def create_ns(self, args=None) -> Tuple[Body, Headers]:
        _url = "{0}/nslcm/v1/ns_instances".format(self._base_path)
        _url = self._build_url_query(_url, args)
        osm_nsdpkg, headers_nsdpkg = self._get_nsdpkg(args={"args": {
            "id": args["payload"]["nsdId"]}
        })
        args["payload"]["nsdId"] = osm_nsdpkg["_id"]
        args['payload']['vimAccountId'] = self._select_vim()
        osm_ns, osm_headers = self._exec_post(
            _url, json=args['payload'], headers=self._headers)
        # Get location header from OSM
        headers = self._build_headers(osm_headers)
        # Get NS info from OSM
        sol_ns, headerz = self.get_ns(osm_ns["id"])
        return sol_ns, headers

    @_authenticate
    def get_ns(self, nsId: str, args=None, skip_sol=False) \
            -> Tuple[Body, Headers]:
        _url = "{0}/nslcm/v1/ns_instances/{1}".format(self._base_path, nsId)
        _url = self._build_url_query(_url, args)
        try:
            osm_ns, osm_headers = self._exec_get(_url, headers=self._headers)
        except ResourceNotFound:
            raise NsNotFound(ns_id=nsId)
        headers = self._build_headers(osm_headers)
        if skip_sol:
            return osm_ns, headers
        sol_ns = self._ns_im_converter(osm_ns)
        return sol_ns, headers

    @_authenticate
    def delete_ns(self, nsId: str, args: Dict = None) -> Tuple[None, Headers]:
        _url = "{0}/nslcm/v1/ns_instances/{1}".format(self._base_path, nsId)
        _url = self._build_url_query(_url, args)
        req_headers = copy.deepcopy(self._headers)
        del req_headers["Content-Type"]
        del req_headers["Accept"]
        try:
            empty_body, osm_headers = self._exec_delete(
                _url, params=None, headers=req_headers)
        except ResourceNotFound:
            raise NsNotFound(ns_id=nsId)
        headers = self._build_headers(osm_headers)
        return None, headers

    @_authenticate
    def instantiate_ns(self, nsId: str, args=None) -> Tuple[None, Headers]:
        _url = "{0}/nslcm/v1/ns_instances/{1}/instantiate".format(
            self._base_path, nsId)
        _url = self._build_url_query(_url, args)
        instantiate_payload = {}
        ns_res, ns_head = self.get_ns(nsId, skip_sol=True)
        instantiate_payload.update(ns_res['instantiate_params'])
        args_payload = args['payload']

        if args_payload and 'additionalParamsForNs' in args_payload:
            instantiate_payload.update(args_payload['additionalParamsForNs'])
            if 'vnf' in instantiate_payload:
                mapping = {v: str(i+1) for i,
                           v in enumerate(ns_res['constituent-vnfr-ref'])}
                for vnf in instantiate_payload['vnf']:
                    if vnf.get('vnfInstanceId'):
                        vnf['member-vnf-index'] = mapping[vnf.pop(
                            'vnfInstanceId')]
            if 'wim_account' not in instantiate_payload:
                instantiate_payload['wimAccountId'] = False

        try:
            empty_body, osm_headers = self._exec_post(
                _url, json=instantiate_payload, headers=self._headers)
        except ResourceNotFound as e:
            print(e)
            raise NsNotFound(ns_id=nsId)

        headers = self._build_headers(osm_headers)
        return None, headers

    @_authenticate
    def terminate_ns(self, nsId: str, args=None) -> Tuple[None, Headers]:
        _url = "{0}/nslcm/v1/ns_instances/{1}/terminate".format(
            self._base_path, nsId)
        _url = self._build_url_query(_url, args)
        try:
            emtpy_body, osm_headers = self._exec_post(
                _url, json=args['payload'], headers=self._headers)
        except ResourceNotFound:
            raise NsNotFound(ns_id=nsId)
        headers = self._build_headers(osm_headers)
        return None, headers

    @_authenticate
    def scale_ns(self, nsId: str, args=None) -> Tuple[None, Headers]:
        _url = "{0}/nslcm/v1/ns_instances/{1}/scale".format(
            self._base_path, nsId)
        _url = self._build_url_query(_url, args)
        try:
            empty_body, osm_headers = self._exec_post(
                _url, json=args['payload'], headers=self._headers)
        except ResourceNotFound:
            raise NsNotFound(ns_id=id)
        headers = self._build_headers(osm_headers)
        return None, headers

    @_authenticate
    def get_op_list(self, args: Dict = None) -> Tuple[BodyList, Headers]:
        _url = "{0}/nslcm/v1/ns_lcm_op_occs".format(self._base_path)
        _url = self._build_url_query(_url, args)
        osm_op_list, osm_headers = self._exec_get(_url, headers=self._headers)
        sol_op_list = []
        for op in osm_op_list:
            sol_op_list.append(self._op_im_converter(op))
        headers = self._build_headers(osm_headers)
        return sol_op_list, headers

    @_authenticate
    def get_op(self, nsLcmOpId, args: Dict = None) -> Tuple[Body, Headers]:
        _url = "{0}/nslcm/v1/ns_lcm_op_occs/{1}".format(
            self._base_path, nsLcmOpId)
        _url = self._build_url_query(_url, args)
        try:
            osm_op, osm_headers = self._exec_get(_url, headers=self._headers)
        except ResourceNotFound:
            raise NsOpNotFound(ns_op_id=nsLcmOpId)
        sol_op = self._op_im_converter(osm_op)
        headers = self._build_headers(osm_headers)
        return sol_op, headers

    def _cpinfo_converter(self, osm_vnf: Dict) -> List[Dict]:
        cp_info = []
        try:
            vnfpkg, headers = self._get_vnfpkg(osm_vnf["vnfd-id"])
        except VnfPkgNotFound:
            return cp_info
        for vdur in osm_vnf["vdur"]:
            for if_vdur in vdur["interfaces"]:
                [if_pkg] = [if_pkg for vdu in vnfpkg["vdu"]
                            for if_pkg in vdu["interface"]
                            if vdu["id"] == vdur["vdu-id-ref"]
                            and if_pkg["name"] == if_vdur["name"]]
                [cp] = [val for key, val in if_pkg.items(
                ) if key.endswith("-connection-point-ref")]
                try:
                    (ip_address, mac_address) = (
                        if_vdur["ip-address"], if_vdur["mac-address"])
                except KeyError:
                    (ip_address, mac_address) = (None, None)
                cp_info.append({
                    "id": cp,
                    "cpdId": cp,
                    "cpProtocolInfo": [
                        {
                            "layerProtocol": "IP_OVER_ETHERNET",
                            "ipOverEthernet": {
                                "macAddress": mac_address,
                                "ipAddresses": [
                                    {
                                        "type": "IPV4",
                                        "addresses": [ip_address]
                                    }
                                ]
                            }
                        }
                    ]
                })
        return cp_info

    def _select_vim(self):
        osm_vims, osm_vim_h = self.get_vim_list()
        if osm_vims and len(osm_vims) > 0:
            return osm_vims[0]['_id']
        else:
            raise VimNotFound()

    def _ns_im_converter(self, osm_ns: Dict) -> Dict:
        sol_ns = {
            "id": osm_ns['id'],
            "nsInstanceName": osm_ns['name'],
            "nsInstanceDescription": osm_ns['description'],
            "nsdId": osm_ns['nsd-ref'],
            "nsState": osm_ns['_admin']['nsState'],
            "vnfInstance": []
        }

        osm_vnfs = []
        if 'constituent-vnfr-ref' in osm_ns:
            for vnf_id in osm_ns["constituent-vnfr-ref"]:
                try:
                    vnf, headers = self._get_vnf(vnf_id)
                    osm_vnfs.append(vnf)
                except VnfNotFound:
                    pass

        for osm_vnf in osm_vnfs:
            vnf_instance = {
                "id": osm_vnf["id"],
                "vnfdId": osm_vnf["vnfd-ref"],
                "vnfProductName": "",
                "vimId": osm_vnf["vim-account-id"] if osm_vnf["vim-account-id"]
                else '',
                # same as the NS
                "instantiationState": osm_ns['_admin']['nsState'],
            }
            if vnf_instance["instantiationState"] == "INSTANTIATED":
                vnf_instance["instantiatedVnfInfo"] = {
                    "vnfState": "STARTED",
                    "extCpInfo": self._cpinfo_converter(osm_vnf)
                }
            sol_ns["vnfInstance"].append(vnf_instance)
        return sol_ns

    @staticmethod
    def _op_im_converter(osm_op):
        sol_op = {
            "id": osm_op["id"],
            "operationState": osm_op["operationState"].upper(),
            "stateEnteredTime": datetime.utcfromtimestamp(
                osm_op["statusEnteredTime"]).isoformat("T") + "Z",
            "nsInstanceId": osm_op["nsInstanceId"],
            "lcmOperationType": osm_op["lcmOperationType"].upper(),
            "startTime": datetime.utcfromtimestamp(
                osm_op["startTime"]).isoformat("T") + "Z",
        }
        return sol_op

    @staticmethod
    def _build_url_query(base, args):
        if args and args['args']:
            url_query = urlencode(args['args'])
            return "{0}?{1}".format(base, url_query)
        return base

    def _build_headers(self, osm_headers):
        headers = {}
        if 'location' in osm_headers:
            re_res = re.findall(
                r"/osm/nslcm/v1/(ns_instances|ns_lcm_op_occs)/([A-Za-z0-9\-]+)",
                osm_headers['location'])
            if len(re_res):
                if re_res[0][0] == 'ns_instances':
                    headers['location'] = '/nfvo/{0}/ns_instances/{1}'.format(
                        self._nfvoId, re_res[0][1])
                elif re_res[0][0] == 'ns_lcm_op_occs':
                    headers['location'] = '/nfvo/{0}/ns_lcm_op_occs/{1}'.format(
                        self._nfvoId, re_res[0][1])
        return headers
