from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
from test.tanim_module import get_fact_or_opinion, get_toxicity, detect_implicit_hate
from gemini import evaluate, getArticleInfo, getVideoInfo

app = Flask(__name__)
CORS(app)


@app.route("/submit-article-link", methods=["POST"])
def handle_article_link():
    data = request.json
    article_link = data.get("articleLink")

    # Fetch the HTML content of the article
    response = requests.get(article_link)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")
        articleInfo = getArticleInfo(soup.text)
        return jsonify(
            {
                "articleInfo": articleInfo,
            }
        )
    else:
        return (
            jsonify(
                {
                    "message": "Failed to fetch page",
                    "error": "Could not retrieve the page from the provided link",
                }
            ),
            400,
        )


@app.route("/submit-video-link", methods=["POST"])
def handle_video_link():
    data = request.json
    video_link = data.get("videoLink")
    videoInfo = getVideoInfo(video_link)
    return jsonify(
        {
            "videoInfo": videoInfo,
        }
    )


@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/gemini", methods=["GET", "POST"])
def gemini():
    return evaluate(request.json["prompt"])


@app.route("/analyze/implicit-hate", methods=["POST"])
def implicit_hate_route():
    text = request.json.get("text", "")
    result = detect_implicit_hate(text)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
