import { useState } from 'react'
import './App.css'

function App() {
  const [email, setEmail] = useState('')
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')
  const [status, setStatus] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setStatus('Sending...')

    try {
      const response = await fetch('/api/send-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to: email,
          subject,
          message,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setStatus('Email sent successfully!')
        setEmail('')
        setSubject('')
        setMessage('')
      } else {
        setStatus(`Error: ${data.error}`)
      }
    } catch (error) {
      setStatus('Error sending email. Please try again.')
    }
  }

  return (
    <div className="container">
      <h1>Email Sender</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">To:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="subject">Subject:</label>
          <input
            type="text"
            id="subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="message">Message:</label>
          <textarea
            id="message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
          />
        </div>
        <button type="submit">Send Email</button>
      </form>
      {status && <p className="status">{status}</p>}
    </div>
  )
}

export default App 