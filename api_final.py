import httplib2
import os
import sys
import re


from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
DEVELOPER_KEY = "XXXXXX"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"


# Authorize the request and store authorization credentials.
def get_authenticated_service(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

# Trusted testers can download this discovery document from the developers page
# and it should be in the same directory with the code.
    return youtube

args = argparser.parse_args()
service = get_authenticated_service(args)
keyword = 'Убер Киев'

# publ_after = '2013-08-24T00:00:00Z'
# publ_before = '2016-02-24T00:00:00Z'

# publ_after = '2016-02-24T00:00:00Z'
# publ_before = '2016-08-24T00:00:00Z'

# publ_after = '2016-08-24T00:00:00Z'
# publ_before = '2017-02-24T00:00:00Z'

publ_after = '2017-07-24T00:00:00Z'
publ_before = '2017-08-24T00:00:00Z'

# for data that contains characters outside of the Basic Multilingual Plane
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)


def print_results(results):
    page = results["items"]
    print(results["pageInfo"])
    total_search_result = 0

    for video in page:
        title = video["snippet"]["title"].lower()
        description = video["snippet"]["description"].lower()
        channel = video["snippet"]["channelTitle"].lower()
        clean_chan = channel.translate(non_bmp_map)
        clean_title = title.translate(non_bmp_map)
        clean_descr = description.translate(non_bmp_map)
        re_pattern = r'\b(?:убер|uber)\b'
        match = re.findall(re_pattern, clean_title)
        match2 = re.findall(re_pattern, clean_descr)
        match3 = re.findall(re_pattern, clean_chan)
#  print (match)
#  print (match2)
#  print(match3)
        if (match or match2 or match3) and ('uber' or 'убер'):
            total_search_result = total_search_result + 1
            print("\nVideo title : %s" % clean_title)
        # print("Channel title : %s" % channel)
        # print("Channel description : %s" % clean_descr)
# print("Video viewed : %s " % video["statistics"]["viewCount"])

    print ("\n\t*-----Found after one run : %s -----*\n" % total_search_result)
    return total_search_result


# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.
def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title",
        # where  "snippet" will be an object and "title" will be a property in
        # that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]
            # Convert a name like "snippet.tags[]" to snippet.tags, but handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key)-2:]
                is_array = True
            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title", but the
                # resource does not yet have a "snippet" object. Create the
                # snippet object here. Setting "ref = ref[key]" means that in
                # the next time through the "for pa in range ..." loop, we will
                # be setting a property in the resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description", and the
                # resource already has a "snippet" object.
                ref = ref[key]
    return resource


# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            # Iterator objects: d.iteritems() -> iter(d.items())
            if value:
                good_kwargs[key] = value
    return good_kwargs

# END BOILERPLATE CODE


# Sample python code for search.list
def initial_search_list_by_keyword(service, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)  # See full sample for function
    results = service.search().list(**kwargs).execute()
    print(results["pageInfo"]["totalResults"])
    print(len(results["items"]))

    if "nextPageToken" in results:
        nextPageToken = results.get("nextPageToken")
#  results["pageToken"] = pagetoken

    kwargs.update({'pageToken': str(nextPageToken)})
    kwargs = remove_empty_kwargs(**kwargs)
# print(kwargs)
#  print(results.get("pageToken"))
    print_results(results)
    resultCount = results["pageInfo"]["totalResults"]
    result_found = 0

    while (resultCount > 0 and nextPageToken is not None):
        next_response = service.search().list(
            part='id,snippet',  # snippet
            pageToken=nextPageToken,
            regionCode='UA',
            order='rating',  # 'relevance, rating
            publishedAfter=publ_after,
            publishedBefore=publ_before,
            maxResults=25,
            q=keyword,
            type='video',
            ).execute()

#    for i in next_response:
#      print i

        if "nextPageToken" in next_response and
        next_response["nextPageToken"] is not None:
            nextPageToken = next_response["nextPageToken"]
            print(nextPageToken)
        if len(next_response["items"]) == 0:
            print("no more results left")
            return
            # count all the matches of all runs of the query

#    print(len(next_response["items"]))
        print_results(next_response)
    resultCount -= 25


def runQuery():
    initial_search_list_by_keyword(
        service,
        part='id,snippet',
        order='rating',
        # location='50.436514, 30.486680',
        # locationRadius='20km',
        publishedAfter=publ_after,
        publishedBefore=publ_before,
        maxResults=25,
        q=keyword,
        type='video',
        )

if __name__ == "__main__":
    runQuery()


# pri zaprose убер київ za poslednij mesyats vydaet stolko zhe reultatov skolko
# sam poisk v youtube
