import uuid
from flask import Flask, Response, request, render_template
from gensim.models import Word2Vec

app = Flask(__name__)

game_env = []
model = Word2Vec.load('./models/word2vec-KCC150.model')

@app.route('/', methods=['GET'])
def index():
    return render_template('create_game.html')


@app.route('/', methods=['POST'])
def create_game():
    data = request.get_json()
    seed = data['seed']
    creator = data['creator']

    try:
        similars = model.wv.most_similar(positive=[seed], topn=500)
        key = add_game_seed(seed, creator, similars)
    
    except:
        return Response(
            f"{seed}: 모르는 단어입니다.",
            status=400
        )

    return {"key": key}


def add_game_seed(seed, creator, similars):
    global game_env

    key = str(uuid.uuid4())
    key = key.replace('-', '')

    game_env.append({
        "key": key,
        "seed": seed,
        "creator": creator,
        "similars": similars
    })

    return key


@app.route('/game/<key>', methods=['GET'])
def game_page(key):
    return render_template('main.html')
    

@app.route('/similars/<key>', methods=['GET'])
def get_similars(key):
    global game_env

    for data in game_env:
        if data['key'] == key:
            return data['similars']

    return Response(status=400)


@app.route('/check/<key>/<word>')
def check_similarity(key, word):
    seed = None
    for data in game_env:
        if data.key == key:
            seed = data.seed

    if seed is None:
        return Response(
            {"message": "존재하지 않는 게임입니다."},
            status=404
        )

    if seed == word:
        return {
            "success": True,
            "isAnswer": True,
            "similarity": '100.0'
        }

    try:
        similarity = model.wv.similarity(seed, word) * 100

    except KeyError:
        return {
            "success": False,
            "isAnswer": False
        }

    return {
        "success": True,
        "isAnswer": False,
        "similarity": str(similarity)
    }


app.run(host='127.0.0.1', port=8080)
