import React from 'react';

const SAMPLE_QUESTIONS = [
  "What happens if I submit a lab late?",
  "What is the minimum attendance required for final exams?",
  "Can I use AI tools like ChatGPT for course assignments?",
  "What is the grading scale and evaluation breakdown?",
  "How many grace days do students get per semester?",
  "What is the policy for Duty Leaves (OD) in sports or hackathons?",
];

export default function SuggestedQuestions({ onSelectQuestion, disabled }) {
  return (
    <div className="chips-container" id="suggested-questions-container">
      {SAMPLE_QUESTIONS.map((q, idx) => (
        <button
          key={idx}
          id={`suggestion-chip-${idx}`}
          className="chip"
          onClick={() => onSelectQuestion(q)}
          disabled={disabled}
        >
          💬 {q}
        </button>
      ))}
    </div>
  );
}
