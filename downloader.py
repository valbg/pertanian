import urllib2
import urllib
import httplib


def download_file(url, request_values):

    # calculate the filename
    file_name = ''

    for key in request_values.keys():
        file_name += key + "-" + request_values[key] + "-"

    file_ext = '.xls'  # enforce downloads having excel extension
    req = urllib2.Request(url, headers={'User-Agent': "IE9"})  # identify as IE to avoid being blocked (403-ed)
    request_data = urllib.urlencode(request_values)

    u = make_request(req, request_data)

    f = open(file_name + file_ext, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buff = u.read(block_sz)
        if not buff:
            break

        file_size_dl += len(buff)
        f.write(buff)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status += chr(8) * (len(status) + 1)
        print status,

    print '\n'

    f.close()


def make_request(req, request_data):
    while True:
        try:
            response = urllib2.urlopen(req, request_data)
            break
        except(IOError, httplib.HTTPException, httplib.BadStatusLine):
            print 'HTTP EXCEPTION : Could not download file \n Will retry! \n'
    return response