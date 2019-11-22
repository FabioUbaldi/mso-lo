from typing import Dict, List
from client.onap import Client as ONAPclient
from client.onap import AgentClient as AGENTclient
# from .interface import Driver #sometimes it has to be in commend like  ONAP(Driver)

# Driver = 'onap'

# class ONAP(Driver):
class ONAP(object):

    def __init__(self):
        self._client = ONAPclient()
        self._agent = AGENTclient()
        # self._client = ONAPclient(**self)

    # def create_ns(self, args: Dict = None) -> Dict:
    #     pass

    def get_ns_list(self, args=None) -> List[Dict]:
        ns = self._client.ns_list()
        return self._ns_converter(ns)

    def get_ns(self, nsId: str, args=None) -> Dict:
        ns = self._client.ns_get(nsId, args=args)
        return self._ns_converter(ns)

    def delete_ns(self, nsId: str, args: Dict = None) -> None:
        return self._agent.ns_delete(nsId, args=args)

    def instantiate_ns(self, nsId: str, args: Dict = None) -> None:
        response = self._agent.ns_instantiate(nsId, args=args)
        return self.instantiate_converter(response)
    #
    # def scale_ns(self, nsId: str, args: Dict = None) -> None:
    #     pass
    #
    # def terminate_ns(self, nsId: str, args: Dict = None) -> None:
    #     pass

    def _ns_converter(self, ns):

        if type(ns) is dict:
            result = {
                "id": ns["id"],
                "nsInstanceName": ns['name'],
                "nsInstanceDescription": 'null',
                "nsdId": ns['serviceSpecification']['id'],
                "nsState": 'INSTANTIATED'
            }

        elif type(ns) is list:
            result = []
            for element in ns:
                result.append({
                    "id": element['id'],
                    "nsInstanceName": element['name'],
                    # In ONAP - no description id NS Instance
                    "nsInstanceDescription": 'null',
                    "nsdId": element['serviceSpecification']['id'],
                    # permitted value of nsState: NOT_INSTANTIATED, INSTANTIATED
                    # In ONAP all listed NS are instantiated
                    "nsState": 'INSTANTIATED'
                    })

        return result

    def instantiate_converter(self, response):
        return
