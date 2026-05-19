import { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedAnswers, setSelectedAnswers] = useState({});

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setResult(null);
    setError('');
    setSelectedAnswers({});

    try {
      const response = await axios.post('http://localhost:5000/api/generate', { text });
      const responseData = response.data;
      if (typeof responseData === 'object') {
        setResult(responseData);
      } else {
        setResult(JSON.parse(responseData));
      }
    } catch (err) {
      console.error("API call or data processing failed:", err);
      const errorMessage = err.response ? JSON.stringify(err.response.data) : err.message;
      setError(`An error occurred: ${errorMessage}. Please check the console.`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerSelect = (questionIndex, selectedOptionKey) => {
    if (selectedAnswers[questionIndex] !== undefined) {
      return; 
    }
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: selectedOptionKey,
    });
  };

  return (
    <div className="App">
      <div className="centered-container">
        <header>
          <h1>A.I. Study Assistant</h1>
          <p>Paste any text below to instantly generate a concise summary and a practice quiz.</p>
        </header>

        <div className="card">
          <form onSubmit={handleSubmit}>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your article, notes, or any text here..."
              required
            />
            <button type="submit" className="generate-button" disabled={isLoading || !text}>
              {isLoading ? <div className="spinner"></div> : 'Generate ✨'}
            </button>
          </form>
        </div>
      </div>

      {error && <div className="card error centered-container">{error}</div>}

      {result && (
        <div className="results-grid">
          <div className="card summary">
            <h2>Summary</h2>
            <ul>
              {result.summary.map((point, index) => (
                <li key={index}>{point}</li>
              ))}
            </ul>
          </div>
          <div className="card quiz">
            <h2>Quiz</h2>
            {result.quiz.map((q, questionIndex) => (
              <div key={questionIndex} className="question-block">
                <p><strong>{questionIndex + 1}. {q.question}</strong></p>
                <div className="quiz-options">
                  {Object.entries(q.options).map(([key, value]) => {
                    const isSelected = selectedAnswers[questionIndex] === key;
                    const isCorrect = q.answer === key;
                    
                    let buttonClass = '';
                    if (isSelected) {
                      buttonClass = isCorrect ? 'correct' : 'incorrect';
                    } else if (selectedAnswers[questionIndex] !== undefined && isCorrect) {
                      buttonClass = 'correct';
                    }

                    return (
                      <button
                        key={key}
                        className={buttonClass}
                        onClick={() => handleAnswerSelect(questionIndex, key)}
                        disabled={selectedAnswers[questionIndex] !== undefined}
                      >
                         <strong>{key}:</strong> {value}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;