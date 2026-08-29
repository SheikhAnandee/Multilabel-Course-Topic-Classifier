# Multilabel-Course-Topic-Classifier
A text classification model covering data collection, preprocessing, model training, and deployment.

The model can classify Udemy courses into **66 different topics** based on their description.
The keys of `deployment\topic_types_encoded.json` show the full list of course topics.

## Data Collection

Data was collected by scraping Udemy course listings (title, URL, description, topic,  topic list) into `course_details.csv`.

In total, I scraped **11,057** course details.

## Data Preprocessing

Initially there were **2,436 different topics/subtopics** in the raw dataset. After some analysis, I found the vast majority of them were rare (appearing in only a handful of courses), so I removed those, leaving **66 topics**. After that, I removed entries left with no remaining topic, resulting in **11,055 samples**.

## Model Training

Fine-tuned a `distilroberta-base` model from HuggingFace Transformers using **Fastai** and **Blurr** for multi-label classification.

The model takes a course description as input and predicts the relevant course topics.

The model training notebook can be viewed [here](https://github.com/SheikhAnandee/Multilabel-Course-Topic-Classifier/tree/a3c48d34f6c1cf4d9234fccd7f1c8df8403498cc/notebooks).

On a held-out validation split, the model achieved an F1 score (micro) of 0.52 and F1 score (macro) of 0.10.

## Model Compression and ONNX Inference

The trained PyTorch model was converted to **ONNX** for more efficient inference.

The ONNX model was then compressed using **dynamic INT8 quantization**, reducing the model size and making it more suitable for CPU-based inference.

The ONNX conversion, quantization, and inference notebook can be viewed [here](https://github.com/SheikhAnandee/Multilabel-Course-Topic-Classifier/tree/a3c48d34f6c1cf4d9234fccd7f1c8df8403498cc/notebooks).

## Model Deployment

The compressed model is deployed as a **Gradio application on HuggingFace Spaces**.

The deployment implementation can be found in the `deployment` folder or [here](https://huggingface.co/spaces/SheikhAnandee/multilabel-ubemy-course-classifier).

The deployment uses:

- `Gradio` for the user interface
- `ONNX Runtime` for model inference
- `distilroberta-base` tokenizer for text preprocessing
- Quantized ONNX model for course-topic prediction
- `topic_types_encoded.json` for mapping predicted labels to topic names

<p align="center">
  <img src="src/Screenshot (651).png" width="900">
</p> 

## Wed Development

Deployed a Flask app that takes a course description and outputs its predicted topics. Check the `flask` branch. The website is live [here](https://multilabel-course-topic-classifier-2.onrender.com/).

<p align="center">
  <img src="src/Screenshot 2026-08-29 201842.png" width="900">
   <br>
  <em>Input form — paste a course description</em>
</p> 

<p align="center">
  <img src="src/Screenshot_2026-08-29_201842.png" style="max-width: 100%; height: auto;" alt="Course description input form">
<br>
<em>Result — multiple predicted topics (Development, Python, IT & Software, Data Science, Programming Languages)</em>
</p>
