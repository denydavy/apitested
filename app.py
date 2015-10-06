import requests, sys, time, json, tempfile, shutil, os

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
        #print(server)
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
        r = getRequest(srv,'live/media/snapshot/'+camera)
        if r.status_code == 200:
            with open('t_img.jpg','wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw,f)
                f_size += os.stat('t_img.jpg').st_size
            time.sleep(1)
            f.close()
            s_count += 1
    print('Getting a snapshot from the camera. Got %s snapshots total. Downloaded size : %s' % (s_count,f_size))
    os.remove(f)

def getNormalisedResponseData(req):
    return json.loads(req.text)

def getRequest(srv,api_command):
    #print("api call :"+"http://"+str(srv)+"/"+api_command)
    return requests.get("http://"+str(srv)+"/"+api_command, auth=('root','root'))

if __name__ == "__main__" : main()