import re
from janome.tokenizer import Tokenizer
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import random, datetime
import multiprocessing, time, io
from multiprocessing import shared_memory
import matplotlib.pyplot as plt
from PIL import Image

trans = Translator()

week = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']

process = None
shm = None

tokenizer = Tokenizer()

def greeting(*_):
    return "何だてめえ"

def address(*_):
    #print("call address")
    r = requests.get("https://get.geojs.io/v1/ip/geo.json")
    #print("geted request")
    #print(r.text)
    data = r.json()
    #print("generated json")
    """print(data['latitude'])
    print(data['longitude'])
    print(data['country'])
    print(data['region'])
    print(data['city'])"""
    try:
        return f"""{
                trans.translate(data['country'], src='en', dest='ja').text
                }の{
                trans.translate(data['region'], src='en', dest='ja').text
                }の{
                trans.translate(data['city'], src='en', dest='ja').text
                }だが何だ？"""
    except KeyError:
        return error()

def now(*_):
    n = datetime.datetime.now()
    return f"{n.year}年{n.month}月{n.day}日の{n.hour}時{n.minute}分だが何だ?"

def today(*_):
    n = datetime.datetime.today()
    return f"{n.year}年{n.month}月{n.day}日だが何だ?"

def day(*_):
    n = datetime.datetime.today()
    return f"{week[n.weekday()]}だが何だ？"

def meaning(ch, _):
    #print("called meaning")
    try:
        res = requests.get(f"https://kotobank.jp/word/{ch[:-2]}").text
        soup = BeautifulSoup(res, "html.parser")
        description = soup.find('section', class_='description')
        #print(type(description), str(description))
        tag_re = """<("[^"]*"|'[^']*'|[^'">])*>"""
        mea = re.sub(tag_re, '', str(description).replace(' ', ''))
        if mea == None: return "何も見つかんなかったぞくそが"
        return f"{mea}だって。※コトバンク情報"
    except Exception as e:
        print(e)
        return error()

def mapping(*_):
    global shm, process
    shm = shared_memory.SharedMemory()
    shm[0] = True
    shm[1] = []
    def _tmp():
        while True:
            if process:
                r = requests.get("https://get.geojs.io/v1/ip/geo.json").json()
                shm[1].append((r["latitude"], r["longitude"]))
                time.sleep(1)
    process = multiprocessing.Process(target=_tmp)
    process.start()

def f_mapping(*_):
    global shm, process
    shm[0] = False
    _, ax = plt.subplots()
    ax.plot([i[0] for i in shm[1]], [i[1] for i in shm[1]])
    plt.show()
    shm.close()
    shm.unlink()
    shm = None
    process.terminate()
    process = None

def finish(*_):
    #print("called finish")
    return None

def error():
    return random.choice(["あんだって？", "やべえエラー出た。"])

"""rq_fun = {
    "オワリニシテ":finish,
    "ネエシズカニ":greeting,
    "ココドコ":address,
    "イマナンジ":now,
    "キョウナンニチ":today,
    "キョウナンヨウビ":day,
    ".+トハ":meaning
}"""

rq_fun = [
    ("オワリニシテ", finish),
    ("ネエシズカニ", greeting),
    ("ココドコ", address),
    ("イマナンジ", now),
    ("キョウナンニチ", today),
    ("キョウナンヨウビ", day),
    (".+トハ", meaning)
]

def main(rq):
    try:
        req = ""
        for token in tokenizer.tokenize(rq): req += token.reading
        req = req.replace("*", "")
        print(req)
        for word, func in rq_fun:
            if re.match(word, req):
                return func(rq, req)
        print("not key")
        return error()
        #return rq_fun[m]()
    except:
        return error()

if __name__ == "__main__":
    print(main("皆とは"))