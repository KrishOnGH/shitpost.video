"use client"
import React, { useState } from 'react';

function App() {
  const [text, setText] = useState('');
  const [videoUrl, setVideoUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5000/generate-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "post": text, "footage_type": "minecraft" }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(new Blob([blob], { type: 'video/mp4' }));
      setVideoUrl(url);
    } catch (error) {
      console.error('Error generating video:', error);
    }
  };

  return (
    <div className="App">
      <form onSubmit={handleSubmit}>
        <label>
          Enter text for subtitles:
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
        </label>
        <button type="submit">Generate Video</button>
      </form>
      {videoUrl && (
        <div>
          <h2>Generated Video:</h2>
          <video controls src={videoUrl} />
        </div>
      )}
    </div>
  );
}

export default App;
