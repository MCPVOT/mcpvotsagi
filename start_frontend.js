#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

const frontendDir = path.join(__dirname, 'frontend');
console.log('🚀 Starting Ultimate AGI Frontend...');
console.log(`📁 Frontend directory: ${frontendDir}`);

// Start Next.js dev server
const nextProcess = spawn('npm', ['run', 'dev'], {
  cwd: frontendDir,
  stdio: 'inherit',
  shell: true,
  env: { ...process.env, PORT: '3000' }
});

nextProcess.on('error', (err) => {
  console.error('❌ Failed to start frontend:', err);
});

nextProcess.on('exit', (code) => {
  console.log(`Frontend process exited with code ${code}`);
});

// Handle shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down frontend...');
  nextProcess.kill('SIGINT');
  process.exit(0);
});