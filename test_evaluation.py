#!/usr/bin/env python3
"""
Evaluation test script for the 4 required questions:
1. How is CGPA calculated?
2. What is the minimum attendance requirement?
3. What happens if a student has an F grade?
4. Ask a question not covered by the documents.
"""

import urllib.request
import json
import time

QUESTIONS = [
    "How is CGPA calculated?",
    "What is the minimum attendance requirement?",
    "What happens if a student has an F grade?",
    "What is the policy for international student visa and embassy renewal?",
]


def test_questions():
    print("=" * 70)
    print("RUNNING 4 MANDATORY EVALUATION TESTS")
    print("=" * 70)

    for idx, q in enumerate(QUESTIONS, start=1):
        print(f"\n{'='*20} QUESTION {idx}: {q} {'='*20}")
        t0 = time.perf_counter()
        req = urllib.request.Request(
            "http://localhost:8000/api/query",
            data=json.dumps({"question": q}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as res:
                data = json.loads(res.read().decode("utf-8"))
            elapsed = (time.perf_counter() - t0) * 1000

            backend_latency = data.get("latency_ms") or {}
            print(f"Latency: E2E={elapsed:.1f}ms | Retrieval={backend_latency.get('retrieval_ms')}ms | Total={backend_latency.get('total_ms')}ms")
            print(f"Demo Mode: {data.get('demo_mode')}")
            print("\nAnswer:")
            print(data.get("answer"))
            print(f"\nRetrieved Citations ({len(data.get('sources', []))}):")
            for s in data.get("sources", []):
                doc_name = s.get("document")
                page = s.get("page")
                score = s.get("score", 0)
                print(f"  - [{doc_name} (Page {page})] Similarity: {score:.3f}")
        except Exception as e:
            print(f"Error testing question {idx}: {e}")

    print("\n" + "=" * 70)
    print("ALL 4 QUESTIONS TESTED")
    print("=" * 70)


if __name__ == "__main__":
    test_questions()
