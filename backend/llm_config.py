"""
LLM configuration module.
Supports IBM watsonx.ai and a local rule-based fallback.
"""

import os
from typing import Optional

LLM_AVAILABLE = False
LLM_MODE = "rule_based"

# ---------------------------------------------------------------------------
# Optional IBM watsonx.ai integration
# ---------------------------------------------------------------------------
# Set these environment variables to enable watsonx:
#   WATSONX_API_KEY   — your IBM Cloud API key
#   WATSONX_PROJECT_ID — your watsonx.ai project ID
#   WATSONX_URL        — deployment URL (default: us-south)
#   WATSONX_MODEL_ID   — model ID (default: ibm/granite-13b-chat-v2)
# ---------------------------------------------------------------------------

_wx_model = None

try:
    from ibm_watsonx_ai.foundation_models import Model  # type: ignore
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams  # type: ignore
    from ibm_watsonx_ai.foundation_models.utils.enums import ModelTypes  # type: ignore

    _api_key = os.getenv("WATSONX_API_KEY", "")
    _project_id = os.getenv("WATSONX_PROJECT_ID", "")
    _url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    _model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-chat-v2")

    if _api_key and _project_id:
        _credentials = {"url": _url, "apikey": _api_key}
        _params = {
            GenParams.MAX_NEW_TOKENS: 512,
            GenParams.TEMPERATURE: 0.3,
            GenParams.REPETITION_PENALTY: 1.1,
        }
        _wx_model = Model(
            model_id=_model_id,
            params=_params,
            credentials=_credentials,
            project_id=_project_id,
        )
        LLM_AVAILABLE = True
        LLM_MODE = "watsonx"
except ImportError:
    pass
except Exception:
    pass


def generate_response(prompt: str, context: str = "") -> Optional[str]:
    """
    Generate a response using the configured LLM.
    Returns None if LLM is unavailable (caller falls back to rule engine).
    """
    if not LLM_AVAILABLE or _wx_model is None:
        return None
    try:
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        result = _wx_model.generate_text(prompt=full_prompt)
        return result.strip() if result else None
    except Exception:
        return None


def get_mode() -> str:
    return LLM_MODE


def is_available() -> bool:
    return LLM_AVAILABLE
