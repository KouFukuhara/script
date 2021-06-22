# ISBNを基に国会図書館のデータベースから書籍情報を取得する

from bs4 import BeautifulSoup
import time
import urllib.request
from collections import defaultdict


def get_book_info_for_ndl(isbn_str):
    """引数に渡された ISBN から書籍情報を国会図書館のデータベースから検索し､情報が含まれている箇所をリスト形式で返す
    データが取得できなかった場合はNoneを返す
    """

    book_info_list = []
    search_isbn_url = f'http://iss.ndl.go.jp/books?search_mode=advanced&rft.isbn={isbn_str}'

    # ISBN の検索結果
    response = urllib.request.urlopen(search_isbn_url)

    if response.status != 200:
        return None
    
    source = response.read() 
    soup = BeautifulSoup(source, 'html.parser')
    book_name_data = soup.find_all(class_ = 'item_summarywrapper')

    if book_name_data == []:
        return None

    target_url = book_name_data[0].a.attrs['href']

    if target_url == []:
        return None

    # 書籍の詳細情報
    response = urllib.request.urlopen(target_url)

    if response.status != 200:
        return None

    source = response.read() 
    soup = BeautifulSoup(source, 'html.parser')
    contents = soup.find_all(id = 'itemcontent')
    contents = contents[0].contents[7]
    contents = contents

    for c in contents:

        if c != '\n':

            data_tmp = c.text
            data_tmp = data_tmp.replace('\n', '')
            book_info_list.append(data_tmp)

    time.sleep(1)
    return book_info_list


def parse_book_data(book_info):

    book_info_dict = {}
    book_info_dict = defaultdict(set)

    for d in book_info:
        ret = book_info_string_format(d)
        if ret != None:
            book_info_dict[ret[0]].add(ret[1])

    return book_info_dict


def book_info_string_format(string):

    info_type_list = [ 'タイトル', '著者', '著者標目', '出版社', '出版年月日等', '大きさ、容量等', \
                        '    注記        ', 'ISBN', 'NACSIS-CATレコード', \
                        '別タイトル', '出版年(W3CDTF)', '件名（キーワード）', 'NDLC', 'NDC（10版）', \
                        'NDC（9版）', 'NDC(8版)', '対象利用者', '資料の種別', '言語（ISO639-2形式）']

    for type in info_type_list:

        if string.startswith(type):
            tmp = string.replace(type, '')

            if tmp.startswith('標目'):
                tmp = string.replace('著者標目', '')
                return ('著者標目', tmp)

            if type == '    注記        ':
                return ('注記', string)

            return (type, string)

    return None


def main():

    with open('isbnlist.txt', 'r', encoding = 'utf-8') as f:
        isbn_data = f.readlines()

    for isbn in isbn_data:
        book_info = get_book_info_for_ndl(isbn)

        if book_info == None:
            print(f'{isbn} is no hit.')
            continue

        book_info_dict = parse_book_data(book_info)

        print('---------------------------------------------')
        for k, v in book_info_dict.items():
            
            print(f'■{k}')
            for i in v:
                # MEMO: 注記のデータの場合は場合分けして対応しないと文字が揃わない
                i = i.replace(k ,'')
                print(f'    {i}')

        print('---------------------------------------------')
        print()


if __name__ == "__main__":
    main()