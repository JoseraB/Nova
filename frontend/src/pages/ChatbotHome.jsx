import React from 'react'
import {assets} from '../assets/assets'



const ChatbotHome = () => {
  return (
    <div className='w-full h-screen relative '>


      <div className="absolute inset-0 flex justify-center items-center overflow-hidden">
        <img 
          src={assets.NOVA}
          alt="NOVA"
          className='object-contain w-[80vw] h-[80vw] opacity-70'   
        />


      
        <div className='absolute top-0 left-0 w-full h-full flex flex-col items-center justify-center space-y-5'>
          <div className="flex items-center space-x-5">
            <img
              src={assets.Knight}
              alt="Knight"
              className='w-[5.5em] h-[5em]'
            />

            <h1 className="text-8xl font-bold tracking-[.25em] ]">
              NOVA
            </h1>
          </div>





          <div className="flex items-center space-x-2">
            <textarea type="text" 
            placeholder="Hi! What can I assist you with today?"
            className="border-2 border-gray-300 rounded-2xl px-4 py-2 h-[10em] w-[37.5em] bg-[#eeeeee] align-top text-start shadow-md"
            />
            
          </div>
        </div>
        
      </div>
      <div className= 'flex justify-between p-3'>

          <img
            src={assets.Settings}
            alt="Settings"
            className=' w-[3em] h-[3em]'
          />

          <img
          src= {assets.Adminicon}
          alt="Adminicon"
          className=' w-[3em] h-[3em]'
          />
      </div>
      
    </div>
  )
}

export default ChatbotHome
