import React from 'react'
import {assets} from '../assets/assets'

const ChatbotHome = () => {
  return (
    <div className='w-full h-screen relative'>
      <div className="absolute inset-0 flex justify-center items-center overflow-hidden">
        <img 
          src={assets.NOVA}
          alt="NOVA"
          className='object-contain'   
        />
        <div className="absolute items-center">
          <h1 className="text-7xl font-bold tracking-[.25em]">
            NOVA
          </h1>
        </div>
      </div>
    </div>
  )
}

export default ChatbotHome
