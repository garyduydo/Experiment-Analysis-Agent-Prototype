#!/usr/bin/env python3
"""
Amplitude Experiment Analyzer - CLI Tool (Groq-powered)
Connects to Amplitude API, pulls experiment data, and analyzes with FREE AI
"""

import os
import json
import requests
import sys
from datetime import datetime
import argparse

class AmplitudeExperimentAnalyzer:
    def __init__(self, amplitude_api_key, amplitude_secret_key, groq_api_key):
        self.amplitude_api_key = amplitude_api_key
        self.amplitude_secret_key = amplitude_secret_key
        self.groq_api_key = groq_api_key
        self.amplitude_base_url = "https://amplitude.com/api/2"
    
    def fetch_experiment_data(self, experiment_id):
        """Fetch experiment data from Amplitude"""
        print(f" Fetching experiment {experiment_id} from Amplitude...")
        
        url = f"{self.amplitude_base_url}/experiments/{experiment_id}"
        
        headers = {
            "Authorization": f"Basic {self.amplitude_api_key}:{self.amplitude_secret_key}"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            print(f" Successfully fetched experiment data")
            return self.transform_amplitude_data(data)
        
        except requests.exceptions.RequestException as e:
            print(f" Error fetching from Amplitude: {e}")
            return None
    
    def transform_amplitude_data(self, amplitude_data):
        """Transform Amplitude data format to our analysis format"""
        
        variants = {}
        for variant in amplitude_data.get('variants', []):
            variant_key = 'control' if variant.get('is_control') else f"variant_{variant.get('id')}"
            
            variants[variant_key] = {
                "name": variant.get('name', 'Unknown'),
                "users": variant.get('users', 0),
                "conversions": variant.get('conversions', 0),
                "conversion_rate": variant.get('conversion_rate', 0),
                "avg_session_duration": variant.get('avg_session_duration'),
                "bounce_rate": variant.get('bounce_rate'),
                "revenue_per_user": variant.get('revenue_per_user')
            }
        
        experiment_data = {
            "experiment_name": amplitude_data.get('name', 'Unknown Experiment'),
            "hypothesis": amplitude_data.get('hypothesis', ''),
            "start_date": amplitude_data.get('start_date', ''),
            "end_date": amplitude_data.get('end_date', ''),
            "variants": variants,
            "metadata": {
                "experiment_id": amplitude_data.get('id'),
                "traffic_source": amplitude_data.get('traffic_source', 'mixed'),
                "segment": amplitude_data.get('segment', 'all_users'),
                "platform": amplitude_data.get('platform', 'all')
            }
        }
        
        return experiment_data
    
    def analyze_with_ai(self, experiment_data):
        """Send experiment data to Groq for FREE analysis"""
        print(f" Analyzing with Groq AI (FREE)...")
        
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
    "is_significant": true/false,
    "sample_size_adequate": true/false
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
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.groq_api_key}"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{
                        "role": "user",
                        "content": prompt
                    }],
                    "temperature": 0.3,
                    "max_tokens": 4000
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            analysis_text = result['choices'][0]['message']['content']
            
            clean_text = analysis_text.replace('```json', '').replace('```', '').strip()
            analysis = json.loads(clean_text)
            
            print(f" Analysis complete!")
            return analysis
        
        except Exception as e:
            print(f" Error analyzing with AI: {e}")
            return None
    
    def save_report(self, experiment_data, analysis, output_file):
        """Save complete report to file"""
        report = {
            "experiment": experiment_data,
            "analysis": analysis,
            "generated_at": datetime.now().isoformat(),
            "tool_version": "1.0",
            "ai_provider": "Groq (FREE)"
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f" Report saved to: {output_file}")
    
    def print_summary(self, analysis):
        """Print analysis summary to console"""
        print("\n" + "="*80)
        print(" EXPERIMENT ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n EXECUTIVE SUMMARY:")
        print(f"   {analysis['executive_summary']}")
        
        print(f"\n STATISTICAL RESULTS:")
        stats = analysis['statistical_results']
        print(f"   Winner: {stats['winner'].upper()}")
        print(f"   Lift: {stats['lift']}")
        print(f"   Confidence: {stats['confidence_level']}")
        print(f"   Significant: {' YES' if stats['is_significant'] else ' NO'}")
        
        print(f"\n KEY INSIGHTS:")
        for i, insight in enumerate(analysis['key_insights'], 1):
            print(f"   {i}. {insight}")
        
        print(f"\n RECOMMENDED ACTION:")
        print(f"   {analysis['recommended_action'].upper()}")
        
        print(f"\n NEXT EXPERIMENTS:")
        for i, exp in enumerate(analysis['next_experiments'], 1):
            print(f"   {i}. {exp}")
        
        print("\n" + "="*80)
        print(f" Cost: $0.00 (FREE with Groq!)")
        print(f"  Time saved: ~2.5 hours vs manual analysis")
        print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Amplitude experiments with FREE AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Analyze specific experiment
  python amplitude_analyzer.py --experiment exp_abc123
  
  # Save report to custom location
  python amplitude_analyzer.py --experiment exp_abc123 --output my-report.json
  
  # Analyze from local JSON file
  python amplitude_analyzer.py --file experiment-data.json

Environment Variables:
  AMPLITUDE_API_KEY       Your Amplitude API key
  AMPLITUDE_SECRET_KEY    Your Amplitude secret key
  GROQ_API_KEY           Your Groq API key (FREE from console.groq.com)
        '''
    )
    
    parser.add_argument('--experiment', '-e', help='Amplitude experiment ID')
    parser.add_argument('--file', '-f', help='Local JSON file with experiment data')
    parser.add_argument('--output', '-o', default='experiment-analysis.json', help='Output file path')
    
    args = parser.parse_args()
    
    amplitude_api_key = os.getenv('AMPLITUDE_API_KEY')
    amplitude_secret_key = os.getenv('AMPLITUDE_SECRET_KEY')
    groq_api_key = os.getenv('GROQ_API_KEY')
    
    if not groq_api_key:
        print(" Error: GROQ_API_KEY environment variable not set")
        print("   Get your FREE key at: https://console.groq.com")
        print("   Set it with: export GROQ_API_KEY='gsk_...'")
        sys.exit(1)
    
    if not args.experiment and not args.file:
        parser.print_help()
        sys.exit(1)
    
    analyzer = AmplitudeExperimentAnalyzer(
        amplitude_api_key,
        amplitude_secret_key,
        groq_api_key
    )
    
    if args.file:
        print(f" Loading experiment data from {args.file}...")
        with open(args.file, 'r') as f:
            experiment_data = json.load(f)
    else:
        if not amplitude_api_key or not amplitude_secret_key:
            print(" Error: AMPLITUDE_API_KEY and AMPLITUDE_SECRET_KEY required for fetching from Amplitude")
            print("   Set them with:")
            print("   export AMPLITUDE_API_KEY='your-key'")
            print("   export AMPLITUDE_SECRET_KEY='your-secret'")
            sys.exit(1)
        
        experiment_data = analyzer.fetch_experiment_data(args.experiment)
        if not experiment_data:
            sys.exit(1)
    
    analysis = analyzer.analyze_with_ai(experiment_data)
    if not analysis:
        sys.exit(1)
    
    analyzer.print_summary(analysis)
    
    analyzer.save_report(experiment_data, analysis, args.output)
    
    print(f"\n Done! Full report saved to {args.output}")


if __name__ == "__main__":
    main()