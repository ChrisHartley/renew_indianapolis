from requests import Request, Session
try:
    from urllib.parse import quote
except ImportError:
    from six.moves.urllib.parse import quote 
import json




class ePPHelper(object):
    def __init__(self, sandbox=True, debug=False):
        try:
            if sandbox != True:
                from api_key import LIVE_API_KEY as API_KEY
                from api_key import LIVE_END_POINT as API_ENDPOINT
            else:
                from api_key import SANDBOX_API_KEY as API_KEY
                from api_key import SANDBOX_END_POINT as API_ENDPOINT
        except ImportError:
            API_KEY = ''
            API_ENDPOINT = ''

        headers = {
            'User-Agent': 'Mozilla/5.0 (ePPHelper Class)',
            'Content-Type': 'application/json',
            'x-strllc-authkey':  API_KEY,
            'Accept': 'application/json',
        }
        self.debug = debug
        self.site_url = 'https://indy.epropertyplus.com'
        self.endpoint = API_ENDPOINT
        s = Session()
        s.headers.update(headers)
        self.session = s

    def parse_results(self, r):
        if self.debug==True:
            import pprint
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint( 'Request Headers: {0}'.format(r.request.headers,))
            pp.pprint( 'Request Body: {0}'.format(r.request.body,))
            pp.pprint( 'Request URL: {0}'.format(r.url,))
            pp.pprint( 'Request Headers: {0}'.format(r.headers,))
            #pp.pprint( r.json())
            #pp.pprint( r.text)

        if r.status_code <= 399:
            try:
                return r.json()
            except ValueError:
                return r.content
        # For 400+ errors we make our own JSON response, especially with
        # 500 errors which return text.
        if r.status_code >= 400:
            if r.text == '':
                return {'success': False, 'server_response_code': r.status_code}
            return r.json()
        raise ValueError

    def get_reference_list(self, classification):
        api_resource = 'referenceData/list/'
        parameter = quote(classification)

        URL = '{0}{1}{2}'.format(self.endpoint, api_resource, parameter)
        return self.parse_results(self.session.get(URL))

    def get_property_summary(self, property_id):
        api_resource = 'property/getSummary?propertyId='
        URL = '{0}{1}{2}'.format(self.endpoint, api_resource, property_id)
        r = self.session.get(URL)
        return self.parse_results(r)

    def get_property(self, property_id):
        api_resource = 'property/get/'
        URL = '{0}{1}{2}'.format(self.endpoint, api_resource, property_id)
        r = self.session.get(URL)
        return self.parse_results(r)

    def get_image_list(self, property_id):
        api_resource = 'image/list/'
        URL = '{0}{1}?ownerId={2}&ownerType=PROPERTY'.format(self.endpoint, api_resource, property_id)
        r = self.session.get(URL)
        return self.parse_results(r)

    def get_image(self, image_id):
        api_resource = 'image/view/'
        URL = '{0}{1}/{2}'.format(self.endpoint, api_resource, image_id)
        r = self.session.get(URL)
        return self.parse_results(r)


    def get_property_search(self, json_query, sort=''):
        api_resource = 'property/summary'
        #json_query =  {"criterias":[{"name":"active","value":"Yes","operator":"EQUALS"}]}
        #json_query = '{"criterias":[{"name":"active","value":"Yes","operator":"EQUALS"},{"name":"published", "value":"Yes", "operator":"EQUALS"},{"name":"inventoryType", "value":"Land Bank", "operator":"EQUALS"}]}'
        parameters = {
            'page': 1,
            'limit': 5000,
            'json': json_query,
            'sort': '[{"property":"postalCode","direction":"ASC"},{"property":"propertyAddress1","direction":"ASC"}]'
        }
        URL = '{0}{1}'.format(self.endpoint, api_resource)
        r = self.session.post(URL, params=parameters)
        return self.parse_results(r)

    def get_published_properties(self):
        URL = 'https://public-indy.epropertyplus.com/landmgmtpub/remote/public/property/getPublishedProperties'
        parameters = {
            'page': 1,
            'limit': 5000,
            'json':  '{"criterias":[{"name":"published","operator":"EQUALS","value":"Yes"}]}',
            'sort': '[{"property":"postalCode","direction":"ASC"},{"property":"propertyAddress1","direction":"ASC"}]',
        }

        r = self.session.post(URL, params=parameters)
        return self.parse_results(r)
