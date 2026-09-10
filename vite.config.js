import { defineConfig } from 'vite';

export default defineConfig({
    build: {
        sourcemap: false,
        minify: false,
        cssMinify: false,
        lib: {
            entry: 'kekule_editor/kekule.js',
            name: 'KekuleEditor',
            fileName: 'kekule-bundle',
            formats: ['es']
        },
        outDir: 'titular',
        emptyOutDir: false,
        rollupOptions: {
            output: {
                codeSplitting: false,
                entryFileNames: 'kekule-bundle.js',
                assetFileNames: '[name][extname]',
            }
        }
    },
});