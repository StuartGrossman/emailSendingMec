const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'dist')));

// Email sending endpoint
app.post('/api/send-email', async (req, res) => {
  try {
    const { to, subject, message } = req.body;

    // Validate input
    if (!to || !subject || !message) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Call Python script to send email
    const pythonProcess = spawn('python3', [
      'send_email.py',
      to,
      subject,
      message
    ]);

    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('Python script error:', error);
        return res.status(500).json({ error: 'Failed to send email' });
      }
      res.json({ success: true, message: 'Email sent successfully' });
    });
  } catch (error) {
    console.error('Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Serve the React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
}); 