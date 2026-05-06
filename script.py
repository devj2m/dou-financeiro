import requests
from bs4 import BeautifulSoup
from datetime import datetime

data = datetime.today().strftime('%Y-%m-%d')

url = f"https://www.in.gov.br/leiturajornal?data={data}"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

titulos = soup.find_all("p")

for t in titulos:
    print(t.text)
