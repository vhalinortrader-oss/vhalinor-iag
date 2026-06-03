import fs from 'fs';
import path from 'path';

const sourcePath = 'src/main/java/com/agi/automation/AGIAutomationEngine_V1.java';
const targetPath = 'src/main/java/com/trading/ai/core/AGIAutomationEngine.java';

let content = fs.readFileSync(sourcePath, 'utf8');

// Fix package
content = content.replace('package com.agi.automation;', 'package com.trading.ai.core;');

// Fix enum syntax errors: "),;" -> "),"
content = content.replace(/\"\),;/g, '"),');

// Write to new location
fs.writeFileSync(targetPath, content);

// Delete old directory
fs.rmSync('src/main/java/com/agi', { recursive: true, force: true });

console.log('Fixed and moved AGIAutomationEngine');
