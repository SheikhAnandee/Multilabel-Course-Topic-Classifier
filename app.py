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

LABEL_THRESHOLD = 0.15


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_text = request.form["text"]
        output = predict_topics(input_text)

        # Debug: see the raw model output in your console.
        print("RAW MODEL OUTPUT:", output)

        labels = extract_labels(output)
        label_text = ", ".join(labels) if labels else "No confident topic found"

        return render_template(
            "result.html", input_text=input_text, output_text=label_text
        )
    else:
        return render_template("index.html")


def predict_topics(input_text):
    result = client.predict(
        description=input_text,
        api_name="/classify_course_topic",
    )
    return result


def extract_labels(output):
    """
    Extract multiple labels from the model output using a simple absolute
    threshold. Since the model produces independent sigmoid confidences per
    label (verified: they don't sum to 1.0), any label above LABEL_THRESHOLD
    is a legitimately separate prediction -- no relative/softmax-style
    comparison between labels is needed.
    """
    confidence_list = output.get("confidences", [])
    if not confidence_list:
        return []

    labels = [
        elem["label"]
        for elem in confidence_list
        if elem["confidence"] >= LABEL_THRESHOLD
    ]
    return labels


if __name__ == "__main__":
    app.run(debug=True)