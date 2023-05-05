import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from pycoingecko import CoinGeckoAPI
from django.core.paginator import Paginator
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import csv


def index(request):
    url = "https://www.delfi.lt/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # Scrape headlines
    headline_tags = soup.select('.headline-category a')
    headlines = [i.get_text() for i in headline_tags]
    # Scrape titles and links
    title_tags = soup.select('.CBarticleTitle')
    titles = [i.get_text() for i in title_tags]
    title_links = [i['href'] for i in title_tags]
    # Combine titles, title links, and headlines using zip function
    combined_list = zip(titles, title_links, headlines)
    return render(request, 'index.html', {'combined_list': combined_list})


def article_detail(request, article_link):
    # make request to article link and parse with BeautifulSoup
    url = article_link
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        # remove unwanted content
        for unwanted in soup.select('.twitter-tweet, .css-901oao'):
            unwanted.extract()
        article_title = soup.find('head').find('title').text.strip().split(" - ")[0]
        date_time = soup.find('div', class_='source-date').text.strip()
        article_lead = soup.find('div', class_='delfi-article-lead').text.strip()
        article_body = soup.find('div', class_='delfi-article-body')
        paragraphs = article_body.find_all('p')
        # clean up paragraphs
        clean_paragraphs = []
        for paragraph in paragraphs:
            paragraph_text = paragraph.get_text(strip=True)
            if paragraph_text:  # check if the paragraph still has text after removing unwanted content
                clean_paragraphs.append(paragraph_text)
        # find images
        images = []
        for image in article_body.find_all('img'):
            image_url = image['src']
            images.append(image_url)
        # find main image
        try:
            image_url = images[0]
        except:
            image_url = ""
        # truncate lead to 100 characters
        lead = article_lead[:100]
        # create context dictionary
        context = {
            'title': article_title,
            'date_time': date_time,
            'lead': lead,
            'paragraphs': clean_paragraphs,
            'images': images,
            'image_url': image_url,
        }
        return render(request, 'article.html', context)
    except:
        return render(request, 'no_article.html')


@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reikšmes iš registracijos formos
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # tikriname, ar sutampa slaptažodžiai
        if password == password2:
            # tikriname, ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Vartotojo vardas {username} užimtas!')
                return redirect('register')
            else:
                # tikriname, ar nėra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(request, f'Vartotojas su el. paštu {email} jau užregistruotas!')
                    return redirect('register')
                else:
                    # jeigu viskas tvarkoje, sukuriame naują vartotoją
                    User.objects.create_user(username=username, email=email, password=password)
                    messages.info(request, f'Vartotojas {username} užregistruotas!')
                    return redirect('login')
        else:
            messages.error(request, 'Slaptažodžiai nesutampa!')
            return redirect('register')
    return render(request, 'register.html')


def get_currency_name(symbol):
    endpoint = 'https://api.binance.com/api/v3/ticker/24hr'
    response = requests.get(endpoint, params={'symbol': symbol}).json()
    return response['symbol'], response['name']


cg = CoinGeckoAPI()


def crypto(request):
    data = cg.get_coins_markets(vs_currency='usd')
    paginator = Paginator(data, 20)  # Show 20 cryptocurrencies per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}

    return render(request, 'crypto.html', context)


def crypto_detail(request, id):
    # Get detailed information about the cryptocurrency with the given ID
    crypto_data = cg.get_coin_by_id(id)
    # Get historical market data for the last week
    week_data = cg.get_coin_market_chart_by_id(id, vs_currency='usd', days=7)
    # Write the historical data to a CSV file
    week_prices = [price[1] for price in week_data['prices']]
    with open('newsportal/static/historydata/{}_prices.csv'.format(id), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Price'])
        writer.writerows(zip(week_prices))
    # Create a Pandas DataFrame from the market data
    df = pd.DataFrame(week_data['prices'], columns=['Timestamp', 'Price'])
    # Convert the Timestamp column to datetime format
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    # Set the Timestamp column as the DataFrame index
    df.set_index('Timestamp', inplace=True)
    # Convert the Price column to numeric format
    df['Price'] = pd.to_numeric(df['Price'])
    # Save DataFrame to CSV
    csv_path = f'newsportal/static/historydata/{id}_prices.csv'
    df.to_csv(csv_path, index=True, header=True)
    # Create a seaborn lineplot from the DataFrame
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df)
    plt.title(f'{crypto_data["name"]} Price Chart')
    plt.xlabel('Date')
    plt.ylabel(f'Price (USD)')
    # Save the plot to a file
    img_path = f'newsportal/static/historydata/{id}_prices.png'
    plt.savefig(img_path, bbox_inches='tight')
    # Convert the plot to base64 encoded string
    with open(img_path, 'rb') as f:
        img_data = f.read()
        img_data = base64.b64encode(img_data).decode('utf-8')
    # Pass data and plot to the template context
    context = {
        'crypto_data': crypto_data,
        'data': df.to_json(orient='split'),
        'plot': img_data
    }
    return render(request, 'crypto_detail.html', context)
