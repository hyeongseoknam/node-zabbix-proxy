import simplejson

def __sendActiveChecks(protocol):
    f = open('../langtest1/resp_active_checks.json')
    active_checks = f.read()
    f.close()
    #print '__sendActiveChecks', active_checks
    return active_checks

def __sendAgentData(protocol):
    items_count = len(protocol.getDoc()['data'])
    resp = {
        "response": "success",
        "info": "Processed %(items_count)d Failed 0 Total %(items_count)d Seconds spent 0.002070" % dict(
            items_count=items_count)
    }
    jsonresp = simplejson.dumps(resp)
    return jsonresp

def getHandler(request_type):
    if request_type == 'active checks':
        return __sendActiveChecks
    elif request_type == 'agent data':
        return __sendAgentData