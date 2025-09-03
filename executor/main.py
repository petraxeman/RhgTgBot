from quart import Quart, request
import processor


app = Quart(__name__)


def build_app():
    return app


@app.route("/execute", methods = ["POST"])
async def install():
    return {"response": processor.process(request.json.get("instruction", {}))}
