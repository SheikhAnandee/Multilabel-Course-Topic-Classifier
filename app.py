from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request
import os
from gradio_client import Client

app = Flask(__name__)

client = Client(
    "SheikhAnandee/multilabel-ubemy-course-classifier",
    token=os.environ.get("HF_TOKEN")
)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        input_text = request.form['text']
        output = predict_topics(input_text)
        confidence_list = output['confidences']
        labels = [elem['label'] for elem in confidence_list if elem['confidence'] >= 0.3]
        label_text = ", ".join(labels)
        return render_template("result.html", input_text=input_text, output_text=label_text)
    else:
        return render_template("index.html")

def predict_topics(input_text):
    result = client.predict(
        description=input_text,
        api_name="/classify_course_topic",
    )
    return result

if __name__ == "__main__":
    app.run(debug=True)