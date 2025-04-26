import React from 'react'
import { Route, Routes } from 'react-router-dom'
import ChatbotHome from './pages/ChatbotHome'

const App = () => {
  return (
    <div>
      <Routes>
 
        <Route path ='/chatbothome' element={<ChatbotHome/>}/>
      </Routes>
    </div>
  )
}

export default App
