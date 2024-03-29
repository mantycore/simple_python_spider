# библиотеки
from queue import Queue # встроенная, для структуры данных "очередь"
import urllib.request # встроенная, для http-запросов
from bs4 import BeautifulSoup # для работы со структурой html
import hyperlink # для продвинутой работы с uri

start = hyperlink.URL.from_text("https://www.anima-incognita.org/") 

links_queue = Queue() # очередь, в которой будут храниться уже известные, но еще
links_queue.put(start) # не обработанные адреса

links_processed = set() # множество, в котором будут храниться все известные адреса
links_processed.add(start.to_text())

# повторим тысячу раз:
for i in range(1000):
    url = links_queue.get() # возьмем из головы очереди новый адрес
    print(url.to_iri().to_text()) # преобразуем его к IRI, представлению адреса с поддержкой юникода
    try:
        # а теперь к URI, представлению в виде ASCII, где все не входящие
        # в ASCII символы преобразуются (разным образом, в зависимости от части адреса:
        # IRI: "https://шу.рф/лонли/локли" >
        # URI: 'https://xn--s1aj.xn--p1ai/%D0%BB%D0%BE%D0%BD%D0%BB%D0%B8/%D0%BB%D0%BE%D0%BA%D0%BB%D0%B8'

        # и выполним http-запрос GET к этому адресу, с таймаутом в 10 секунд.
        # если случится таймаут, то будет выброшено исключение (событие ошибки);
        # поскольку мы сейчас находимся в блоке try, то исключение будет поймано
        # в соотвествующем блоке catch ниже.
        contents = urllib.request.urlopen(url.to_uri().to_text(), timeout=10).read()
        
        # возьмем содержимое полученного ответа и распарсим его при
        # помощи BeautifulSoup, который, в свою очередь, использует парсер lxml
        soup = BeautifulSoup(contents, "lxml")

        # найдем в полученной структуре html все теги a,
        # у которых присутствует аттрибут href (гиперссылки)
        # а затем для каждой ссылки...
        for link in soup.find_all('a', href=True):
            # разрешим полученную гиперссылку относительно исходной.
            # это значит, что если ссылка относительная (не содержит имени протокола и,
            # возможно, нескольких последующих частей), то недостающие части будут взяты
            # из исходной ссылки.
            # Затем исключим из нее часть под названием fragment (хвостик, идущий
            # после символа #, который означает адрес внутри одного и того же документа,
            # например раздел с подзаголовком) и нормализуем, то есть приведем к полностью
            # стандартному представлению.
            link_url = url.click(link['href']).replace(fragment='').normalize()
            # если эту ссылку мы еще не видели, то...
            if not link_url.to_text() in links_processed:
                # отметим, что  вот мы ее увидели
                links_processed.add(link_url.to_text())
                # и добавим в хвост очереди
                links_queue.put(link_url)
    except:
        print("timeout")
        pass
