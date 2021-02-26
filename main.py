import os
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

import requests,json
from bs4 import BeautifulSoup
class Book():
    def __init__(self,dir_prefix, session:requests.Session, id, name=None):
        self.view_url = 'http://wbsl.gov.in/bookReader.action?bookId={id}'
        self.session = session
        self.in_progress_dir= f'{dir_prefix}_in_progres'
        self.done_dir=f'{dir_prefix}_done'
        self.id = id
        self.short_name = None
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
    def get_info_from_meta(self)->None:
        bs = BeautifulSoup(self.session.get(self.meta_url.format(id=self.id)).content,'html.parser')
        trs = bs.find_all('tr')[1:]
        for el in trs:
            name,value=el.find_all('td')
            name=name.text
            value=value.text
            if name == 'Head Number:\xa0':
                self.head_number=value
            elif name == 'Title:\xa0' and self.name==None:
                while value[-1]==' ':
                    value=value[:-1]
                self.name=value
                self.short_name = value[:64]
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
    def generate_imgs_names(self)->None:
        for num in range(1,int(self.pages)+1):
            name=str(num)
            while len(name)<8:
                name = '0'+name
            self.image_list.append(name+'.jpg')
    def get_url(self)->str:
        return self.view_url.format(id=self.id)
    def get_img_list(self)->list:
        data =[]
        for el in self.image_list:
            data.append(self.image_url.format(disk_name=self.disk_name,title=self.name,image=el))
        return data
    def download(self)->None:
        self.__make_dir()
        for el in self.image_list:
            url = self.image_url.format(disk_name=self.disk_name,title=self.name,image=el)
            url = url.replace(' ','%20')
            open(f'{self.in_progress_dir}/{self.short_name}/{el}', 'wb').write(session.get(url).content)
    def async_download(self):
        self.__make_dir()


    def make_pdf(self)->None:
        pass
    def __make_dir(self):
        try:
            os.mkdir(self.in_progress_dir)
        except FileExistsError:
            pass
        try:
            os.mkdir(f'{self.in_progress_dir}/{self.short_name}')
        except FileExistsError:
            pass
if __name__ == '__main__':
    ids = [x for x in range(1,22000)]
    session = requests.session()
    book = Book('./pdf',session, '13992')
    book.get_info_from_meta()
    book.generate_imgs_names()
    book.download()