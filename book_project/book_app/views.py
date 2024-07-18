from django.shortcuts import render
import requests
import logging
from django.http import HttpResponse,JsonResponse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import logging
import base64
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
main_url="http://127.0.0.1:8001"
def count_books(request):
    url1 = main_url+"/books_count"
    url2 = main_url+"/author_count"
    url3 = main_url+"/five_star_count"
    url4 = main_url+"/top_five_books"
    url5= main_url+"/top_five_authors"
    url6= main_url+"/ratings_count"
    try:
        response1 = requests.get(url1)
        response2 = requests.get(url2)
        response3 = requests.get(url3)
        reponse4 = requests.get(url4)
        response5 = requests.get(url5)
        response6 = requests.get(url6)
        if response1.status_code == 200 and response2.status_code == 200 and response3.status_code == 200 and reponse4.status_code == 200 and response5.status_code==200 and response6.status_code==200:
            data1 = response1.json()
            data2 = response2.json()
            data3 = response3.json()
            data4 = reponse4.json()
            data5 = response5.json()
            data6 = response6.json()
            top_books = []
            for book in data4:
                top_books.append({
                    'image': book[0],
                    'name': book[1],
                    'author': book[2]
                })
            authors = list(data5.keys())
            books_count = list(data5.values())
            fig, ax = plt.subplots(figsize=(9, 7))
            ax.pie(books_count, labels=authors, colors=['#FF9EAA', '#FFD1DC', '#FFAFC9',    '#FF80A0', '#FF4D7A'], autopct='%1.1f%%')
            ax.axis('equal') 
            ax.set_title('Top 5 authors with highest number of books written',fontsize = 15)
            img1 = io.BytesIO()
            plt.savefig(img1, format='png')
            img1.seek(0)
            chart1_url = base64.b64encode(img1.getvalue()).decode()
            plt.close()

            ratings =list(data6.keys())
            ratings_count = list(data6.values())
            fig, ax = plt.subplots(figsize = (9,7))
            ax.bar(ratings, ratings_count, color=['#7469B6','#AD88C6','#E1AFD1','#DBC4F0','#053657'])
            for i, v in enumerate(ratings_count):
                ax.text(i, v + 3, str(v), color='black', ha='center')        
            ax.set_xlabel('Ratings Distribution')
            ax.set_ylabel('Ratings Count')
            ax.set_title('Ratings Distribution count', fontsize = 15)
            img2 = io.BytesIO()
            plt.savefig(img2, format='png')
            img2.seek(0)
            chart2_url = base64.b64encode(img2.getvalue()).decode()
            plt.close()

            content = {
                'count': data1,
                'count_author': data2,
                'five_count': data3,
                'five_images': top_books,
                'chart1':chart1_url,
                'chart2':chart2_url
            }
            return render(request, "dashboard.html",content)
        else:
            return HttpResponse("Failed to retrieve data", status=500)
    except Exception as e:
        logging.error(f"Error retrieving data: {e}")
        return HttpResponse("An error occurred", status=500)
    
def suggestions_search(request):
    booktitle_url = main_url+"/book_title_list"
    author_url = main_url+"/author_list"
    ratings_url = main_url+"/ratings_list"
    genres_url= main_url+"/genres_list"
    booktitle_response = requests.get(booktitle_url)
    author_response = requests.get(author_url)
    ratings_response = requests.get(ratings_url)
    genres_response=requests.get(genres_url)
    book_title = booktitle_response.json()
    author_names = author_response.json()
    ratings_data = ratings_response.json()
    genres_data=genres_response.json()
    books_title = [book[0] for book in book_title]
    authors_title = [author[0] for author in author_names]
    ratings_title=[str(rating[0]) for rating in ratings_data]
    genres_title=[genre[0] for genre in genres_data]
    categories = {
    "Books": books_title,
    "Authors": authors_title,
    "Genres":genres_title,
    "Ratings": ratings_title
    }
    if request.method == 'POST':
        category = request.POST.get('category')
        query = request.POST.get('query','').lower()
        suggestions = []
        if category in categories:
            suggestions = [item for item in categories[category] if query in item.lower()]
    return JsonResponse({"suggestions": suggestions})

logger = logging.getLogger(__name__)
def searching(request):
    if request.method == 'POST':
        option = request.POST.get('category')
        value = request.POST.get('query')
    else:
        option = request.GET.get('category')
        value = request.GET.get('query')

    logger.info(f"Search option: {option}, Search value: {value}")

    if option == "Books":
        response = requests.get(f"{main_url}/search_book_title/{value}")
        data = response.json()
        if not data:
            data = "Invalid"
    elif option == "Authors":
        response = requests.get(f"{main_url}/search_author/{value}")
        data = response.json()
        if not data:
            data = "Invalid"
    elif option == "Genres":
        response = requests.get(f"{main_url}/search_generes/{value}")
        data = response.json()
        if not data:
            data = "Invalid"
    elif option == "Ratings":
        response = requests.get(f"{main_url}/search_ratings/{value}")
        data = response.json()
        if not data:
            data = "Invalid"
    else:
        data = "Error"

    logger.info(f"API Response Data: {data}")

    if data == "Invalid" or data == "Error":
        context_data = {
            'book_name': data,
            'option': option,
            'query': value,
        }
        return render(request, 'search.html', context_data)

    page = request.GET.get('page', 1)
    paginator = Paginator(data, 10)

    if int(page)>paginator.num_pages:
        page_not_found=True
    try:
        books = paginator.page(page)
        page_not_found =False
    except PageNotAnInteger:
        books = paginator.page(1)
        page_not_found =False
    except EmptyPage:
        books = paginator.page(paginator.num_pages)
        

    context_data = {
        'book_name': books,
        'option': option,
        'query': value,
        'page_not_found' : page_not_found
    }
    logger.info(f"Context Data: {context_data}")

    

    return render(request, 'search.html', context_data)