import requests
import time
import csv

my_key = 'your-key-here'

def clean_json(articles):
    
    cleaned_articles = []
    
    for article in articles['response']['docs']:
        
        dct = {}
        
        if article['abstract'] is not None:
            dct['abstract'] = article['abstract']
        if article['lead_paragraph'] is not None:
            dct['lead_paragraph'] = article['lead_paragraph']
        if article['headline']['main'] is not None:
            dct['main_headline'] = article['headline']['main']
        if article['headline']['print_headline'] is not None:
            dct['print_headline'] = article['headline']['print_headline']
        if article['pub_date'] is not None:
            dct['pub_date'] = article['pub_date']
        if article['word_count'] is not None:
            dct['word_count'] = article['word_count']
        if article.get('type_of_material',None) is not None:
            dct['type_of_material'] = article['type_of_material']
    
        cleaned_articles.append(dct)
    
    return cleaned_articles
        
def get_data(year,filters, length):
    
    all_articles = []
    
    if len(filters) > 1:
        f = 'fq='
        for k, v in filters.items():
            f = f + f'{k}:({v}) ' + 'AND '
        f = f.rstrip('AND ')
    
    
    if length == 'full':
        begin_date = str(year) + '0101'
        end_date = str(year) + '1231'
    elif length == 'first-half': 
        begin_date = str(year) + '0101'
        end_date = str(year) + '0630'
    elif length == 'second-half':
        begin_date = str(year) + '0701'
        end_date = str(year) + '1231'
        
    for i in range(0,100):
        print(f'Getting data from page {i}')
        url = f'https://api.nytimes.com/svc/search/v2/articlesearch.json?{f}&page={i}&begin_date={begin_date}&end_date={end_date}&sort=oldest&api-key='+my_key
        print(url)
        
        r = requests.get(url)

        articles = r.json()
        
        try:
            articles = clean_json(articles)

            all_articles = all_articles + articles
            time.sleep(10)
        except KeyError:
            break
        
    return all_articles


def create_file(start,end,length):
    
    final_articles = []
    
    for year in range(start, end):
        yearly_articles = get_data(year,{'source':'"The New York Times"','section_name':'Obituaries'},length=length)
        final_articles = final_articles + yearly_articles
    print(final_articles)
    with open(f'death_data.csv','a', newline='') as csvfile:
        if final_articles:
            fieldnames=final_articles[0].keys()
            writer=csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(final_articles)
    
    print(f'Data added.')

start_years = list(range(1985, 2020, 1))
end_years = list(range(1986, 2021, 1))

for start, end in zip(start_years,end_years):
    print(f"Starting {start}")
    create_file(start=start,end=end,length='first-half')
    create_file(start=start,end=end,length='second-half')
