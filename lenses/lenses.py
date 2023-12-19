import base64
import os
import io

from flask import Flask, redirect, render_template, request, url_for

from backend import Backend
from error_codes import BackendErrors

backend = Backend(os.environ["CLICKHOUSE_HOST"] if "CLICKHOUSE_HOST" in os.environ else  "localhost")

app = Flask(__name__)


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        url = url_for(
            "result",
            sensors=request.form["sensors"],
            start=request.form["start"],
            end_or_duration=request.form["end_or_dur"],
        )
        return redirect(url)
    return render_template("index.html")


@app.route("/result")
def result():
    backend_response = backend.get_result(
        request.args.get("sensors"),
        request.args.get("start"),
        request.args.get("end_or_duration"),
    )

    if isinstance(backend_response, io.BytesIO):
        return render_template("result.html", chart=base64.b64encode(backend_response.getvalue()).decode("utf-8"))
    elif backend_response == BackendErrors.WRONG_SENSOR_LIST:
        pass
    elif backend_response == BackendErrors.WRONG_START_TIMESTAMP:
        pass
    elif backend_response == BackendErrors.WRONG_END_TIMESTAMP:
        pass
    elif backend_response == BackendErrors.NO_DATA:
        pass
