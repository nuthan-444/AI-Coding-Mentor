/**
 * Auth routes — signup, login, logout, /api/me
 */
const express = require('express');
const router  = express.Router();
const User    = require('../models/User');

// POST /signup
router.post('/signup', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password)
      return res.status(400).json({ success: false, message: 'Email and password required.' });
    if (password.length < 6)
      return res.status(400).json({ success: false, message: 'Password must be at least 6 characters.' });

    const existing = await User.findOne({ email });
    if (existing)
      return res.status(409).json({ success: false, message: 'Email already registered.' });

    const user = new User({ email, password });
    await user.save();

    // Auto-login after signup
    req.session.userId = user._id.toString();
    req.session.email  = user.email;

    res.json({ success: true, message: 'Account created.' });
  } catch (err) {
    console.error('[signup]', err.message);
    console.log(err)
    res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// POST /login
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password)
      return res.status(400).json({ success: false, message: 'Email and password required.' });

    const user = await User.findOne({ email });
    if (!user)
      return res.status(401).json({ success: false, message: 'Invalid email or password.' });

    const ok = await user.comparePassword(password);
    if (!ok)
      return res.status(401).json({ success: false, message: 'Invalid email or password.' });

    req.session.userId = user._id.toString();
    req.session.email  = user.email;

    res.json({ success: true, message: 'Logged in.' });
  } catch (err) {
    console.error('[login]', err.message);
    res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// POST /logout
router.post('/logout', (req, res) => {
  req.session.destroy(() => res.json({ success: true }));
});

// GET /api/me — return current session user
router.get('/api/me', (req, res) => {
  if (!req.session.userId) return res.json({ userId: null });
  res.json({ userId: req.session.userId, email: req.session.email });
});

module.exports = router;