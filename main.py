import multiprocessing
import os
import time
import img2pdf
import requests, json
from bs4 import BeautifulSoup


class Book:
    def __init__(self, dir_prefix, session: requests.Session, id, name=None):
        self.view_url = 'http://wbsl.gov.in/bookReader.action?bookId={id}'
        self.session = session
        self.in_progress_dir = f'{dir_prefix}_in_progres'
        self.done_dir = f'{dir_prefix}_done'
        self.id = id
        self.short_name = None
        self.name = name
        self.head_number = None
        self.author = None
        self.subject = None
        self.publisher = None
        self.pages = None
        self.publication_year = None
        self.type = None
        self.disk_name = None
        self.source = None
        self.meta_url = 'http://wbsl.gov.in/bookReader.action?bookId={id}'
        self.image_url = 'http://wbsl.gov.in/Books/{disk_name}/{title}/PTIFF/{image}'
        self.image_list = []

    def get_info_from_meta(self) -> None:
        bs = BeautifulSoup(self.session.get(self.meta_url.format(id=self.id)).content, 'html.parser')
        els = bs.find_all('script')[-2].contents[0].replace('\n', '').replace("'", '').split('var')
        for el in els:
            try:
                name, value = el.split('=')
                name = name.strip()
                value = value.strip()
                if name[-1]==';':
                    name = name[:-1]
                    name.strip()
                if value[-1]==';':
                    value = value[:-1]
                    value.strip()

            except ValueError:
                name, value = ['', '']

            if name == 'bookheadno':
                self.head_number = value
            elif name == 'title' and self.name == None:
                while value != '' and value[-1] == ' ':
                    value = value[:-1]
                self.name = value

            elif name == 'author':
                self.author = value
            elif name == 'filename':
                self.short_name = value.replace('&#039;','\'')

            elif name == 'subject':
                self.subject = value
            elif name == 'publisher':
                self.publisher = value
            elif name == 'totalpages':
                self.pages = value
            elif name == 'publicationDate':
                self.publication_year = value
            elif name == 'documentType':
                self.category = value
            elif name == 'disk_name':
                self.disk_name = value
            elif name == 'source':
                self.source = value

    def generate_imgs_names(self) -> None:
        for num in range(1, int(self.pages) + 1):
            name = str(num)
            while len(name) < 8:
                name = '0' + name
            self.image_list.append(name + '.jpg')

    def get_url(self) -> str:
        return self.view_url.format(id=self.id)

    def get_img_list(self) -> list:
        data = []
        for el in self.image_list:
            data.append(self.image_url.format(disk_name=self.disk_name, title=self.short_name, image=el))
        return data

    def download(self) -> None:
        self.__make_dir()
        for el in self.image_list:
            url = self.image_url.format(disk_name=self.disk_name, title=self.short_name, image=el)
            url = url.replace(' ', '%20')
            open(f'{self.in_progress_dir}/{self.short_name}/{el}', 'wb').write(session.get(url).content)

    def async_download(self, workers: int):
        self.__make_dir()
        data = []
        for el in self.image_list:
            url = self.image_url.format(disk_name=self.disk_name, title=self.short_name, image=el)
            url = url.replace(' ', '%20')
            data.append(url)
        download = async_downloader(data, f'{self.in_progress_dir}/{self.short_name}', workers)
        while not download.done():
            time.sleep(0.1)

    def make_pdf(self) -> None:
        directory = f'{self.in_progress_dir}/{self.short_name}/'
        dir_list = os.listdir(f'{self.in_progress_dir}/{self.short_name}')
        dir_list.sort()
        images = []

        for el in dir_list:
            images.append(directory + el)
        open(f'{self.done_dir}/{self.short_name}.pdf', 'wb').write(img2pdf.convert(images))
        self.__delete_dir()

    def __delete_dir(self):
        try:
            for el in os.listdir(f'{self.in_progress_dir}/{self.short_name}'):
                os.remove(f'{self.in_progress_dir}/{self.short_name}/{el}')
            os.rmdir(f'{self.in_progress_dir}/{self.short_name}')
        except:
            pass

    def __make_dir(self):
        try:
            os.mkdir(self.in_progress_dir)
        except FileExistsError:
            pass
        try:
            os.mkdir(self.done_dir)
        except FileExistsError:
            pass
        try:
            os.mkdir(f'{self.in_progress_dir}/{self.short_name}')
        except FileExistsError:
            pass


class async_downloader(multiprocessing.Process):
    def __init__(self, images: list, dir, num, session=requests.session()):
        multiprocessing.Process.__init__(self)
        self.session = session
        self.images = images
        self.num = num
        self.dir = dir
        self.__status = multiprocessing.Value('i', 0)

        self.start()

    def start(self) -> None:
        downloaders = []
        while self.images or downloaders:
            if len(downloaders) < self.num and self.images:
                img = self.images[0]
                self.images.remove(img)
                tmp = multiprocessing.Process(target=download, args=(img, self.dir + '/' + img.split('/')[-1]))
                tmp.start()
                downloaders.append(tmp)
            for el in downloaders:
                if not el.is_alive():
                    if el.exitcode == -1:
                        print('error')
                    downloaders.remove(el)
        self.__status.value = 1

    def done(self):
        if self.__status.value == 1:
            return True

        else:
            return False


def download(image, dir):
    while True:
        try:
            rs = requests.get(image)
            open(dir, 'wb').write(rs.content)
            if len(rs.content) > 100 and rs.status_code == 200 and len(open(dir,'rb').read())>100:
                return 1
        except:
            pass
        print('error', dir, image)


if __name__ == '__main__':
    try:

        ids = json.load(open('progress.json'))
    except FileNotFoundError:
        ids = [x for x in range(1, 22001)]
    session = requests.session()
    session.get('http://wbsl.gov.in/eArchive.action')
    while ids:
        el = ids[0]
        book = Book('./pdf', session, str(el))
        book.get_info_from_meta()
        book.generate_imgs_names()
        book.async_download(100)
        book.make_pdf()
        ids.remove(ids[0])
        json.dump(ids, open('progress.json', 'w'))
