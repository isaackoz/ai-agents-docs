Use this pattern in `src/hooks.client.ts` when client-side SvelteKit errors may wrap ConnectRPC errors.

Adjust auth redirection and the returned error shape to the target app.

```ts
import { Code, ConnectError } from "@connectrpc/connect";
import type { HandleClientError } from "@sveltejs/kit";

import { redirectToAuthLogin } from "$lib/utils";

export const handleError: HandleClientError = async ({
  error,
  event,
  message,
  status,
}) => {
  if (error instanceof ConnectError) {
    status = mapCodeToStatus(error.code);
    message = error.message;
    if (error.code === Code.Unauthenticated) {
      redirectToAuthLogin();
    }
  }

  return {
    error,
    event,
    message,
    status,
    code: error instanceof ConnectError ? error.code : Code.Unknown,
  };
};

function mapCodeToStatus(code: Code): number {
  switch (code) {
    case Code.Unauthenticated:
      return 401;
    case Code.PermissionDenied:
      return 403;
    case Code.NotFound:
      return 404;
    case Code.Internal:
      return 500;
    default:
      return 500;
  }
}
```

Modify `src/app.d.ts` for type safety when the app reads the error code.

```ts
import type { UserMe } from "$lib/contexts/auth.svelte";
import type { Code } from "@connectrpc/connect";

declare global {
  namespace App {
    interface Error {
      message: string;
      code: Code;
    }

    interface PageData {
      user: UserMe | null;
    }
  }
}

export {};
```
