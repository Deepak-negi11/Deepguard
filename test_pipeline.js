const http = require('http');

async function testPipeline() {
  const baseUrl = 'http://localhost:8000/api/v1';
  let token = '';

  // 1. Register
  console.log('1. Registering user...');
  try {
    const regRes = await fetch(`${baseUrl}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'tester.final@deepguard.com',
        password: 'securepassword123',
        full_name: 'Final Tester',
      }),
    });
    console.log('Register status:', regRes.status);
  } catch (e) {
    console.log('Register failed (perhaps already exists)');
  }

  // 2. Login
  console.log('\n2. Logging in...');
  const loginRes = await fetch(`${baseUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'tester.final@deepguard.com',
      password: 'securepassword123',
    }),
  });
  if (!loginRes.ok) {
    console.error('Login failed!', await loginRes.text());
    return;
  }
  const loginData = await loginRes.json();
  token = loginData.access_token;
  console.log('Login successful. Got token.');

  // 3. Submit Task
  console.log('\n3. Submitting task...');
  const verifyRes = await fetch(`${baseUrl}/verify/news`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      url: 'https://example.com/test-news',
      text: 'This is a test fake news article. Scientists have cloned dinosaurs!',
    }),
  });
  if (!verifyRes.ok) {
    console.error('Task submission failed!', await verifyRes.text());
    return;
  }
  const verifyData = await verifyRes.json();
  const taskId = verifyData.task_id;
  console.log('Task submitted! Task ID:', taskId);

  // 4. Poll for results
  console.log('\n4. Polling for results...');
  while (true) {
    const resRes = await fetch(`${baseUrl}/results/${taskId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!resRes.ok) {
      console.error('Polling failed!', await resRes.text());
      break;
    }
    const resultData = await resRes.json();
    console.log('Current status:', resultData.status);
    if (resultData.status === 'completed' || resultData.status === 'failed') {
      console.log('Final Result Data:', JSON.stringify(resultData, null, 2));
      break;
    }
    // wait 1.5 seconds
    await new Promise(r => setTimeout(r, 1500));
  }
}

testPipeline().catch(console.error);
