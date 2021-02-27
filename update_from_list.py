import json

import requests
from bs4 import BeautifulSoup

from main import Book

url = 'http://wbsl.gov.in/ajaxSearch.action?sEcho=2&iColumns=2&sColumns=,&iDisplayStart=0&iDisplayLength=10&bRegex_0=false&bSearchable_0=true&bSortable_0=true&bRegex_1=false&bSearchable_1=true&bSortable_1=true&sSearch={name}&bRegex=false&iSortCol_0=0&sSortDir_0=asc&iSortingCols=1'
if __name__ == '__main__':
    session = requests.session()
    session.get('http://wbsl.gov.in/eArchive.action')
    try:
        ids = json.load(open('progress.json','r'))
    except:
        ids = [x for x in range(1, 22001)]

    for el in open('filtered list.txt').read().split('\n'):
        id_n='error'
        rs = session.get(url.format(name=el.replace(' ', '%20')))

        for le in rs.json()['data']:
            id_n = int(le['bookid'])
            if id_n in ids:
                book = Book('./pdf', session, str(id_n))
                book.get_info_from_meta()
                book.generate_imgs_names()
                book.async_download(100)
                book.make_pdf()
                ids.remove(id_n)
            else:
                id_n = str(id_n)+' skip'
        json.dump(ids,open('progress.json','w'))
        if id_n == 'error':
            open('errors.txt','a').write('\n'+el)
        print(el,'id:',id_n)