from flask_cors import CORS
from flask import Flask, jsonify
from app.utils.response_util import api_response

def create_app():
    # Initialize Flask app
    app = Flask(__name__)

    # Enable CORS for all domains on all routes
    CORS(app, resources={r"/*": {"origins": "*"}})

    from app.controllers.llm_controller import llm_controller
    app.register_blueprint(llm_controller, url_prefix="/api/llm")

    from app.controllers.deepgram_controller import deepgram_controller
    app.register_blueprint(deepgram_controller, url_prefix="/api/deepgram")

    from app.controllers.s3_controller import s3_controller
    app.register_blueprint(s3_controller, url_prefix="/api/s3")

    from app.controllers.record_controller import record_controller
    app.register_blueprint(record_controller, url_prefix="/api/record")


    @app.route("/")
    def root():
        return api_response(200,'This is DEV Test API!')


    @app.route("/health")
    def health():
        return api_response(200,'Health is OK!')

    @app.errorhandler(404)
    def page_not_found(error):
        print(error)
        return api_response(404,'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.')

    return app
