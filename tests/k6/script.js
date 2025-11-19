import http from 'k6/http';
import { sleep, check } from 'k6';

// Setup test options
export let options = {
  vus: 5,
  duration: '20s',
};

export default function () {
  const url = 'http://127.0.0.1:8000/analyze';

  // Create multipart/form-data payload
  const formData = {
    branch: 'main',
    commit: 'test123',
    recipients: 'youremail@example.com',
    // Dummy file upload (text file content)
    files: http.file('Sample test content', 'report1.json'),
  };

  const res = http.post(url, formData);

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1);
}
