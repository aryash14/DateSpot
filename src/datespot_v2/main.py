#!/usr/bin/env python
import sys
import warnings
import time
    
import pandas as pd
from datetime import datetime

from datespot.crew import Datespot

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    inputs = {

        # 'user_input': 'Looking for an italian spot with a rooftop view and live music',
        'user_input': 'Looking for a rooftop bar in SF.',
        'current_year': str(datetime.now().year)
    }
    
    try:
        start_time = time.time()
        crew = Datespot().crew()
        crew.kickoff(inputs=inputs)
        costs = 1.93 * (crew.usage_metrics.prompt_tokens + crew.usage_metrics.completion_tokens) / 1_000_000
        end_time = time.time()
        print(f"Total costs: ${costs:.4f}")
        print(f"Total runtime: {end_time - start_time:.2f} seconds")

        df_usage_metrics = pd.DataFrame([crew.usage_metrics.dict()])
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        Datespot().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Datespot().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    try:
        Datespot().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
