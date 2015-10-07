import sys
import json
import shutil
import os

import requests


def main():

    print("===== Initiating test run =========\n")

    # basic web-client check
    srv = sys.argv[1]

    r = getRequest(srv,'/')
    if r.status_code == 200:
        print("Web-client: available (+)")
    else:
        print("Web client is not available")



    # calling uuid
    r = getRequest(srv,'uuid')

    if(r.status_code) == 200:
        print("Getting uuid :" + getNormalisedResponseData(r)['uuid']+"   (+)")
    else:
        print("Test failed : " +r.text)

    # calling video-origins

    r = getRequest(srv,'video-origins')

    if r.status_code == 200:
        s_count = 0
        srv_list = set([])
        video_sources = set([])
        for i in getNormalisedResponseData(r):
            s_count += 1
            video_sources.add(i)
            srv_list.add(i.split('/')[0])
        print("Getting video-origins: Total of %s sources were found" % s_count + "  (+)")
    else:
        print("Test failed : " +r.text)

    # calling per-server sources list
    for server in srv_list:
        r = getRequest(srv,"video-origins/"+server)
        s_count = 0
        if r.status_code == 200:
            for i in getNormalisedResponseData(r):
                s_count += 1
            print("Getting server-specific video-origins: Total of %s sources were found for server %s" % (s_count,server) + "  (+)")
        else:
            print("Test failed : " +r.text)

    # getting a snapshot from the cameras
    s_count = 0
    f_size = 0
    for camera in video_sources:
        r = requests.get('http://' + str(srv) + '/live/media/snapshot/' + camera, auth=('root', 'root'), stream=True)
        if r.status_code == 200:
            with open('t_img.jpg','wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw,f)
                f.close()
                f_size += os.stat('t_img.jpg').st_size
            s_count += 1
            os.remove(f.name)
            print('Getting a snapshot from the camera %s. Got %s snapshots total. Downloaded size : %s Bytes (+)' % (
                camera, s_count, f_size))
        else:
            print('Failed to get a snapshot for camera %s. Response status code : %s.' % (camera, r.status_code))

    # getting a video stream (just a request)
    # TODO: get & play (or save) actual video stream
    for camera in video_sources:
        r = getRequest(srv, 'live/media/' + camera + '?format=rtsp')
        if r.status_code == 200:
            print('Got a videostream for camera %s. (+)' % camera)
        else:
            print('Failed to get a videostream for camera %s. Response code %s' % (camera, r.status_code))

    # get archive intervals
    intervals = dict()
    for camera in video_sources:
        r = getRequest(srv, 'archive/contents/intervals/' + camera + '/future/past')
        if r.status_code == 200:
            intervals[camera] = getNormalisedResponseData(r)
            print("Got intervals for camera %s (+)" % camera)
        else:
            print("Failed to get intervals for camera %s" % camera)

    # get archive video stream (just a request)
    # TODO: get & play (or save) actual video stream
    for camera in video_sources:
        r = getRequest(srv, 'archive/media/' + camera + '/past')
        if r.status_code == 200:
            print('Got an archive video stream for camera %s (+)' % camera)
        else:
            print("Failed to get an archive video stream for camera %s" % camera)

    # get statistics
    r = getRequest(srv, 'statistics/webserver')
    if r.status_code == 200:
        print("Got webserver statistics: (+)")
        for k in getNormalisedResponseData(r):
            print(str(k) + " : " + str(getNormalisedResponseData(r)[k]))

    # per camera statistics
    for camera in video_sources:
        r = getRequest(srv, 'statistics/' + camera)
        if r.status_code == 200:
            print("Got statistics for camera %s (+)" % camera)
        else:
            print("Failed to get statistics for camera %s" % camera)

    # get displays
    r = getRequest(srv, 'GetDisplays')
    if r.status_code == 200:
        print("Got displays list (+)")
    else:
        print("Failed to get displays")

    # get Layouts
    r = getRequest(srv, 'GetLayouts')
    if r.status_code == 200:
        print("Got layouts list (+)")
    else:
        print("Failed to get layouts")

    # get alerts
    for camera in video_sources:
        r = getRequest(srv, 'archive/events/alerts/' + camera + "/future/past?limit=100")
        if r.status_code == 200:
            print("Got alerts for camera %s" % camera)
        else:
            print("Failed to get alerts for camera %s" % camera)

    # get detector's events
    for camera in video_sources:
        r = getRequest(srv, 'archive/events/detectors/' + camera + "/future/past?limit=100")
        if r.status_code == 200:
            print("Got detector's events for camera %s" % camera)
        else:
            print("Failed to get detector's events for camera %s" % camera)

    print("===== Test finished! ======")

def getNormalisedResponseData(req):
    return json.loads(req.text)

def getRequest(srv,api_command):
    # print("api call :" + "http://" + str(srv) + "/" + api_command)
    return requests.get("http://"+str(srv)+"/"+api_command, auth=('root','root'))

if __name__ == "__main__" : main()