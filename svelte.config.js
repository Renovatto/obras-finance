import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	compilerOptions: {
		// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
		runes: ({ filename }) => (filename.split(/[/\\]/).includes('node_modules') ? undefined : true)
	},
	kit: {
		// adapter-static is used for SPA (Single Page Application) mode
		adapter: adapter({
			pages: 'backend/dist',
			assets: 'backend/dist',
			fallback: 'index.html', // multi-page SPA fallback
			precompress: false,
			strict: true
		})
	}
};

export default config;
