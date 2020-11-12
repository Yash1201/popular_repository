from django.shortcuts import render, redirect
import requests
from django.contrib import messages


def home(request):
    if request.method == 'POST':
        org_name = request.POST['org_name']  # Organisation Name
        n = int(request.POST['n'])  # Number of most forked repository
        m = int(request.POST['m'])  # Number of top contributors

        if n <= 0 or m <= 0 or len(org_name) == 0:  # checking invalid input
            messages.info(request, 'Invlaid Input')
            return redirect('/')
        org_name = org_name.lower()
        org_url = f"https://api.github.com/search/repositories?q=org%3A{org_name}&order=desc&sort=forks&page=1&per_page=100"
        response = requests.get(org_url).json()

        if 'message' in response:  # checking name is incorrect
            messages.info(request, 'NO Organisation found !')
            return redirect('/')

        elif response['items'][0]['owner']['type'] != "Organization":  # checking if it is organisation or user
            messages.info(request, 'NO Organisation found !')
            return redirect('/')

        elif response['total_count'] == 0:  # if there is no repository in Organisation
            messages.info(request, 'NO Repository found !')
            return redirect('/')

        else:  # everything is correct till now
            array = []  # making a list to collect all the data
            most_forked = min(n, response['total_count'])  # checking if n is greater then total repository
            no_of_page = int(n / 100)  # dividing by 100 becoz at one request we can get details max of 100 repository
            left_repo = most_forked

            for i in range(no_of_page + 1):  # this loop is for how many pages we have to hit to get that much of data
                url = f"https://api.github.com/search/repositories?q=org%3A{org_name}&order=desc&sort=forks&page={i + 1}&per_page=100"
                response = requests.get(url).json()
                try:
                    cur_repo = min(left_repo, len(response['items']))
                    left_repo -= len(response['items'])

                    for j in range(cur_repo):  # this loop is to traverse all repository that we get in a response

                        dictionary = {}  # this is use to store all the data in dictionary format
                        dictionary['name'] = response['items'][j]['name']
                        dictionary['link'] = response['items'][j]['html_url']
                        dictionary['fork'] = response['items'][j]['forks_count']

                        contri_url = response['items'][j][
                            'contributors_url']  # extracting the api link of contributor list
                        contri_url += '?page=1&per_page=100'
                        contri_repsonse = requests.get(contri_url).json()  # geting the data of contributor(committees)
                        dictionary['contribution'] = []  # storing the details of contributor

                        try:

                            for k in range(min(m, len(contri_repsonse))):  # traversing the details of all committees

                                contri_dict = {};
                                contri_dict['name'] = contri_repsonse[k]['login']
                                contri_dict['link'] = contri_repsonse[k]['html_url']
                                contri_dict['commit'] = contri_repsonse[k]['contributions']
                                dictionary['contribution'].append(contri_dict)
                        except:
                            print("Skipping. Request Limit Exceed error")
                        array.append(dictionary)  # at last appending all the data in array to pass to html page
                except:
                    print("error")
            # print(len(array))
            org_name = org_name.upper()
            rend_dict = {"array": array, "org_name": org_name}
            return render(request,'repository.html', {"rend_dict": rend_dict})  # rendering(passing) the value
    else:
        return render(request, 'home.html')