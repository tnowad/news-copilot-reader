from flask import Blueprint, request, jsonify
from app.extensions import cache
from http import HTTPStatus

generation_bp = Blueprint("generation", __name__)


@cache.memoize(timeout=300)
def generate_text_cached(prompt, max_length=100, temperature=0.9, top_k=20):
    from app.services.generation.text_generation import text_generation_pipeline

    top_p = 0.9
    data = text_generation_pipeline(
        prompt, max_length=max_length, temperature=temperature, top_k=top_k, top_p=top_p
    )

    return data[0].get("generated_text")  # type: ignore


@generation_bp.route("/generate-text", methods=["POST"])
def generate_text():
    try:
        prompt = request.get_json().get("prompt")
        max_length = request.get_json().get("maxLength", 10)
        temperature = request.get_json().get("temperature", 0.1)
        top_k = request.get_json().get("topK", 20)

        generated_text = generate_text_cached(prompt, max_length, temperature, top_k)

        response_data = {
            "statusCode": HTTPStatus.OK,
            "message": "Text generated successfully",
            "data": {
                "generatedText": generated_text,
            },
        }

        return jsonify(response_data), HTTPStatus.OK

    except Exception as e:
        return (
            jsonify(
                {
                    "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR,
                    "message": "Internal Server Error",
                    "error": str(e),
                }
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
