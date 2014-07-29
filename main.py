import downloader
import time
import httplib
import urllib
import urllib2
from bs4 import BeautifulSoup

# url of the site
url = 'http://aplikasi.pertanian.go.id/bdsp/newkom-e.asp'
# download url
download_url = 'http://aplikasi.pertanian.go.id/bdsp/hasil_kom-e.asp'

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
    iterate_over_selects(selects)


def iterate_over_selects(selectors, hidden_inputs=None):
    # if there are no hidden inputs specified default it to empty array
    if not hidden_inputs:
        hidden_inputs = []
    # iterate over the selects (drop-downs) on page
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

        # for each option of the current drop down - make a request
        iterate_over_options(options, opt_name, hidden_inputs)

        # Once we have exercised all options for a level remove it from the list of values in use.
        # We can then iterate over the same element once again by using the next option of the
        # parent selector. If by removing it we end up removing the only child (root)
        # that means we have completed.

        values_in_use.remove(opt_name)
        request_values[opt_name] = ''

        if len(values_in_use) == 0:
            exit("Completed!")

    # Proceed downloading the file
    if len(hidden_inputs) == 8:

        # process hidden fields into a request
        download_request_headers = {}
        for hidden_input in hidden_inputs:
            download_request_headers[hidden_input.attrs.get('name')] = hidden_input.attrs.get('value')

        # add 'excel' header
        download_request_headers['save'] = 'xl'

        #actually download
        downloader.download_file(download_url, download_request_headers)

        #end section


def iterate_over_options(options, opt_name, hidden_inputs):
    for opt in options:
        # skip empty values, those denote comments on the site (omg)
        opt_value = opt.attrs.get('value')
        if opt_value == '':
            continue

        # generate the new POST data
        request_values[opt_name] = opt_value

        # update the request values from hidden fields
        for hidden_input in hidden_inputs:
            if not request_values.has_key(hidden_input.attrs.get('name')):
                request_values[hidden_input.attrs.get('name')] = hidden_input.attrs.get('value')

        new_request_data = urllib.urlencode(request_values)
        print 'Request: ', new_request_data  # for debugging/logging purposes

        # send the next POST request
        new_request = make_request(new_request_data)

        # convert into Beautiful Soap
        new_soup = BeautifulSoup(new_request)

        # get selects & inputs
        new_selects = new_soup.findAll('select')
        new_inputs = new_soup.findAll('input')

        # get hidden inputs
        hidden_inputs = []
        for new_input in new_inputs:
            if new_input.attrs.get('type') == 'hidden':
                hidden_inputs.append(new_input)

        # sleep for 2 seconds so that we don't overflow the request servers
        time.sleep(5)

        # go to the next iteration of the loop
        iterate_over_selects(new_selects, hidden_inputs)


def make_request(new_request_data):
    successful_request = False

    while not successful_request:
        try:
            new_request = urllib2.urlopen(url, new_request_data).read()
            successful_request = True
        except(IOError, httplib.HTTPException, httplib.BadStatusLine):
            print 'Error happened! headers: ', new_request_data

    return new_request


def post_request_dict_update(selectors):
    for selector in selectors:
        name = selector.attrs.get('name')
        selected_value_list = selector.findAll('option', attrs={'selected': ''})
        selected_value = ''
        if len(selected_value_list) == 1:
            selected_value = selected_value_list[0].attrs.get('value')

        request_values[name] = selected_value
    print 'The first request will be made with the following values', request_values


main()