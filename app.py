# from dotenv import load_dotenv
# load_dotenv()

# from flask import Flask, render_template, request
# import os
# from gradio_client import Client

# app = Flask(__name__)

# client = Client(
#     "SheikhAnandee/multilabel-ubemy-course-classifier",
#     token=os.environ.get("HF_TOKEN")
# )

# @app.route("/", methods=['GET', 'POST'])
# def index():
#     if request.method == "POST":
#         input_text = request.form['text']
#         output = predict_topics(input_text)
#         confidence_list = output['confidences']
#         labels = [elem['label'] for elem in confidence_list if elem['confidence'] >= 0.5]
#         label_text = ", ".join(labels)
#         return render_template("result.html", input_text=input_text, output_text=label_text)
#     else:
#         return render_template("index.html")

# def predict_topics(input_text):
#     result = client.predict(
#         description=input_text,
#         api_name="/classify_course_topic",
#     )
#     return result

# if __name__ == "__main__":
#     app.run(debug=True)
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

# Minimum confidence a label needs to be considered a real candidate at all.
MIN_ABSOLUTE_THRESHOLD = 0.30

# A label is kept if its confidence is within this fraction of the top label's score.
# e.g. 0.6 means: keep any label with confidence >= 60% of the highest confidence.
RELATIVE_THRESHOLD_RATIO = 0.6


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
    Extract multiple labels from the model output.

    NOTE: If the model was trained with a softmax output layer instead of
    independent sigmoids, confidences across labels will sum to ~1.0, which
    makes true multi-label prediction impossible at the model level (only
    one label can realistically clear a fixed 0.5 threshold). This function
    uses a relative threshold as a practical workaround, but the real fix is
    retraining the model with a sigmoid + BCEWithLogitsLoss head for genuine
    multi-label output.
    """
    confidence_list = output.get("confidences", [])
    if not confidence_list:
        return []

    max_conf = max(elem["confidence"] for elem in confidence_list)
    dynamic_threshold = max(MIN_ABSOLUTE_THRESHOLD, max_conf * RELATIVE_THRESHOLD_RATIO)

    labels = [
        elem["label"]
        for elem in confidence_list
        if elem["confidence"] >= dynamic_threshold
    ]
    return labels


if __name__ == "__main__":
    app.run(debug=True)