# Initial SvelteKit SPA Setup

Use this for new Isaac-stack frontends. Refer to `ik-connectrpc` for protobuf, ConnectRPC, and generated client setup.

1. Ensure `bun` is available.
2. Run:

   ```bash
   bun x sv create <app-name> --template minimal --types ts --install bun --add eslint prettier vitest tailwindcss sveltekit-adapter
   ```

3. Choose the default Vitest and Tailwind prompts. For the SvelteKit adapter prompt, choose `adapter-static`.
4. Create `src/routes/+layout.ts`:

   ```ts
   export const ssr = false;
   export const prerender = true;
   ```

5. Configure `svelte.config.js`:

   ```js
   import adapter from "@sveltejs/adapter-static";

   /** @type {import("@sveltejs/kit").Config} */
   const config = {
     kit: {
       adapter: adapter({
         fallback: "index.html",
       }),
       prerender: {
         handleUnseenRoutes: "ignore",
       },
     },
   };

   export default config;
   ```

6. Install shadcn-svelte defaults:

   ```bash
   cp /path/to/plugins/isaac-stack/skills/ik-svelte/references/components.json ./components.json
   bun x shadcn-svelte@latest add --all --yes
   ```

7. Add TanStack Query/Form and ConnectRPC client packages when the first feature needs them.
