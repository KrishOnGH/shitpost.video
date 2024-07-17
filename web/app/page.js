"use client"
import React, { useEffect, useState } from 'react';
import { TiTick } from "react-icons/ti";
import { io } from 'socket.io-client'

function App() {
  const [text, setText] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [progress, setProgress] = useState(0);
  const [username] = useState(() => Math.random().toString(36).substring(7));
  const steps = ["Audio Generated", "Video Generated", "Subtitles Added", "Compiled"];

  useEffect(() => {
    const socket = io('http://localhost:5000');
    socket.on('progress', (data) => {
      if (data.username === username) {
        setProgress(data.step);
      }
    });

    return () => {
      socket.disconnect();
    };
  }, [username]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setProgress(1);
    try {
      const response = await fetch('http://localhost:5000/generate-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "post": text, "footage_type": "minecraft", "username": username }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(new Blob([blob], { type: 'video/mp4' }));
      setVideoUrl(url);
      setProgress(5);
    } catch (error) {
      console.error('Error generating video:', error);
    }
  }

  const handleDownload = () => {
    if (videoUrl) {
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = 'video.mp4';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleRetry = () => {
    setProgress(0);
    setText('');
    setVideoUrl('');
  };

  return (
    <div className='bg-[#202020] w-[100vw] flex flex-col justify-start min-h-screen'>
      <div className="absolute flex w-full pt-4 mt-10 pb-2 items-start justify-between bg-[#202020]">
        {steps?.map((step, i) => (
          <div
            key={i}
            className={`step-item ${progress === i + 1 && "active"} ${
              (i + 1 < progress) && "complete"
            } `}
          >
            <div className="step">
              {i + 1 < progress ? <TiTick size={24} /> : i + 1}
            </div>
            <p className="text-gray-500">{step}</p>
          </div>
        ))}
      </div>

      <div className='flex-grow flex flex-col items-center justify-center'>
        {progress === 0 && (
          <div className='w-full h-full text-3xl'>
            <form className='w-full h-full flex items-center justify-center' onSubmit={handleSubmit}>
              <label>
                <div className='ml-3 mb-2'>
                  Enter text for subtitles:
                </div>
                <input
                  className='text-black ml-3'
                  type="text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
              </label>
              <button className='text-2xl ml-20 rounded-3xl bg-blue-700 p-5' type="submit">Generate Video</button>
            </form>
          </div>
        )}

        {progress > 0 && progress < 5 && (
          <div className='text-3xl w-full flex justify-center'>
            {progress === 1 && "Audio generating.."}
            {progress === 2 && "Video Generating.."}
            {progress === 3 && "Subtitles being added.."}
            {progress === 4 && "Video compiling.."}
          </div>
        )}

        {progress === 5 && (
          <div className='w-full flex flex-col items-center h-full'>
            <h2 className='text-3xl mb-7'>Video compiled!</h2>
            {videoUrl && (
              <div className='w-full flex justify-center h-full items-center'>
                <video controls src={videoUrl} className='max-w-full max-h-[70vh]' />
                <div className='flex'>
                  <button onClick={handleDownload} className='ml-10 mb-3 px-5 py-3 bg-blue-700 rounded-2xl cursor-pointer'>Download</button>
                  <button onClick={handleRetry} className='ml-5 mb-3 px-5 py-3 bg-red-700 rounded-2xl cursor-pointer'>Retry</button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
