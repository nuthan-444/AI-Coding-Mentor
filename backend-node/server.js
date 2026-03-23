require('dotenv').config();
const express    = require('express');
const session    = require('express-session');
const MongoStore = require('connect-mongo');
const mongoose   = require('mongoose');
const path       = require('path');

const authRoutes = require('./routes/auth');
const apiRoutes  = require('./routes/api');

const app  = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(session({
  secret: process.env.SESSION_SECRET || 'dev-secret-change-in-prod',
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({
    mongoUrl: process.env.MONGO_URI || 'mongodb://localhost:27017/coding-mentor',
    touchAfter: 24 * 3600
  }),
  cookie: {
    maxAge: 7 * 24 * 60 * 60 * 1000,
    httpOnly: true,
    sameSite: 'lax'
  }
}));

// ✅ Log every request to debug
app.use((req, res, next) => {
  console.log(`[${req.method}] ${req.path}`);
  next();
});

// ✅ Mount routes
app.use('/', authRoutes);
app.use('/', apiRoutes);

// ✅ Static files
app.use(express.static(path.join(__dirname, '../frontend')));

// ✅ Catch-all
app.use((req, res) => {
  if (req.method === 'POST' || req.path.startsWith('/api')) {
    return res.status(404).json({ message: `Route not found: ${req.method} ${req.path}` });
  }
  res.sendFile(path.join(__dirname, '../frontend', 'index.html'));
});

mongoose.connect(process.env.MONGO_URI || 'mongodb://localhost:27017/coding-mentor')
  .then(() => {
    console.log('✅ MongoDB connected');
    app.listen(PORT, () => {
      console.log(`🚀 Node server running → http://localhost:${PORT}`);
      // ✅ Print all registered routes
      console.log('\n📋 Registered routes:');
      app._router.stack.forEach(r => {
        if (r.route) {
          console.log(`  ${Object.keys(r.route.methods)[0].toUpperCase()} ${r.route.path}`);
        } else if (r.name === 'router') {
          r.handle.stack.forEach(h => {
            if (h.route) {
              console.log(`  ${Object.keys(h.route.methods)[0].toUpperCase()} ${h.route.path}`);
            }
          });
        }
      });
    });
  })
  .catch(err => {
    console.error('❌ MongoDB connection failed:', err.message);
    process.exit(1);
  });