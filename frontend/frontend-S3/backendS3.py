from flask import Flask, request, jsonify
import boto3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Your bucket name
BUCKET_NAME = "s3copyofthedatapayment"    # change the bucket name 

# Initialize boto3 S3 client (it will use IAM role attached to EC2)
s3 = boto3.client("s3")

@app.route('/')
def home():
    return "Flask S3 Copy API is running!"

# Upload file to S3
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)

    try:
        s3.upload_fileobj(file, BUCKET_NAME, filename)
        return jsonify({"message": f"File '{filename}' uploaded successfully to {BUCKET_NAME}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Copy object inside the same bucket (source → destination)
@app.route('/copy', methods=['POST'])
def copy_file():
    data = request.get_json()
    source = data.get("source")
    destination = data.get("destination")

    if not source or not destination:
        return jsonify({"error": "Source and Destination keys required"}), 400

    try:
        copy_source = {"Bucket": BUCKET_NAME, "Key": source}
        s3.copy_object(CopySource=copy_source, Bucket=BUCKET_NAME, Key=destination)
        return jsonify({"message": f"Copied {source} → {destination}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Runs on port 5000, accessible via your LB
    app.run(host="0.0.0.0", port=5000)
