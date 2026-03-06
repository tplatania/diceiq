const fs = require('fs');
const code = fs.readFileSync('D:/diceiq/iphone/index.html', 'utf8');
// Check for problematic em dashes in JS section only
const scriptMatch = code.match(/<script>([\s\S]*?)<\/script>/);
if (scriptMatch) {
  const js = scriptMatch[1];
  const lines = js.split('\n');
  let found = false;
  lines.forEach((line, i) => {
    if (line.includes('\u2014') || line.includes('\u2013')) {
      console.log('Em dash at line', i+1, ':', line.trim());
      found = true;
    }
  });
  if (!found) console.log('No em dashes found in JavaScript - code should be OK');
}
