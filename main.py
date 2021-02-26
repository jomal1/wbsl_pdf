from selenium.webdriver import Firefox
import multiprocessing
import requests,json
from bs4 import BeautifulSoup
class Book():
    def __init__(self, session:requests.Session, id, name=None):
        self.session = session
        self.id = id
        self.name = name
        self.head_number = None
        self.author = None
        self.description = None
        self.subject = None
        self.publisher = None
        self.pages = None
        self.publication_year = None
        self.digital_publication_year = None
        self.format = None
        self.type = None
        self.category = None
        self.disk_name = None
        self.source = None
        self.meta_url = 'http://wbsl.gov.in/bookSearchResult.action?bookId={id}'
        self.image_url = 'http://wbsl.gov.in/Books/{disk_name}/{title}/PTIFF/{image}'
        self.image_list = []
    def get_info_from_meta(self):
        bs = BeautifulSoup(self.session.get(self.meta_url.format(id=self.id)).content,'html.parser')
        trs = bs.find_all('tr')[1:]
        for el in trs:
            name,value=el.find_all('td')
            name=name.text
            value=value.text
            if name == 'Head Number:\xa0':
                self.head_number=value
            elif name == 'Title:\xa0' and self.name==None:
                self.name=value
            elif name == 'Author(s):\xa0':
                self.author = value
            elif name == 'Description:\xa0':
                self.description = value
            elif name == 'Subject:\xa0':
                self.subject = value
            elif name == 'Publisher:\xa0':
                self.publisher = value
            elif name == 'Total Pages:\xa0':
                self.pages = value
            elif name == 'Publication Year:\xa0':
                self.publication_year = value
            elif name == 'Digital Publication Date:\xa0':
                self.digital_publication_year = value
            elif name == 'Format:\xa0':
                self.format = value
            elif name == 'Document Type:\xa0':
                self.type = value
            elif name == 'Document Category:\xa0':
                self.category = value
            elif name == 'Disk Name:\xa0':
                self.disk_name = value
            elif name == 'Source:\xa0':
                self.source = value
    def generate_imgs_names(self):
        name=f'num.pdf'
        while len(name)<8:
            name = '0'+name
        self.image_list.append(name)





if __name__ == '__main__':
    wb = Firefox()