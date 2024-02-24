import requests
import pandas as pd
from bs4 import BeautifulSoup

dataML = {
    'Nome Produto': [],
    'URL Produto': [],
    'Preço': [],
    'Vendedor': [],
    'URL Vendedor': []
}

def dataHandler(soap: BeautifulSoup):
    next = True
    while next:
        resultSearch = soap.find_all('div',{'class': 'ui-search-result__content-wrapper'})
        for item in resultSearch:
            productName = item.find('h2', {'class': 'ui-search-item__title'}).text
            print(productName)
            urlProduct = item.find('div', {'class': 'ui-search-item__group ui-search-item__group--title'}).find('a')['href']
            productPrice = item.find('span', {'class': 'andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript'}).text.replace('R$', '')
            detailProduct = requestML(urlProduct)
            sellerName = detailProduct.find('span', {'class': 'ui-pdp-color--BLUE ui-pdp-family--REGULAR'}).text
            detailURL = detailProduct.find('div', {
                'class': 'ui-box-component ui-box-component-pdp__visible--desktop'}) if detailProduct is not None else None
            try:
                sellerURL = detailURL.find('a', {'class': 'ui-pdp-media__action ui-box-component__action'})['href']
                appendList(productName, urlProduct, productPrice.replace(',', '.'), sellerName, sellerURL)
                pass
            except Exception as error:
                appendList(productName, urlProduct, productPrice.replace(',','.'), sellerName,
                           f"https://www.mercadolivre.com.br/perfil/{sellerName.replace(' ', '+')}")
                pass
        response = nextPage(soap)
        next = response[0]
        if next: soap = requestML(response[1])

def requestML(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
        site = requests.get(url,headers=headers)
        site.raise_for_status()
        return BeautifulSoup(site.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer solicitação para a página {e}")

def appendList(productName, productURL, price, seller, sellerURL):
    dataML['Nome Produto'].append(productName)
    dataML['URL Produto'].append(productURL)
    dataML['Preço'].append(price)
    dataML['Vendedor'].append(seller)
    dataML['URL Vendedor'].append(sellerURL)

def nextPage(soap):
    page = soap.find('li',{'class': 'andes-pagination__button andes-pagination__button--next'})
    print(page)
    if page is not None:
        url = page.find('a')['href']
        return True, url
    else:
        return False, ''

search = 'cd-henrique-juliano'
url = f'https://lista.mercadolivre.com.br/{search}'
dataHandler(requestML(url))

data = pd.DataFrame(data=dataML)
data.to_excel('tabela_produtos.xlsx', index=False)
