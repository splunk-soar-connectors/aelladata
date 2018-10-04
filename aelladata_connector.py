# --
# File: aelladata/aelladata_connector.py
#
# Copyright (c) Aella Data Inc, 2018
#
# This unpublished material is proprietary to Aella Data.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Aella Data.
#
# --
""" Code that implements calls made to the aelladata systems device"""

# Phantom imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# THIS Connector imports
from aelladata_consts import *

import requests
import json
# import imp
import sys

import aelladata_parser

# import pdb

MODULE_NAME = 'custom_parser'
HANDLER_NAME = 'handle_request'


class PhantomDebugWriter():
    def __init__(self, this):
        self.this = this

    def write(self, message):
        self.this.debug_print(message)


class StarlightConnector(BaseConnector):

    # actions supported by this script
    ACTION_ID_RUN_QUERY = "run_query"
    ACTION_ID_GET_CONFIG = "get_config"
    REQUIRED_INGESTION_FIELDS = ["ingest_index",
                                 "ingest_type",
                                 "ingest_query"]

    def __init__(self):
        """ """

        self._key = None
        self._host = None
        self._verify = None
        self._headers = None
        self._base_url = None
        self._username = None
        self._auth_method = None

        # Call the BaseConnectors init first
        super(StarlightConnector, self).__init__()

    def initialize(self):
        """ Called once for every action, all member initializations occur here"""

        config = self.get_config()

        # Get the Base URL from the asset config and so some cleanup
        self._base_url = config[AELLADATA_JSON_DEVICE_URL]
        if (self._base_url.endswith('/')):
            self._base_url = self._base_url[:-1]

        # The host member extacts the host from the URL, is used in creating status messages
        self._host = self._base_url[self._base_url.find('//') + 2:]

        # The headers, initialize them here once and use them for all other REST calls
        self._headers = {'Accept': 'application/json'}

        self._username = config.get(phantom.APP_JSON_USERNAME)
        self._password = config.get(phantom.APP_JSON_PASSWORD)

        if (self._username and self._password):
            self._auth_method = True

        self._verify = config['verify_server_cert']

        return phantom.APP_SUCCESS

    def _make_rest_call(self, endpoint, action_result, headers={}, params=None, data=None, method="get"):
        """ Function that makes the REST call to the device, generic function that can be called from various action handlers"""

        # Get the config
        # config = self.get_config()

        # Create the headers
        headers.update(self._headers)

        if (method in ['get', 'put', 'post']):
            headers.update({'Content-Type': 'application/json'})

        resp_json = None

        # get or post or put, whatever the caller asked us to use, if not specified the default will be 'get'
        request_func = getattr(requests, method)

        # handle the error in case the caller specified a non-existant method
        if (not request_func):
            return action_result.set_status(phantom.APP_ERROR, AELLADATA_ERR_API_UNSUPPORTED_METHOD, method=method)

        if (self._auth_method):
            self.save_progress('Using authentication')
        else:
            self.save_progress('Not using any authentication, since either the password or username not specified')

        # Make the call
        try:
            r = request_func(self._base_url + endpoint,  # The complete url is made up of the base_url, and the endpoint
                    auth=(self._username, self._password) if self._auth_method else None,
                    data=json.dumps(data) if data else None,  # the data, converted to json string format if present, else just set to None
                    headers=headers,  # The headers to send in the HTTP call
                    # verify=config[phantom.APP_JSON_VERIFY],  # should cert verification be carried out?
                    verify=self._verify,  # should cert verification be carried out?
                    params=params)  # uri parameters if any
        except Exception as e:
            return (action_result.set_status(phantom.APP_ERROR, AELLADATA_ERR_SERVER_CONNECTION, e), resp_json)

        if hasattr(action_result, 'add_debug_data'):
            if (r is not None):
                action_result.add_debug_data({'r_text': r.text})
                action_result.add_debug_data({'r_headers': r.headers})
                action_result.add_debug_data({'r_status_code': r.status_code})
            else:
                action_result.add_debug_data({'r_text': 'r is None'})

        # Try a json parse, since most REST API's give back the data in json, if the device does not return JSONs, then need to implement parsing them some other manner
        try:
            resp_json = r.json()
        except Exception as e:
            # r.text is guaranteed to be NON None, it will be empty, but not None
            msg_string = AELLADATA_ERR_JSON_PARSE.format(raw_text=r.text.replace('{', ' ').replace('}', ' '))
            return (action_result.set_status(phantom.APP_ERROR, msg_string, e), resp_json)

        # Handle any special HTTP error codes here, many devices return an HTTP error code like 204. The requests module treats these as error,
        # so handle them here before anything else, uncomment the following lines in such cases
        # if (r.status_code == 201):
        #     return (phantom.APP_SUCCESS, resp_json)

        # Handle/process any errors that we get back from the device
        if (200 <= r.status_code <= 399):
            # Success
            return (phantom.APP_SUCCESS, resp_json)

        # Failure
        action_result.add_data(resp_json)

        details = json.dumps(resp_json).replace('{', '').replace('}', '')

        return (action_result.set_status(phantom.APP_ERROR, AELLADATA_ERR_FROM_SERVER.format(status=r.status_code, detail=details)), resp_json)

    def _test_connectivity(self, param):
        """ Function that handles the test connectivity action, it is much simpler than other action handlers."""

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # set the endpoint
        endpoint = '/_cluster/health'

        # Action result to represent the call
        action_result = ActionResult()

        # Progress message, since it is test connectivity, it pays to be verbose
        self.save_progress(AELLADATA_MSG_CLUSTER_HEALTH)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result)

        # Process errors
        if (phantom.is_fail(ret_val)):

            # Dump error messages in the log
            self.debug_print(action_result.get_message())

            # Set the status of the complete connector result
            self.set_status(phantom.APP_ERROR, action_result.get_message())

            # Append the message to display
            self.append_to_message(AELLADATA_ERR_CONNECTIVITY_TEST)

            # return error
            return phantom.APP_ERROR

        # Set the status of the connector result
        return self.set_status_save_progress(phantom.APP_SUCCESS, AELLADATA_SUCC_CONNECTIVITY_TEST)

    def _run_query(self, param):
        """ Action handler for the 'run query' action"""

        # This is an action that needs to be represented by the ActionResult object
        # So create one and add it to 'self' (i.e. add it to the BaseConnector)
        # When the action_result is created this way, the parameter is also passed.
        # Other things like the summary, data and status is set later on.
        action_result = self.add_action_result(ActionResult(dict(param)))

        query_string = param.get(AELLADATA_JSON_QUERY, None)
        event_id = param.get("event_id", None)

        if not query_string and not event_id:
            return action_result.set_status(phantom.APP_ERROR, "Missing query string or event id")

        if event_id:
            query_json = { "query": { "match": { "_id": event_id } } }
            query_string = json.dumps(query_json)
            endpoint = "/{0}/{1}/_search".format("aella-ser*", "amsg")
        else:
            # validate the query that we got
            query_string = param[AELLADATA_JSON_QUERY]
            endpoint = "/{0}/{1}/_search".format(param[AELLADATA_JSON_INDEX], param[AELLADATA_JSON_TYPE])

        try:
            query_json = json.loads(query_string)
        except Exception as e:
            return action_result.set_status(phantom.APP_ERROR, "Unable to load query json. Error: {0}".format(str(e)))

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call(endpoint, action_result, data=query_json)

        # Process errors
        if (phantom.is_fail(ret_val)):

            # Dump error messages in the log
            self.debug_print(action_result.get_message())
            return action_result.get_status()

        action_result.update_summary({
            AELLADATA_JSON_TOTAL_HITS: response.get('hits', {}).get('total', 0),
            AELLADATA_JSON_TIMED_OUT: response.get('timed_out', False)})

        if event_id:
            timed_out = response.get("timed_out", False)
            hits = response.get("hits", {}).get("hits", [])
            for item in hits:
                index = item.get("_index", "")
                source = item.get("_source", {})
                if index:
                    source["_index"] = index
                source["timed_out"] = timed_out
                action_result.add_data(source)
        else:
            action_result.add_data(response)

        # Set the Status
        return action_result.set_status(phantom.APP_SUCCESS)

    def _get_config(self, param):

        action_result = self.add_action_result(ActionResult(dict(param)))

        # Connectivity
        self.save_progress(phantom.APP_PROG_CONNECTING_TO_ELLIPSES, self._host)

        # Make the rest endpoint call
        ret_val, response = self._make_rest_call('/_mapping', action_result)

        # Process errors
        if (phantom.is_fail(ret_val)):

            # Dump error messages in the log
            self.debug_print(action_result.get_message())
            return action_result.get_status()

        indices = response.keys()

        for index in indices:

            types = response[index]['mappings'].keys()

            data = {'index': index, 'types': types}

            action_result.add_data(data)

        action_result.update_summary({'total_indices': len(indices)})

        # Set the Status
        return action_result.set_status(phantom.APP_SUCCESS)

    def _save_container(self, container_dict):

        config = self.get_config()
        container = container_dict.get('container')
        container['label'] = config.get('ingest', {}).get('container_label')
        container['artifacts'] = container_dict.get('artifacts')

        return self.save_container(container)

    def _on_poll(self, param):
        container_count = param.get('container_count', 0)

        config = self.get_config()

        # Find out the polling interval
        ingest = config.get('ingest', None)
        if not ingest:
            return self.set_status(phantom.APP_ERROR, "Error getting ingest config")

        poll_interval = ingest.get('interval_mins', None)
        if not poll_interval:
            return self.set_status(phantom.APP_ERROR, "Error getting ingest config")

        event = config.get('event', '*')
        score = config.get('score', 50)

        index_str = "aella-ser*"
        query_str = "event_name:{}  AND severity:>{}".format(event, score)
        ts_str = "now-{}m".format(poll_interval)
        query_json = {"query": { "bool": { "must": [ { "query_string": { "query": query_str, "analyze_wildcard": True } }, { "range": { "timestamp": { "gt": ts_str } } } ] } } }
        query_str = json.dumps(query_json)

        query_params = {
            AELLADATA_JSON_TYPE: 'amsg',
            AELLADATA_JSON_INDEX: index_str,
            AELLADATA_JSON_QUERY: query_str
        }

        ret_val = self._run_query(query_params)
        if phantom.is_fail(ret_val):
            return ret_val

        action_results = self.get_action_results()
        for action_result in action_results:
            for data in action_result.get_data():
                ret_dict_list = None
                saved_stdout = sys.stdout
                debug_out = PhantomDebugWriter(self)
                sys.stdout = debug_out
                ret_dict_list = aelladata_parser.ingest_parser(data, self.debug_print)
                sys.stdout = saved_stdout
                if not ret_dict_list:
                    continue

                if (container_count and self.is_poll_now() and
                        container_count > len(ret_dict_list)):
                    ret_dict_list = ret_dict_list[:container_count]

                for ret_dict in ret_dict_list:
                    self._save_container(ret_dict)

        return self.set_status(phantom.APP_SUCCESS)

    def handle_action(self, param):
        """Function that handles all the actions"""

        # Get the action that we are supposed to carry out, set it in the connection result object
        action = self.get_action_identifier()

        # Intialize it to success
        ret_val = phantom.APP_SUCCESS

        # Bunch if if..elif to process actions
        if (action == self.ACTION_ID_RUN_QUERY):
            ret_val = self._run_query(param)
        elif (action == self.ACTION_ID_GET_CONFIG):
            ret_val = self._get_config(param)
        elif (action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY):
            ret_val = self._test_connectivity(param)
        elif action == phantom.ACTION_ID_INGEST_ON_POLL:
            ret_val = self._on_poll(param)

        return ret_val


if __name__ == '__main__':
    """ Code that is executed when run in standalone debug mode
    for .e.g:
    python2.7 ./aelladata_connector.py /tmp/aelladata_test_create_ticket.json
        """

    # Imports
    # import pudb

    # Breakpoint at runtime
    # pudb.set_trace()

    # The first param is the input json file
    with open(sys.argv[1]) as f:

        # Load the input json file
        in_json = f.read()
        in_json = json.loads(in_json)
        # print(json.dumps(in_json, indent=' ' * 4))

        # Create the connector class object
        connector = StarlightConnector()

        # Se the member vars
        connector.print_progress_message = True

        # Call BaseConnector::_handle_action(...) to kickoff action handling.
        ret_val = connector._handle_action(json.dumps(in_json), None)

        # Dump the return value
        print ret_val

    exit(0)
