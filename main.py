import downloader
import time
import httplib
import urllib
import urllib2
from bs4 import BeautifulSoup

# url of the site
url = 'http://aplikasi.pertanian.go.id/bdsp/newkom.asp'
# download url
download_url = 'http://aplikasi.pertanian.go.id/bdsp/hasil_kom.asp'

# initialize request dictionary
request_values = {}
values_in_use = []


def main():
    # get initial page
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)

    # get all the drop-downs from page
    selects = soup.findAll('select')

    # populate dictionary from response
    post_request_dict_update(selects)

    # initiate the traversing
    recursive_func(selects)


def recursive_func(selectors, hidden_inputs=[]):
    for select in selectors:
        # get name of the selector (a.k.a. province, status, years, etc.)
        opt_name = select.attrs.get('name')

        # if it is already in use go to next selector
        if opt_name in values_in_use:
            continue

        # else append it to the list of selectors in use
        values_in_use.append(opt_name)

        # get all available options and iterate over them
        options = select.findAll('option')
        for opt in options:
            opt_value = opt.attrs.get('value')
            if opt_value == '':
                continue

            # generate the new POST data
            request_values[opt_name] = opt_value

            for hidden_input in hidden_inputs:
                request_values[hidden_input.attrs.get('name')] = hidden_input.attrs.get('value')

            new_request_data = urllib.urlencode(request_values)
            print('New headers to be send', new_request_data)  # for debugging/logging purposes

            # send the next POST request

            new_request = make_request(new_request_data)
            new_soup = BeautifulSoup(new_request)
            new_selects = new_soup.findAll('select')
            new_inputs = new_soup.findAll('input')
            hidden_inputs = []
            for new_input in new_inputs:
                if new_input.attrs.get('type') == 'hidden':
                    hidden_inputs.append(new_input)
            # sleep for 2 seconds so that we don't overflow the request servers
            time.sleep(3)

            # go to the next iteration of the loop
            recursive_func(new_selects, hidden_inputs)

        # once we have exercised all options for a level remove it from used list
        # so we can iterate over it once again by exercising the next option of the
        # parent selector. If by removing it we end up removing the only child (root)
        # that means we have completed.

        values_in_use.remove(opt_name)

        if len(values_in_use) == 0:
            exit("Completed!")

    print("Download now!")
    downloader.download_file(download_url, request_values)
    # remove hidden values to prevent duplication
    for hidden_input in hidden_inputs:
        if request_values.has_key(hidden_input.attrs.get('name')):
            request_values.pop(hidden_input.attrs.get('name'))


def make_request(new_request_data):
    successful_request = False

    while not successful_request:
        try:
            new_request = urllib2.urlopen(url, new_request_data).read()
            successful_request = True
        except(IOError, httplib.HTTPException):
            print ("Error happened! headers: ", new_request_data)

    return new_request


def post_request_dict_update(selectors):
    for selector in selectors:
        name = selector.attrs.get('name')
        selected_value_list = selector.findAll('option', attrs={'selected': ''})
        selected_value = ''
        if len(selected_value_list) == 1:
            selected_value = selected_value_list[0].attrs.get('value')

        request_values[name] = selected_value
    print("The first request will be made with the following values", request_values)


main()