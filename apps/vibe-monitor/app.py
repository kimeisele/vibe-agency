#!/usr/bin/env python3
"""
Vibe Monitor - System Status Dashboard
========================================

A web dashboard that visualizes vibe-agency system status
by consuming ./bin/vibe status --json output.

This is ARCH-019: The first native artifact built by the system itself.

Routes:
  GET /           - Serve the dashboard HTML
  GET /api/status - Execute vibe status and return JSON

Usage:
  python3 app.py
  # Then visit: http://localhost:5000
"""

import json
import logging
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template
from flask.logging import default_handler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS for API endpoint
@app.after_request
def add_cors_headers(response):
    """Add CORS headers to all responses."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


def get_repo_root():
    """Get the repository root (2 levels up from this file)."""
    return Path(__file__).parent.parent.parent


@app.route('/')
def index():
    """Serve the dashboard HTML."""
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """
    Execute './bin/vibe status --json' and return the parsed JSON.

    Returns:
        JSON response with system status

    Error handling:
        - Subprocess errors: Return 500 with error details
        - JSON parse errors: Return 500 with error details
    """
    try:
        # Get repository root
        repo_root = get_repo_root()
        vibe_cmd = repo_root / 'bin' / 'vibe'

        # Check if vibe command exists
        if not vibe_cmd.exists():
            logger.error(f"vibe command not found: {vibe_cmd}")
            return jsonify({
                'error': 'vibe command not found',
                'details': f'Expected at: {vibe_cmd}'
            }), 500

        # Execute: ./bin/vibe status --json
        logger.info(f"Executing: {vibe_cmd} status --json")
        result = subprocess.run(
            ['python3', str(vibe_cmd), 'status', '--json'],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10
        )

        # Check for subprocess errors
        if result.returncode != 0:
            logger.error(f"vibe command failed with code {result.returncode}")
            logger.error(f"stderr: {result.stderr}")
            return jsonify({
                'error': 'vibe command execution failed',
                'return_code': result.returncode,
                'stderr': result.stderr,
                'stdout': result.stdout
            }), 500

        # Parse JSON output
        try:
            status_data = json.loads(result.stdout)
            logger.info(f"Successfully parsed vibe status JSON")
            return jsonify(status_data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"stdout: {result.stdout}")
            return jsonify({
                'error': 'Failed to parse vibe status JSON',
                'details': str(e),
                'raw_output': result.stdout
            }), 500

    except subprocess.TimeoutExpired:
        logger.error("vibe command timed out")
        return jsonify({
            'error': 'vibe command timed out (10s)',
            'details': 'The command took too long to execute'
        }), 500

    except Exception as e:
        logger.exception("Unexpected error in /api/status")
        return jsonify({
            'error': 'Unexpected server error',
            'details': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'vibe-monitor'})


if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("🔍 VIBE MONITOR - System Status Dashboard")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Starting Flask server...")
    logger.info("Dashboard will be available at: http://localhost:5000")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 70)

    # Run Flask server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
