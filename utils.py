#!/usr/bin/python
import datetime
from urllib.parse import urlencode

import validators
import requests

global debug

def httpget(url, timeout=30,params={},headers={}):
    if validators.url:
        try:
            if len(params) == 0:
                httpresp = requests.get(url,timeout=timeout,headers=headers)
            else:
                httpresp = requests.get(url,timeout=timeout,headers=headers,params=urlencode(params))

            return httpresp

        except requests.exceptions.HTTPError as err:
            print(format(err)+"\n HTTP Error from Server with URL:"+format(url))
            return "URL_ERROR"
        except requests.exceptions.ConnectionError as err:
            print(format(err)+"\n Error Connecting to URL:"+format(url)+"\n"+str(params))
            return "URL_ERROR"
        except requests.exceptions.Timeout as err:
            # Maybe set up for a retry, or continue in a retry loop
            print(format(err)+"\n Request TimeOut on URL:"+format(url))
            return "URL_ERROR"
        except requests.exceptions.TooManyRedirects as err:
            # Tell the user their URL was bad and try a different one
            print(format(err)+"\n Too Many redirects on URL:"+format(url))
            return "URL_ERROR"
        except requests.exceptions.RequestException as err:
            # catastrophic error. bail.
            print(format(err)+"\n Error in HTTP Connection for URL:"+format(url))
            return "URL_ERROR"
    else:
        print("Malformed URL")
        return "URL_ERROR"

def c_print(data):
    if debug:
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(date + ": " + data)
