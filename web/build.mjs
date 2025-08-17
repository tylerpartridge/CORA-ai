import { build } from 'esbuild';
import { createHash } from 'crypto';
import { readFileSync, writeFileSync, mkdirSync, readdirSync, renameSync } from 'fs';
import { join, basename } from 'path';

const outDir = 'static/js/bundles';

// Clean previous build
mkdirSync(outDir, { recursive: true });

await build({
  entryPoints: [
    'static/js/performance.js',
    'static/js/accessibility.js',
    'static/js/error-manager.js',
    'static/js/timeout-handler.js',
    'static/js/web-vitals-monitoring.js',
  ],
  bundle: true,
  minify: true,
  sourcemap: true,
  outdir: outDir,
  splitting: true,
  format: 'esm',
  target: ['es2019'],
  entryNames: '[name]',
  chunkNames: '[name]-[hash]',
});

// Process generated files and create manifest
const files = readdirSync(outDir).filter(f => f.endsWith('.js') && !f.endsWith('.map'));
const manifest = { builtAt: new Date().toISOString(), files: {} };

// Define our expected entry points
const entryPoints = ['performance', 'accessibility', 'error-manager', 'timeout-handler', 'web-vitals-monitoring'];

for (const file of files) {
  const baseName = file.replace('.js', '');
  
  // Check if this is one of our main entry points
  if (entryPoints.includes(baseName)) {
    manifest.files[baseName] = `/static/js/bundles/${file}`;
  }
}

writeFileSync(join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 2));

console.log('Build complete. Bundles in', outDir);
console.log('Generated files:', files);
console.log('Manifest:', JSON.stringify(manifest, null, 2));

