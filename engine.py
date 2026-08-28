import os
import json
from pathlib import Path
import google.generativeai as genai
from src.checker import check_case

def load_prompt() -> str:
    prompt_path = Path("prompts/diagnose_prompt.md")
    if prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are a network AI assistant. Return JSON."

def run_diagnosis(case: dict) -> dict:
    """
    Orchestrates the deterministic checker and the AI diagnosis.
    Returns a unified result dictionary.
    """
    show_output = case.get("show_outputs", "")
    symptom = case.get("symptom", "")
    topology = case.get("topology_note", "")
    
    # 1. Run deterministic checker
    checker_results = check_case(show_output)
    
    # 2. Build prompt
    system_prompt = load_prompt()
    
    user_prompt = f"""
    Case ID: {case.get('case_id')}
    Symptom: {symptom}
    Topology Note: {topology}
    
    Show Command Outputs:
    {show_output}
    
    Deterministic Checker Findings:
    {json.dumps(checker_results, indent=2)}
    
    Provide the diagnosis in the requested JSON format.
    """
    
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    if not api_key or api_key == "your_api_key_here":
        return _demo_mode_diagnosis(case, checker_results)
        
    try:
        genai.configure(api_key=api_key)
        # Using a model that supports JSON or general text
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        response = model.generate_content(
            system_prompt + "\n\n" + user_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1
            )
        )
        
        text = response.text.strip()
        
        # Clean up possible markdown formatting
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        ai_result = json.loads(text)
        return _validate_and_normalize(ai_result, checker_results, mode="LIVE AI MODE")
        
    except Exception as e:
        # Fallback or error
        return {
            "mode": "ERROR",
            "error_message": str(e),
            "checker_results": checker_results
        }

def _demo_mode_diagnosis(case: dict, checker_results: dict) -> dict:
    """Fallback static diagnosis for Demo Mode without API key"""
    
    # Extract hints from dataset if available
    expected_fault = case.get("expected_fault", "Unknown fault")
    layer = case.get("osi_layer", "Layer 3")
    
    ai_result = {
        "root_cause": f"[DEMO] The expected fault is: {expected_fault}",
        "osi_layer": layer,
        "confidence": 0.85,
        "evidence": [f"[DEMO] Reference dataset expects: {expected_fault}"] + [f.get("evidence", "") for f in checker_results.get("findings", [])],
        "next_command": "show running-config",
        "fix_steps": [
            "! This is a demo mode fix",
            "configure terminal",
            "! fix goes here"
        ]
    }
    
    # Specific demo fix for NET-001
    if case.get("case_id") == "NET-001":
        ai_result["fix_steps"] = [
            "configure terminal",
            "interface GigabitEthernet0/0.30",
            "no shutdown"
        ]
        
    return _validate_and_normalize(ai_result, checker_results, mode="DEMO MODE")

def _validate_and_normalize(ai_result: dict, checker_results: dict, mode: str) -> dict:
    # Ensure all fields are present
    normalized = {
        "mode": mode,
        "checker_results": checker_results,
        "diagnosis": {
            "root_cause": ai_result.get("root_cause", "Unable to determine root cause."),
            "osi_layer": ai_result.get("osi_layer", "Unknown"),
            "confidence": float(ai_result.get("confidence", 0.0)),
            "evidence": ai_result.get("evidence", []),
            "next_command": ai_result.get("next_command", ""),
            "fix_steps": ai_result.get("fix_steps", [])
        }
    }
    return normalized
