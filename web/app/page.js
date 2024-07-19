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

  const [link, setLink] = useState('');
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
    try {
      if (link.toLowerCase().startsWith('https://www.reddit.com/r/amitheasshole/comments/') || link.toLowerCase().startsWith('https://www.reddit.com/r/askreddit/comments/')) {
        setProgress(1);
        const response = await fetch('http://localhost:5000/generate-video', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ "link": link, "footage_type": selectedFootage, "subtitle_color": subtitleColor, "username": username}),
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(new Blob([blob], { type: 'video/mp4' }));
        setVideoUrl(url);
        setProgress(5);
      } else {
        window.alert("Link must be of AITA or AskReddit subreddit post.")
      }
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
    setLink('');
    setVideoUrl('');
  };

  const generatelink = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:5000/generate-link', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "username": username }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      data = response.json()
      setLink(data)
    } catch (error) {
      console.error('Error generating link:', error);
    }
  }

  const openlink = async (e) => {
    e.preventDefault();
    if (link.toLowerCase().startsWith('https://www.reddit.com/r/amitheasshole/comments/') || link.toLowerCase().startsWith('https://www.reddit.com/r/askreddit/comments/')) {
      window.open(link)
    } else {
      window.alert("Link must be of AITA or AskReddit subreddit post.")
    }
  }

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
                    Enter reddit link (AITA/AskReddit):
                  </div>

                  <div className='relative flex'>
                    <button 
                      onClick={openlink}
                      className="absolute left-3 bottom-[1rem] text-indigo-500 cursor-pointer"
                    >
                      <svg height="24px" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 15L15 9M15 9H10.5M15 9V13.5" stroke="#6366f1" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M22 12C22 16.714 22 19.0711 20.5355 20.5355C19.0711 22 16.714 22 12 22C7.28595 22 4.92893 22 3.46447 20.5355C2 19.0711 2 16.714 2 12C2 7.28595 2 4.92893 3.46447 3.46447C4.92893 2 7.28595 2 12 2C16.714 2 19.0711 2 20.5355 3.46447C21.5093 4.43821 21.8356 5.80655 21.9449 8" stroke="#6366f1" stroke-width="1.5" stroke-linecap="round"/>
                      </svg>
                    </button>

                    <input
                      className='text-black w-full p-2 px-12 rounded'
                      type="text"
                      value={link}
                      onChange={(e) => setLink(e.target.value)}
                      required
                    />

                    <button 
                      onClick={generatelink}
                      className="absolute right-3 bottom-[1rem] text-indigo-500 cursor-pointer"
                    >
                      <svg version="1.0" xmlns="http://www.w3.org/2000/svg"
                        className="w-8 h-6"
                        width="512.000000pt" height="512.000000pt" viewBox="0 0 512.000000 512.000000"
                        preserveAspectRatio="xMidYMid meet">

                        <g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)"
                          fill="#6366f1" stroke="#6366f1">
                          <path d="M2740 5098 c-37 -19 -52 -38 -95 -113 l-51 -89 -87 -18 c-47 -9 -100
                          -24 -116 -32 -62 -33 -97 -110 -82 -179 10 -43 15 -51 91 -132 l56 -60 -10
                          -101 c-11 -121 -6 -147 43 -195 63 -64 116 -64 257 1 l71 32 84 -38 c107 -49
                          168 -52 223 -10 61 46 70 73 62 203 l-7 112 64 69 c35 37 70 85 76 105 25 73
                          -10 157 -81 193 -16 8 -67 23 -114 32 l-86 17 -52 90 c-43 76 -58 93 -96 113
                          -24 12 -58 22 -75 22 -17 0 -51 -10 -75 -22z m124 -241 c24 -45 54 -91 65
                          -101 11 -10 54 -24 98 -32 140 -26 133 -16 64 -90 -98 -104 -96 -99 -82 -215
                          7 -56 11 -103 8 -105 -2 -2 -42 14 -89 36 -47 22 -97 40 -111 40 -13 0 -64
                          -18 -112 -40 -48 -23 -89 -39 -91 -37 -2 2 0 37 6 78 18 141 19 140 -62 225
                          -79 83 -79 87 1 99 25 3 69 12 96 20 53 15 58 21 136 162 13 24 25 43 26 43 1
                          0 22 -37 47 -83z"/>
                          <path d="M4262 5099 c-26 -13 -55 -39 -70 -62 -24 -36 -27 -51 -30 -146 -1
                          -58 -5 -116 -8 -128 -2 -13 -44 -54 -98 -98 -55 -44 -101 -89 -110 -109 -32
                          -68 -15 -165 38 -215 13 -12 75 -41 137 -64 l113 -42 41 -107 c22 -59 50 -120
                          62 -136 28 -39 81 -62 138 -62 85 0 110 22 263 220 2 3 61 7 131 10 117 5 132
                          8 168 32 46 31 83 97 83 149 -1 44 -25 96 -89 188 -28 41 -51 80 -51 88 0 7
                          14 61 31 120 42 149 29 214 -55 271 -55 37 -100 37 -229 1 l-116 -32 -93 61
                          c-138 91 -177 100 -256 61z m205 -231 c62 -41 113 -68 129 -68 14 0 72 13 128
                          29 55 16 110 31 121 33 24 4 24 -1 -16 -138 -16 -56 -29 -114 -29 -128 0 -16
                          28 -68 70 -132 39 -57 73 -111 76 -118 4 -10 -25 -14 -137 -19 -164 -6 -150 1
                          -259 -141 -36 -47 -69 -85 -75 -86 -5 0 -30 55 -54 122 -24 66 -52 129 -61
                          138 -9 9 -72 37 -138 61 -67 24 -122 49 -121 54 0 6 42 43 94 84 52 40 102 82
                          110 91 12 14 17 49 21 146 3 71 7 135 10 142 5 15 -1 18 131 -70z"/>
                          <path d="M3280 3994 c-39 -14 -257 -228 -1647 -1618 l-1602 -1601 -16 -59
                          c-20 -67 -16 -135 11 -193 23 -51 446 -474 497 -497 58 -27 126 -31 193 -11
                          l59 16 1596 1597 c1132 1132 1601 1609 1614 1637 27 58 31 133 10 196 -16 49
                          -40 76 -239 277 -150 152 -235 229 -266 244 -57 28 -149 33 -210 12z m347
                          -366 c217 -217 230 -236 200 -294 -9 -16 -127 -140 -264 -276 l-248 -248 -253
                          253 -252 252 252 251 c139 139 262 257 273 263 11 6 36 9 55 6 29 -4 67 -37
                          237 -207z m-682 -688 l250 -250 -1250 -1250 c-687 -687 -1262 -1255 -1277
                          -1261 -15 -6 -40 -8 -55 -4 -34 8 -416 385 -434 426 -6 16 -8 41 -5 56 5 19
                          396 417 1259 1281 689 688 1254 1252 1257 1252 3 0 118 -113 255 -250z"/>
                          <path d="M4654 3319 c-17 -5 -64 -38 -104 -74 l-74 -66 -115 7 c-111 6 -118 5
                          -150 -17 -49 -34 -72 -70 -78 -121 -4 -38 2 -60 37 -138 l41 -93 -41 -95 c-50
                          -114 -51 -160 -3 -220 45 -56 91 -68 210 -55 l98 11 65 -63 c80 -76 100 -87
                          160 -87 108 0 150 51 183 222 l12 64 90 52 c73 42 94 59 112 94 29 54 29 104
                          0 155 -17 30 -44 52 -112 92 l-90 52 -17 85 c-25 126 -58 176 -129 196 -39 12
                          -53 11 -95 -1z m66 -274 c11 -54 28 -107 37 -118 10 -10 55 -39 101 -64 46
                          -25 82 -46 80 -48 -2 -1 -44 -26 -94 -54 -103 -57 -104 -59 -130 -193 l-17
                          -88 -79 75 c-89 84 -92 85 -232 65 -38 -6 -71 -9 -73 -6 -2 2 14 43 37 91 22
                          48 40 98 40 110 0 13 -18 62 -40 110 -22 49 -39 90 -36 92 2 2 50 -1 105 -7
                          117 -14 113 -16 213 79 35 33 64 58 65 57 2 -1 12 -47 23 -101z"/>
                        </g>
                      </svg>
                    </button>
                  </div>
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
