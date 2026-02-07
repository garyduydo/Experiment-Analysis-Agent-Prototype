#!/usr/bin/env python3
"""
Flask API for Amplitude Experiment Analyzer
HYBRID MODE: Supports both server-side and user-provided API keys
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import requests
from datetime import datetime
import random

app = Flask(__name__, static_folder='.')
CORS(app)

class KeyRotator:
    """Handles API key rotation for high availability"""
    
    def __init__(self):
        self.keys = self._load_keys()
        self.current_index = 0
    
    def _load_keys(self):
        """Load API keys from environment (supports multiple keys)"""
        keys = []
        
        primary_key = os.getenv('GROQ_API_KEY')
        if primary_key:
            keys.append(primary_key)
        
        index = 2
        while True:
            key = os.getenv(f'GROQ_API_KEY_{index}')
            if not key:
                break
            keys.append(key)
            index += 1
        
        return keys
    
    def get_key(self):
        """Get current API key with round-robin rotation"""
        if not self.keys:
            return None
        
        key = self.keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.keys)
        return key
    
    def get_random_key(self):
        """Get random API key for load balancing"""
        if not self.keys:
            return None
        return random.choice(self.keys)
    
    def has_keys(self):
        """Check if any keys are available"""
        return len(self.keys) > 0
    
    def count(self):
        """Get number of available keys"""
        return len(self.keys)


class AmplitudeExperimentAnalyzer:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
    
    def analyze_with_ai(self, experiment_data):
        """Send experiment data to Groq for FREE analysis"""
        print(f"[INFO] Analyzing with Groq AI...")
        
        prompt = f"""You are an expert growth analyst. Analyze this A/B test experiment and provide comprehensive insights.

EXPERIMENT DATA:
{json.dumps(experiment_data, indent=2)}

Provide your analysis in the following JSON structure (respond ONLY with valid JSON, no markdown):

{{
  "executive_summary": "2-3 sentence summary of results and recommendation",
  "statistical_results": {{
    "primary_metric": "conversion_rate",
    "winner": "variant_a or control or inconclusive",
    "lift": "percentage improvement",
    "confidence_level": "95% or 90% or below 90%",
    "is_significant": true,
    "sample_size_adequate": true
  }},
  "key_insights": [
    "Insight 1 with specific numbers",
    "Insight 2 with specific numbers",
    "Insight 3 with specific numbers"
  ],
  "secondary_metrics": [
    {{
      "metric": "avg_session_duration",
      "impact": "positive/negative/neutral",
      "change": "percentage or absolute change",
      "note": "brief explanation"
    }}
  ],
  "risks_and_caveats": [
    "Important caveat 1",
    "Important caveat 2"
  ],
  "recommended_action": "ship/iterate/kill with brief rationale",
  "next_experiments": [
    "Suggested follow-up experiment 1",
    "Suggested follow-up experiment 2"
  ],
  "report_narrative": "A comprehensive 3-4 paragraph narrative report"
}}"""
        
        try:
            if not self.groq_api_key.startswith('gsk_'):
                raise Exception(f"Invalid Groq API key format. Key should start with 'gsk_'")
            
            print(f"[OK] API key format valid")
            print(f"[OK] Sending request to Groq...")
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.groq_api_key}"
                },
                json={
                    "model": "llama-3.1-70b-versatile",
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }],
                    "temperature": 0.3,
                    "max_tokens": 4000
                },
                timeout=60
            )
            
            if response.status_code == 400:
                error_detail = response.json() if response.text else {}
                print(f"[ERROR] Groq 400 Error: {error_detail}")
                
                if 'error' in error_detail:
                    error_msg = error_detail['error']
                    if isinstance(error_msg, dict):
                        error_msg = error_msg.get('message', str(error_msg))
                    raise Exception(f"Groq API Error: {error_msg}")
                
                raise Exception(f"Groq API Bad Request (400)")
            
            elif response.status_code == 401:
                raise Exception("Groq API Key is invalid or expired")
            
            elif response.status_code == 429:
                raise Exception("Groq API rate limit exceeded. Try again in a moment.")
            
            response.raise_for_status()
            result = response.json()
            
            print(f"[OK] Got response from Groq")
            
            if 'choices' not in result or len(result['choices']) == 0:
                raise Exception(f"Unexpected Groq response format")
            
            analysis_text = result['choices'][0]['message']['content']
            clean_text = analysis_text.replace('```json', '').replace('```', '').strip()
            
            try:
                analysis = json.loads(clean_text)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse AI response as JSON")
                raise Exception(f"AI returned invalid JSON: {str(e)}")
            
            print(f"[SUCCESS] Analysis complete!")
            return analysis
        
        except requests.exceptions.Timeout:
            raise Exception("Groq API timeout - please try again")
        
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', str(e))
                    raise Exception(f"Groq API error: {error_msg}")
                except:
                    raise Exception(f"Groq API error: {str(e)}")
            raise Exception(f"Connection error: {str(e)}")
        
        except Exception as e:
            if "Groq" in str(e):
                raise
            raise Exception(f"Analysis failed: {str(e)}")


key_rotator = KeyRotator()


@app.route('/')
def index():
    """Serve the frontend"""
    return send_from_directory('.', 'index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze experiment data endpoint
    HYBRID MODE: Accepts user-provided key OR uses server key
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        experiment_data = data.get('experiment_data')
        user_api_key = data.get('api_key') 
        
        if not experiment_data:
            return jsonify({'error': 'No experiment data provided'}), 400
        
        if 'variants' not in experiment_data:
            return jsonify({'error': 'Invalid experiment data: missing variants'}), 400
        
        if user_api_key:
            print(f"[INFO] Using user-provided API key")
            groq_api_key = user_api_key
            key_source = "user"
        else:
            groq_api_key = key_rotator.get_key()
            if not groq_api_key:
                return jsonify({
                    'error': 'No server API key configured. Please provide your own Groq API key or contact the administrator.',
                    'require_user_key': True
                }), 500
            print(f"[INFO] Using server API key (pool: {key_rotator.count()} keys)")
            key_source = "server"
        
        print(f"[INFO] Experiment: {experiment_data.get('experiment_name', 'Unknown')}")
        print(f"[INFO] Variants: {list(experiment_data['variants'].keys())}")
        print(f"[INFO] Key source: {key_source}")
        
        analyzer = AmplitudeExperimentAnalyzer(groq_api_key)
        analysis = analyzer.analyze_with_ai(experiment_data)
        
        response_data = {
            **analysis,
            '_meta': {
                'key_source': key_source,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Error in analyze endpoint: {error_msg}")
        
        response = {'error': error_msg}
        if 'invalid' in error_msg.lower() or '401' in error_msg:
            response['suggest_user_key'] = True
        
        return jsonify(response), 500


@app.route('/api/config', methods=['GET'])
def config():
    """
    Return configuration info for frontend
    Tells UI whether to show "Use Your Own Key" option
    """
    server_key_available = key_rotator.has_keys()
    
    return jsonify({
        'server_key_available': server_key_available,
        'server_key_count': key_rotator.count() if server_key_available else 0,
        'hybrid_mode': True,
        'features': {
            'use_server_key': server_key_available,
            'use_own_key': True,
            'key_rotation': key_rotator.count() > 1
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    server_keys = key_rotator.count()
    
    return jsonify({
        'status': 'healthy',
        'server_keys_configured': server_keys,
        'hybrid_mode': True,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/test-groq', methods=['GET'])
def test_groq():
    """Test Groq API connection with server keys"""
    try:
        groq_api_key = key_rotator.get_key()
        if not groq_api_key:
            return jsonify({'error': 'No server API keys configured'}), 500
        
        print("[INFO] Testing Groq API connection...")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {groq_api_key}"
            },
            json={
                "model": "llama-3.1-70b-versatile",
                "messages": [{"role": "user", "content": "Say 'OK'"}],
                "max_tokens": 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("[SUCCESS] Groq API test successful!")
            return jsonify({
                'status': 'success',
                'message': f'Groq API is working! ({key_rotator.count()} keys configured)',
                'keys_available': key_rotator.count()
            })
        else:
            return jsonify({
                'status': 'error',
                'status_code': response.status_code,
                'response': response.text
            }), response.status_code
    
    except Exception as e:
        print(f"[ERROR] Groq API test exception: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Hybrid Experiment Analyzer on port {port}...")
    print("=" * 60)
    
    if key_rotator.has_keys():
        print(f"[OK] Server API keys configured: {key_rotator.count()} key(s)")
        print(f"[OK] Key rotation: {'ENABLED' if key_rotator.count() > 1 else 'DISABLED'}")
    else:
        print(f"[WARNING] No server API keys configured")
        print(f"[INFO] Users will need to provide their own Groq API keys")
    
    print(f"[OK] Hybrid mode: ENABLED")
    print(f"[OK] Users can choose: Server key OR their own key")
    print("=" * 60)
    print(f"Server ready! Visit http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=True)