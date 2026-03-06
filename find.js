const fs = require('fs');
const code = fs.readFileSync('D:/diceiq/iphone/index.html', 'utf8');
const lines = code.split('\n');
lines.forEach((line, i) => {
  if (line.includes('return html')) console.log(i+1, line.trim());
});
