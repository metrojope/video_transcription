from flask import Flask, jsonify

print("Importing Flask...")

app = Flask(__name__)

print("Creating Flask app...")

@app.route('/examples', methods=['GET'])
def get_examples():
    print("Handling /examples request...")
    examples = [
        "Example 1: Your example text here.",
        "Example 2: Your example text here.",
        "Example 3: Your example text here."
    ]
    return jsonify(examples)

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(host='0.0.0.0', debug=True, port=8080)
    print("Flask server is running.")