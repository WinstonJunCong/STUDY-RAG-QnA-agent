#!/usr/bin/env python3
import pandas as pd
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

import config
config.DEBUG_LLM = False

from pipeline.index_builder import load_index, configure_settings
from agent.qa import ask

def main():
    configure_settings()
    index = load_index()
    
    df = pd.read_excel('C:/Users/LS0758/Downloads/UAT.xlsx')
    
    responses = []
    for i, question in enumerate(df['Questiion']):
        print(f"[{i+1}/17] {question[:50]}...")
        try:
            result = ask(question, index)
            response = result['answer']
        except Exception as e:
            response = f"ERROR: {str(e)}"
        responses.append(response)
        print(f"   -> Done ({len(response)} chars)")
    
    df['Latest Response (R12b-StrongerRule)'] = responses
    
    output_path = 'C:/Users/LS0758/Downloads/UAT.xlsx'
    df.to_excel(output_path, index=False)
    print(f"\nSaved to {output_path}")
    print("Added column: 'Latest Response (R12b-StrongerRule)'")
    
    print("\n>> Scoring responses...")
    from scoring.score_responses import score_latest_version
    score_latest_version()

if __name__ == "__main__":
    main()
