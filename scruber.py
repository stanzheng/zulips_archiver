#!/usr/bin/env python3
import argparse
import json
from typing import Dict, List, Any

import zulip

usage = """\nGets the complete history of a particular stream or a particular topic in Zulip
and store them in JSON format.
    get-history --stream <stream_name> [--topic <topic_name> --filename <file_to_store_messages>]
Example: get-history --stream announce --topic important"""

parser = zulip.add_default_arguments(argparse.ArgumentParser(usage=usage))
parser.add_argument('--stream', help="The stream name to get the history", default = "" )
parser.add_argument('--topic', help="The topic name to get the history", default = "")
parser.add_argument('--filename', default='history.json', help="The file name to store the fetched  \
                    history.\n Default 'history.json'")
options = parser.parse_args()

client = zulip.init_from_options(options)

narrow = [{'operator': 'stream', 'operand': options.stream}]
if options.topic:
    narrow.append({'operator': 'topic', 'operand': options.topic})
narrow = [        {
        "operator": "sender",
        "operand": "MY_EMAIL",
        }] # foo
request = {
    # Initially we have the anchor as 0, so that it starts fetching
    # from the oldest message in the narrow
    'anchor': 0,
    'num_before': 0,
    'num_after': 1000,
    'narrow': narrow,
    'client_gravatar': False,
    'apply_markdown': False
}

all_messages = []  # type: List[Dict[str, Any]]
found_newest = False

while not found_newest:
    result = client.get_messages(request)
    try:
        found_newest = result["found_newest"]
        if result['messages']:
            # Setting the anchor to the next immediate message after the last fetched message.
            request['anchor'] = result['messages'][-1]['id'] + 1
            for i in result['messages']:
                # print(i)
                if i['content'] == '.':
                    continue 
                else: 
                   print(i['content'])
                x = client.update_message({"message_id": i['id'], "content": "."})
                while x['result'] == "error":
                    # retry 
                    x = client.update_message({"message_id": i['id'], "content": "."})
            # all_messages.extend(result["messages"])
    except Exception as e:
        # Might occur when the request is not returned with a success status
        print('Error occured: Payload was:')
        print(result)
        # quit()
        import time;  
        time.sleep(15)

# with open(options.filename, "w+") as f:
#     print('Writing %d messages...' % len(all_messages))
#     f.write(json.dumps(all_messages))
