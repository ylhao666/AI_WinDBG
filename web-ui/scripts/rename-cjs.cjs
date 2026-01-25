const fs = require('fs');
const path = require('path');

const files = ['main', 'preload'];
const distDir = path.join(__dirname, 'dist-electron');

files.forEach(file => {
  const jsFile = path.join(distDir, `${file}.js`);
  const cjsFile = path.join(distDir, `${file}.cjs`);

  if (fs.existsSync(jsFile)) {
    try {
      fs.renameSync(jsFile, cjsFile);
      console.log(`Renamed: ${file}.js -> ${file}.cjs`);
    } catch (error) {
      console.error(`Error renaming ${file}.js:`, error.message);
    }
  }
});
