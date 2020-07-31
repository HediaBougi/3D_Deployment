from flask import Flask, request, jsonify
from tools.dictionaryValue import dictionaryValue
import time

app = Flask(__name__)


@app.route('/getnparray/', methods=['GET'])
def getnparray():
    start = time.time()
    address = request.args.get("address", None)

    # For debugging
    print(f"got address {address}")

    result = {}
    if not address:
        result["ERROR"] = "Please enter a valid address"
        return "<h1>Enter valid address!!</h1>"
    else:
        result = dictionaryValue(address)

    end = time.time()
    print("--- Run Time : %s seconds ---" % (end - start))
    return jsonify(result)


@app.route('/')
def route():
    return "<h1>Loading...API Documentation !!</h1>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
