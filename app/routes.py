"""API routes for the DevOps LLM application."""

import logging

from flask import Blueprint, jsonify, render_template, request

from app.database import get_all_prompts, get_categories, get_prompt_by_id
from app.middleware import rate_limit

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Serve the main web interface."""
    prompts = get_all_prompts()
    categories = get_categories()
    return render_template("index.html", prompts=prompts, categories=categories)


@main_bp.route("/api/prompts", methods=["GET"])
def list_prompts():
    """GET /api/prompts - Retrieve all available prompts."""
    prompts = get_all_prompts()
    return jsonify({"status": "success", "count": len(prompts), "data": prompts})


@main_bp.route("/api/prompts/<int:prompt_id>", methods=["GET"])
def get_prompt(prompt_id):
    """GET /api/prompts/<id> - Retrieve a specific prompt."""
    prompt = get_prompt_by_id(prompt_id)
    if not prompt:
        return jsonify({"error": "Prompt not found", "id": prompt_id}), 404
    return jsonify({"status": "success", "data": {"id": prompt_id, "prompt": prompt}})


@main_bp.route("/api/generate", methods=["POST"])
@rate_limit
def generate():
    """POST /api/generate - Generate LLM response for a given prompt ID."""
    from flask import current_app

    # Validate request body
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()
    prompt_id = data.get("id")

    if prompt_id is None:
        return jsonify({"error": "Missing required field: 'id'"}), 400

    try:
        prompt_id = int(prompt_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Field 'id' must be a valid integer"}), 400

    # Fetch prompt from database
    prompt_text = get_prompt_by_id(prompt_id)
    if not prompt_text:
        return jsonify({"error": f"Prompt with id={prompt_id} not found"}), 404

    # Generate LLM response
    try:
        llm_service = current_app.config.get("LLM_SERVICE")
        if not llm_service:
            return jsonify({"error": "LLM service not configured"}), 503

        result = llm_service.generate_response(
            prompt=prompt_text,
            system_prompt="You are a knowledgeable assistant. Provide clear, well-structured, and insightful responses.",
        )

        return jsonify(
            {
                "status": "success",
                "data": {
                    "prompt_id": prompt_id,
                    "response": result["content"],
                    "model": result["model"],
                    "usage": result["usage"],
                    "latency_seconds": result["latency_seconds"],
                },
            }
        )

    except Exception as e:
        logger.error(f"LLM generation failed for prompt_id={prompt_id}: {e}")
        return jsonify({"error": "Failed to generate response", "message": str(e)}), 502


@main_bp.route("/health", methods=["GET"])
def health_check():
    """GET /health - Application health check endpoint."""
    from flask import current_app

    from app.database import get_db_connection

    health = {"status": "healthy", "version": "1.0.0", "checks": {}}

    # Database check
    try:
        with get_db_connection() as conn:
            conn.execute("SELECT 1")
        health["checks"]["database"] = "connected"
    except Exception as e:
        health["status"] = "degraded"
        health["checks"]["database"] = f"error: {str(e)}"

    # LLM service check
    llm_service = current_app.config.get("LLM_SERVICE")
    health["checks"]["llm_service"] = "configured" if llm_service else "not configured"

    status_code = 200 if health["status"] == "healthy" else 503
    return jsonify(health), status_code


@main_bp.route("/api/categories", methods=["GET"])
def list_categories():
    """GET /api/categories - List all prompt categories."""
    categories = get_categories()
    return jsonify({"status": "success", "data": categories})


@main_bp.route("/generate-from-text", methods=["POST"])
def generate_from_text():
    """POST /generate-from-text - Generate LLM response from raw prompt text.
    Used by AWS Lambda for the S3-triggered event-driven pipeline.
    """
    from flask import current_app

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json(silent=True) or {}
    prompt_text = (data.get("prompt") or "").strip()

    if not prompt_text:
        return jsonify({"error": "Missing required field: 'prompt'"}), 400

    try:
        llm_service = current_app.config.get("LLM_SERVICE")
        if not llm_service:
            return jsonify({"error": "LLM service not configured"}), 503

        result = llm_service.generate_response(
            prompt=prompt_text,
            system_prompt="You are a knowledgeable assistant. Provide clear, well-structured, and insightful responses.",
        )

        # Return both 'result' (for Lambda compatibility) and 'data' (full info)
        return jsonify(
            {
                "status": "success",
                "result": result["content"],
                "data": {
                    "response": result["content"],
                    "model": result["model"],
                    "usage": result["usage"],
                    "latency_seconds": result["latency_seconds"],
                },
            }
        )

    except Exception as e:
        logger.error(f"LLM generation from text failed: {e}")
        return jsonify({"error": "Failed to generate response", "message": str(e)}), 502
