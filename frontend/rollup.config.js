import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import babel from '@rollup/plugin-babel';
import replace from '@rollup/plugin-replace';
import postcss from 'rollup-plugin-postcss';
import { readFileSync } from 'fs';

const production = process.env.NODE_ENV === 'production';

export default {
  input: 'src/main.jsx',
  output: {
    file: 'dist/assets/index.js',
    format: 'es',
    sourcemap: !production
  },
  plugins: [
    replace({
      'process.env.NODE_ENV': JSON.stringify(production ? 'production' : 'development'),
      preventAssignment: true
    }),
    resolve({
      extensions: ['.js', '.jsx'],
      browser: true
    }),
    commonjs(),
    babel({
      babelHelpers: 'bundled',
      exclude: 'node_modules/**',
      presets: ['@babel/preset-react'],
      extensions: ['.js', '.jsx']
    }),
    postcss({
      extract: 'dist/assets/index.css',
      minimize: production
    }),
    {
      name: 'copy-html',
      generateBundle() {
        const html = readFileSync('index.html', 'utf-8')
          .replace(
            /<script type="module" crossorigin src=".*"><\/script>/,
            '<script type="module" crossorigin src="/assets/index.js"></script>'
          )
          .replace(
            /<link rel="stylesheet" crossorigin href=".*">/,
            '<link rel="stylesheet" crossorigin href="/assets/index.css">'
          );
        this.emitFile({
          type: 'asset',
          fileName: '../index.html',
          source: html
        });
      }
    }
  ],
  external: []
};
