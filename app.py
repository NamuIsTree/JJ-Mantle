from flask import Flask, render_template
from gensim.models import Word2Vec

app = Flask(__name__)

seed = ''
history = []
list_len = 0

model = Word2Vec.load('./models/word2vec-KCC150.model')


@app.route('/', methods=['GET'])
def index():
    return render_template('main.html')


@app.route('/seed/<word>')
def set_seed(word):
    global seed
    global history
    global list_len

    history = []
    list_len = 0
    seed = word

    return {
        "success": True
    }


@app.route('/check/<word>')
def check_similarity(word):
    if seed == word:
        return {
            "success": True,
            "isAnswer": True,
            "similarity": '100.0',
            "history": build_history()
        }

    try:
        similarity = model.wv.similarity(seed, word) * 100

    except KeyError:
        return {
            "success": False
        }

    add_data(word, similarity)

    return {
        "success": True,
        "isAnswer": False,
        "similarity": str(similarity),
        "history": build_history()
    }


def add_data(word, similarity):
    global history
    global list_len

    for data in history:
        if data[2] == word:
            return

    count = list_len + 1
    data = (similarity, count, word)

    if list_len == 0:
        history.append(data)
    else:
        found = False

        for i in range(list_len):
            if data > history[i]:
                history.insert(i, data)
                found = True
                break

        if found is False:
            history.append(data)

    list_len = list_len + 1


def build_history():
    text = ''
    for data in history:
        text = f"{text}#{data[1]}\t{data[2]}\t{data[0]}\n"

    return text


app.run(host='127.0.0.1', port=8080)
