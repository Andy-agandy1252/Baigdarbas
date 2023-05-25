from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from pycoingecko import CoinGeckoAPI
from django.core.paginator import Paginator
import base64
import requests
from bs4 import BeautifulSoup
from .models import Reklama, UserProfile, Article, Comment, CommentLike, CommentDislike, Feedback
from django.urls import reverse
from .forms import ArticleForm, ReklamaForm, CommentForm, FeedbackForm
import csv
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse

cg = CoinGeckoAPI()


def index(request):
    all_articles = []
    articles = Article.objects.all()
    reklama = Reklama.objects.all()
    url = 'https://www.delfi.lt'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Scrape headlines
    headline_tags = soup.select('.headline-category a')
    headlines = [i.get_text() for i in headline_tags]
    # Scrape titles and images
    title_tags = soup.select('.CBarticleTitle')
    titles = [i.get_text() for i in title_tags]
    title_links = [i['href'] for i in title_tags]
    images = [i['data-src'] for i in soup.select('.img-responsive')]
    # Combine titles, headlines, and images using zip function
    combined_list = zip(titles, headlines, images, title_links)
    # Create and append new Article objects to the all_articles list
    # scraped part
    for title, headline, image, title_link in combined_list:
        # article = Article(title=title, headline=headline, image=image, is_scraped=True)
        title_encode = str(base64.urlsafe_b64encode(bytes(title_link, 'utf-8')), 'utf-8')
        article = {
            'title': title,
            'headline': headline,
            'image': image,
            'title_link': reverse("scraped_article_detail", kwargs={"article_link": title_encode}),
        }
        all_articles.append(article)
        # my part
    for article in articles:
        article = {
            'title': article.title,
            'headline': article.headline,
            'image': article.image.url,
            'title_link': f"/pergale/article/{article.id}/",
        }
        all_articles.append(article)
    return render(request, 'index.html', {'articles': all_articles, 'reklama': reklama})


def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    comments = Comment.objects.filter(article=article)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            return redirect('article_detail', article_id=article.id)

        comment_id = request.POST.get('comment_id')
        if comment_id:
            comment = Comment.objects.get(id=comment_id)
            user = request.user
            if user.is_authenticated:
                if 'like' in request.POST and not CommentLike.objects.filter(user=user, comment=comment).exists():
                    if CommentDislike.objects.filter(user=user, comment=comment).exists():
                        CommentDislike.objects.filter(user=user, comment=comment).delete()
                    CommentLike.objects.create(user=user, comment=comment)
                    comment.likes = CommentLike.objects.filter(comment=comment).count()
                    comment.dislikes = CommentDislike.objects.filter(comment=comment).count()
                    comment.save()
                elif 'dislike' in request.POST and not CommentDislike.objects.filter(user=user,
                                                                                     comment=comment).exists():
                    if CommentLike.objects.filter(user=user, comment=comment).exists():
                        CommentLike.objects.filter(user=user, comment=comment).delete()
                    CommentDislike.objects.create(user=user, comment=comment)
                    comment.likes = CommentLike.objects.filter(comment=comment).count()
                    comment.dislikes = CommentDislike.objects.filter(comment=comment).count()
                    comment.save()
            else:
                # Handle the case when the user is not authenticated
                return redirect('login') 

            return redirect('article_detail', article_id=article.id)
    else:
        form = CommentForm()

    context = {
        'article': article,
        'comments': comments,
        'form': form
    }
    return render(request, 'article.html', context)


def scraped_article_detail(request, article_link):
    # make request to article link and parse with BeautifulSoup
    url = base64.urlsafe_b64decode(article_link)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    try:
        # remove unwanted content
        for unwanted in soup.select('.twitter-tweet, .css-901oao'):
            unwanted.extract()
        article_title = soup.find('head').find('title').text.strip().split(' - ')[0]
        date_time = soup.find('div', class_='source-date').text.strip()
        article_lead = soup.find('div', class_='delfi-article-lead').text.strip()
        article_body = soup.find('div', class_='delfi-article-body')
        paragraphs = article_body.find_all('p')
        # clean up paragraphs
        clean_paragraphs = []
        for paragraph in paragraphs:
            paragraph_text = paragraph.get_text(strip=True)
            if paragraph_text:
                # check if the paragraph still has text after removing unwanted content
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
        return render(request, 'scraped_article.html', context)
    except:
        return render(request, 'no_article.html')


def crypto(request):
    sort_options = [
        ('price_desc', 'Price (high to low)'),
        ('price_asc', 'Price (low to high)'),
        ('market_cap_rank_desc', 'Market Cap Rank (Bottom to Top)'),
        ('market_cap_rank_asc', 'Market Cap Rank (Top to Bottom)'),
        ('market_cap_change_desc', 'Market Cap Change % (high to low)'),
        ('market_cap_change_asc', 'Market Cap Change % (low to high)'),
        ('name_asc', 'Name (A-Z)'),
        ('name_desc', 'Name (Z-A)'),
    ]
    selected_sort_option = request.GET.get('sort_by', 'price_desc')
    data = cg.get_coins_markets(vs_currency='usd')
    if selected_sort_option == 'price_asc':
        data = sorted(data, key=lambda x: x['current_price'])
    elif selected_sort_option == 'price_desc':
        data = sorted(data, key=lambda x: x['current_price'], reverse=True)
    elif selected_sort_option == 'market_cap_rank_asc':
        data = sorted(data, key=lambda x: x['market_cap_rank'])
    elif selected_sort_option == 'market_cap_rank_desc':
        data = sorted(data, key=lambda x: x['market_cap_rank'], reverse=True)
    elif selected_sort_option == 'market_cap_change_asc':
        data = sorted(data, key=lambda x: x['market_cap_change_percentage_24h'])
    elif selected_sort_option == 'market_cap_change_desc':
        data = sorted(data, key=lambda x: x['market_cap_change_percentage_24h'], reverse=True)
    elif selected_sort_option == 'name_asc':
        data = sorted(data, key=lambda x: x['name'])
    elif selected_sort_option == 'name_desc':
        data = sorted(data, key=lambda x: x['name'], reverse=True)
    paginator = Paginator(data, 20)  # Show 20 cryptocurrencies per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    reklama = Reklama.objects.all()  # Get the first Reklama instance
    context = {
        'page_obj': page_obj,
        'sort_options': sort_options,
        'selected_sort_option': selected_sort_option,
        'reklama': reklama,
    }
    return render(request, 'crypto.html', context)


def crypto_detail(request, id):
    # Get detailed information about the cryptocurrency with the given ID
    crypto_data = cg.get_coin_by_id(id)
    # Get historical market data for the last week
    week_data = cg.get_coin_market_chart_by_id(id, vs_currency='usd', days=365)
    # Write the historical data to a CSV file
    with open('newsportal/static/historydata/{}_prices.csv'.format(id), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Price'])
        writer.writerows(week_data['prices'])
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
    # Pass data and plot to the template context
    context = {
        'crypto_data': crypto_data,
        'data': df.to_json(orient='split'),
        'csv_path': csv_path,
    }
    return render(request, 'crypto_detail.html', context)


@login_required
def add_article(request):
    user_profile = request.user.userprofile
    if user_profile.balanse <= 29:
        return redirect('balanse')
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user.username
            article.save()
            # Subtract 30 from user's balanse
            user_profile.balanse -= 30
            user_profile.save()
            return redirect('article_detail', article_id=article.id)
    else:
        form = ArticleForm()
    return render(request, 'add_article.html', {'form': form})


@login_required
def add_reklama(request):
    user_profile = request.user.userprofile
    if user_profile.balanse <= 19:
        return redirect('balanse')
    if request.method == 'POST':
        form = ReklamaForm(request.POST, request.FILES)
        if form.is_valid():
            reklama = form.save(commit=False)
            reklama.save()
            # Subtract 20 from user's balanse
            user_profile.balanse -= 20
            user_profile.save()
            return redirect('index')
    else:
        form = ReklamaForm()
    return render(request, 'add_reklama.html', {'form': form})


@login_required
def balanse(request):
    if request.method == 'POST':
        user = request.user
        user.save()
        user.userprofile.balanse = request.POST['balanse']
        user.userprofile.save()
        return redirect('balanse')
    return render(request, 'balanse.html')


def what_is_pro(request):
    return render(request, 'what_is_pro.html')


def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    avatar_url = user_profile.avatar.url if user_profile.avatar else None
    return render(request, 'profile.html', {'profile': user_profile, 'avatar_url': avatar_url})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.username = request.POST['username']
        user.email = request.POST['email']
        if request.POST['password']:
            user.set_password(request.POST['password'])
        user.save()
        user_profile = user.userprofile
        user_profile.bio = request.POST['bio']
        user_profile.location = request.POST['location']
        # Check if an image file was uploaded
        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            print(avatar.name)
            print(avatar.content_type)
            # Save the image in the user profile
            user_profile.avatar = avatar
        user_profile.save()
        return redirect('profile')
    else:
        return render(request, 'profile_edit.html')


@csrf_protect
def register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
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
                    user = User.objects.create_user(username=username, email=email, password=password,
                                                    first_name=first_name, last_name=last_name)
                    # Create a UserProfile instance for the user
                    UserProfile.objects.create(user=user, balanse=0)
                    messages.info(request, f'Vartotojas {username} užregistruotas!')
                    return redirect('login')
        else:
            messages.error(request, 'Slaptažodžiai nesutampa!')
            return redirect('register')
    return render(request, 'register.html')


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def contact_us(request):
    if request.method == 'POST':
        vardas = request.POST.get('first_name')
        pavarde = request.POST.get('last_name')
        el_pastas = request.POST.get('email')
        content = request.POST.get('content')
        subject = 'New Contact Form Submission'
        message = f'Vardas: {vardas}\nPavarde: {pavarde}\nEl. paštas: {el_pastas}\nContent: {content}'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [from_email]  # Use your own email address as the recipient
        send_mail(subject, message, from_email, recipient_list)
    return render(request, 'contact_us.html')


def about(request):
    return render(request, 'about.html')


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feedback')  # Redirect to a success page after saving the feedback
    else:
        form = FeedbackForm()
    feedbacks = Feedback.objects.all()  # Retrieve all feedbacks from the database
    return render(request, 'feedback.html', {'form': form, 'feedbacks': feedbacks})
