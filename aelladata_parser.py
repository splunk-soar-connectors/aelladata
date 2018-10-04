# --
# File: aelladata_parser.py
#
# Copyright (c) Aella Data Inc, 2017-2018
#
# This unpublished material is proprietary to Aella Data.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Aella Data.
#
# --


def ingest_parser(data, log_func):
    results = []
    if not isinstance(data, dict):
        return results

    hits = data.get('hits', {}).get('hits', [])
    for hit in hits:
        container = {}
        artifacts = []

        # anything printed to stdout will be added to the phantom debug logs
        print "Found hit {}. Building container".format(hit['_id'])

        source = hit.get("_source", None)
        if not source:
            continue

        event_name = source.get("event_name", None)
        if not event_name:
            continue

        eid = hit['_id']
        container['run_automation'] = False
        sdi = "{}_{}".format(event_name, eid)
        container['source_data_identifier'] = eid
        container['name'] = sdi

        artifacts.append({
            # always True since there is only one
            'run_automation': True,
            'label': 'Starlight event',
            'name': event_name,
            'source_data_identifier': eid,
            'cef': {"eventId": eid},
            'cef_types': {"eventId": ["starlight event id"]}
        })

        results.append({
            'container': container,
            'artifacts': artifacts
        })

    return results
