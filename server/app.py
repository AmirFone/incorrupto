from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

# from test.tanim_module import get_fact_or_opinion, get_toxicity, detect_implicit_hate
from gemini import evaluate, getArticleInfo, getVideoInfo
from huggingFaceModels import analyze_text
from dalle3 import generate_image
from db import authUser, addUser, addArticle, getArticles

# from test.amir import analyze_text
# from test.amir_dalle_3 import generate_image

app = Flask(__name__)
CORS(app)


@app.route("/submit-article-link", methods=["POST"])
def handle_article_link():
    try:
        data = request.json
        article_link = data.get("articleLink")

        # Fetch the HTML content of the article
        response = requests.get(article_link)

        # Check if the request was successful
        if response.status_code == 200:
            try:
                # Parse the HTML content
                soup = BeautifulSoup(response.text, "html.parser")
                articleInfo = getArticleInfo(soup.text)
            except Exception as e:
                return jsonify({"error": f"Failed to parse article content: {e}"}), 500

            try:
                cleaned_article = evaluate(
                    "Your evaluation call for cleaned_article here"
                )
            except Exception as e:
                return jsonify({"error": f"Failed during article cleaning: {e}"}), 500

            try:
                article_summary = evaluate(
                    "Your evaluation call for article_summary here"
                )
            except Exception as e:
                return (
                    jsonify({"error": f"Failed during article summarization: {e}"}),
                    500,
                )

            try:
                important_people = evaluate(
                    "Your evaluation call for important_people here"
                )
            except Exception as e:
                return (
                    jsonify({"error": f"Failed to identify important people: {e}"}),
                    500,
                )

            try:
                # dalle_image_link = generate_image(article_summary)
                1 == 1
            except Exception as e:
                return (
                    jsonify({"error": f"Failed to generate image with DALL-E: {e}"}),
                    500,
                )

            try:
                analytics_metrics = analyze_text(cleaned_article)
            except Exception as e:
                return jsonify({"error": f"Failed during text analysis: {e}"}), 500

            # If all operations are successful, return the combined results
            return jsonify(
                {
                    "articleInfo": articleInfo,
                    "cleanedArticleText": article_summary,
                    "important_people": important_people,
                    "analytics_metrics": analytics_metrics,  # converting a python dict
                }
            )
        else:
            return (
                jsonify(
                    {
                        "message": "Failed to fetch page",
                        "error": "Could not retrieve the page from the "
                        "provided link",
                    }
                ),
                400,
            )

    except Exception as e:
        # Catch any other exception that was not handled
        return (
            jsonify(
                {
                    "error": f"An unexpected error occurred: {e}",
                    "dalle_image_link": dalle_image_link,
                    "analytics_metrics": json.dumps(
                        analytics_metrics
                    ),  # converting a python dict
                }
            ),
            500,
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


@app.route("/create-user", methods=["POST"])
def create_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    user = addUser(
        {
            "cf1:name": name,
            "cf1:email": email,
            "cf1:password": password,
        },
    )
    return jsonify(
        {
            "message": "User created successfully",
        }
    )


@app.route("/get-user", methods=["GET"])
def get_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = authUser(email, password)
    if authUser:
        return jsonify(
            {
                "user": user,
            }
        )
    else:
        return (
            jsonify(
                {
                    "message": "Failed to authenticate user",
                    "error": "Could not authenticate user",
                }
            ),
            400,
        )


@app.route("/create-article", methods=["POST"])
def create_article():
    data = request.json
    userID = data.get("userID")
    url = data.get("url")
    data = data.get("data")
    article = addArticle(
        {
            "cf1:userID": userID,
            "cf1:url": url,
            "cf1:data": data,
        },
    )
    return jsonify(
        {
            "message": "Article created successfully",
        }
    )


@app.route("/get-articles", methods=["GET"])
def get_articles():
    data = request.json
    userID = data.get("userID")

    articles = getArticles(userID)
    if authUser:
        return jsonify(
            {
                "articles": articles,
            }
        )
    else:
        return (
            jsonify(
                {
                    "message": "Failed to get articles",
                    "error": "No articles found",
                }
            ),
            400,
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
