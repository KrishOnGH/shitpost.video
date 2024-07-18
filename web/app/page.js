"use client"
import React, { useEffect, useState } from 'react';
import { TiTick } from "react-icons/ti";
import { io } from 'socket.io-client'

function App() {
  const [username, setUsername] = useState('');

  useEffect(() => {
    let user = localStorage.getItem('user');
    console.log(user)
    if (user) {
      setUsername(user);
    } else {
      const newUsername = Math.random().toString(36).substring(7);
      setUsername(newUsername);
      localStorage.setItem('user', newUsername);
    }
  }, []);

  const [text, setText] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [progress, setProgress] = useState(0);
  const [selectedFootage, setSelectedFootage] = useState('minecraft');
  const [subtitleColor, setSubtitleColor] = useState('white');
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
    setUsername(Math.random().toString(36).substring(7))
    try {
      const response = await fetch('http://localhost:5000/generate-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "post": text, "footage_type": selectedFootage, "subtitle_color": subtitleColor, "username": username}),
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
      <div className="flex w-full pt-4 mt-10 pb-2 items-start justify-between bg-[#202020]">
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
          <div className='w-full h-full text-4xl px-4 md:px-8 lg:px-16'>
            <form className='w-full h-full flex flex-col items-start' onSubmit={handleSubmit}>
              <div className='w-full max-w-2xl mx-auto'>
                <label className='block mb-8'>
                  <div className='mb-2 text-3xl'>
                    Enter text for subtitles:
                  </div>
                  <input
                    className='text-black w-full p-2 rounded'
                    type="text"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    required
                  />
                </label>
                
                <div className='mb-2 text-2xl'>
                    Footage Type:
                </div>
                <div className='flex mb-8'>
                  <label className='flex items-center'>
                    <input
                      type="radio"
                      className="form-radio h-5 w-5 text-blue-600"
                      name="footageType"
                      value="minecraft"
                      checked={selectedFootage === 'minecraft'}
                      onChange={(e) => setSelectedFootage(e.target.value)}
                    />
                    <span className="ml-2 mr-4 text-xl">Minecraft</span>
                  </label>
      
                  <label className='flex items-center'>
                    <input
                      type="radio"
                      className="form-radio h-5 w-5 text-blue-600"
                      name="footageType"
                      value="subway surfers"
                      checked={selectedFootage === 'subway surfers'}
                      onChange={(e) => setSelectedFootage(e.target.value)}
                    />
                    <span className="ml-2 text-xl">Subway Surfers</span>
                  </label>
                </div>

                <div className='mb-2 text-2xl'>
                    Subtitle Color:
                </div>
                <div className='flex mb-8'>
                  <label className='flex items-center'>
                    <input
                      type="radio"
                      className="form-radio h-5 w-5 text-blue-600"
                      name="subtitleColor"
                      value="white"
                      checked={subtitleColor === 'white'}
                      onChange={(e) => setSubtitleColor(e.target.value)}
                    />
                    <span className="ml-2 mr-4 text-xl">White</span>
                  </label>
      
                  <label className='flex items-center'>
                    <input
                      type="radio"
                      className="form-radio h-5 w-5 text-blue-600"
                      name="subtitleColor"
                      value="yellow"
                      checked={subtitleColor === 'yellow'}
                      onChange={(e) => setSubtitleColor(e.target.value)}
                    />
                    <span className="ml-2 mr-4 text-xl">Yellow</span>
                  </label>
                  
                  <label className='flex items-center'>
                    <input
                      type="radio"
                      className="form-radio h-5 w-5 text-blue-600"
                      name="subtitleColor"
                      value="purple"
                      checked={subtitleColor === 'purple'}
                      onChange={(e) => setSubtitleColor(e.target.value)}
                    />
                    <span className="ml-2 mr-4 text-xl">Purple</span>
                  </label>
                  
                  <label className='flex items-center'>
                    <input
                      type="radio"
                      className="form-radio h-5 w-5 text-blue-600"
                      name="subtitleColor"
                      value="blue"
                      checked={subtitleColor === 'blue'}
                      onChange={(e) => setSubtitleColor(e.target.value)}
                    />
                    <span className="ml-2 text-xl">Blue</span>
                  </label>
                </div>

                <button className='text-2xl rounded-2xl bg-blue-700 px-4 py-3' type="submit">
                  Generate Video
                </button>
              </div>
            </form>
          </div>
        )}

        {progress > 0 && progress < 5 && (
          <div className='text-3xl w-full flex justify-center mb-[13.75rem]'>
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
                <video controls src={videoUrl} className='max-w-full max-h-[70vh] rounded-2xl' />
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
