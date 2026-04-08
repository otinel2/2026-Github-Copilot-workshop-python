"""API routes for bootstrap health checks."""

from flask import Blueprint, jsonify


api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health():
    return jsonify({"status": "ok"})
