const express = require('express');
const router  = express.Router();
const axios   = require('axios');

const PYTHON_URL = process.env.PYTHON_URL || 'http://localhost:8000';

// ── Auth middleware ───────────────────────────────────────────
function requireAuth(req, res, next) {
  console.log('Session check:', req.session.userId);
  if (!req.session || !req.session.userId) {
    return res.status(401).json({ message: 'Not authenticated. Please log in.' });
  }
  next();
}

// ── Python POST helper ────────────────────────────────────────
async function callPythonPost(endpoint, payload) {
  console.log(`[Python POST] ${PYTHON_URL}${endpoint}`, payload);
  const res = await axios.post(`${PYTHON_URL}${endpoint}`, payload, {
    timeout: 60000,
    headers: { 'Content-Type': 'application/json' }
  });
  return res.data;
}

// ── Python GET helper ─────────────────────────────────────────
async function callPythonGet(endpoint, params) {
  console.log(`[Python GET] ${PYTHON_URL}${endpoint}`, params);
  const res = await axios.get(`${PYTHON_URL}${endpoint}`, {
    params,
    timeout: 60000
  });
  return res.data;
}

// ─────────────────────────────────────────────────────────────
// ✅ POST /analyze
// ─────────────────────────────────────────────────────────────
router.post('/analyze', requireAuth, async (req, res) => {
  console.log('✅ /analyze hit by user:', req.session.userId);
  try {
    const { code, language } = req.body;
    if (!code) return res.status(400).json({ message: 'Code is required.' });

    const data = await callPythonPost('/analyze', {
      code,
      language: language || 'python',
      userId: req.session.userId
    });
    res.json(data);
  } catch (err) {
    console.error('[/analyze error]', err.message);
    res.status(500).json({
      message: err.response?.data?.detail || err.message || 'Analysis failed.'
    });
  }
});

// ─────────────────────────────────────────────────────────────
// ✅ POST /practice
// ─────────────────────────────────────────────────────────────
router.post('/practice', requireAuth, async (req, res) => {
  console.log('✅ /practice hit by user:', req.session.userId);
  try {
    const data = await callPythonPost('/generate-test', {
      userId: req.session.userId
    });
    res.json(data);
  } catch (err) {
    console.error('[/practice error]', err.message);
    res.status(500).json({
      message: err.response?.data?.detail || err.message || 'Failed to generate test.'
    });
  }
});

// ─────────────────────────────────────────────────────────────
// ✅ POST /submit-test
// ─────────────────────────────────────────────────────────────
router.post('/submit-test', requireAuth, async (req, res) => {
  console.log('✅ /submit-test hit by user:', req.session.userId);
  try {
    const { question, answer, questionIndex } = req.body;
    if (!question || answer === undefined)
      return res.status(400).json({ message: 'Question and answer required.' });

    const data = await callPythonPost('/evaluate-test', {
      userId: req.session.userId,
      question,
      answer,
      questionIndex
    });
    res.json(data);
  } catch (err) {
    console.error('[/submit-test error]', err.message);
    res.status(500).json({
      message: err.response?.data?.detail || err.message || 'Evaluation failed.'
    });
  }
});

// ─────────────────────────────────────────────────────────────
// ✅ GET /weaknesses
// ─────────────────────────────────────────────────────────────
router.get('/weaknesses', requireAuth, async (req, res) => {
  console.log('✅ /weaknesses hit by user:', req.session.userId);
  try {
    const data = await callPythonGet('/weaknesses', {
      userId: req.session.userId
    });
    res.json(data);
  } catch (err) {
    console.error('[/weaknesses error]', err.message);
    res.json({ weaknesses: [] });
  }
});

module.exports = router;