"use client"
import React, { useEffect, useState } from 'react';
import { TiTick } from "react-icons/ti";
import io from 'socket.io-client'

function App() {
  const [text, setText] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [progress, setProgress] = useState(1);
  const [complete, setComplete] = useState(false)
  const [socket, setSocket] = useState(null);
  const steps = ["Audio Generated", "Video Generated", "Subtitles Added", "Compiled"]

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
    <div className='bg-[#202020] flex flex-col gap-[7rem] items-center justify-center'>
      <div className="flex items-start h-screen w-screen mt-10 justify-between">
        {steps?.map((step, i) => (
          <div
            key={i}
            className={`step-item ${progress === i + 1 && "active"} ${
              (i + 1 < progress || complete) && "complete"
            } `}
          >
            <div className="step">
              {i + 1 < progress || complete ? <TiTick size={24} /> : i + 1}
            </div>
            <p className="text-gray-500">{step}</p>
          </div>
        ))}
      </div>

      <div className='flex flex-col'>
        <form onSubmit={handleSubmit}>
          <label>
            Enter text for subtitles:
            <input
              type="text"
              className='text-black'
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
    </div>
  );
}

export default App;
