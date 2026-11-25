// Stand-in for @decky/api in the browser preview.
import { call, subscribe } from "../backend";
import { router } from "../router";

export function callable<_Args extends unknown[], Result>(name: string) {
  return (...args: _Args): Promise<Result> => call(name, args as unknown[]) as Promise<Result>;
}

// The real definePlugin hands the plugin definition to Decky; here it is just returned.
export function definePlugin<T>(factory: () => T): T {
  return factory();
}

// Pages registered by the plugin are shown by the preview (see preview/main.tsx).
export const routerHook = {
  addRoute: router.addRoute,
  removeRoute: router.removeRoute,
};

// The backend's events. The preview has one: "status".
const unsubscribe = new Map<(...args: any[]) => any, () => boolean>();

export function addEventListener<Args extends any[] = []>(event: string, listener: (...args: Args) => any) {
  if (event === "status") unsubscribe.set(listener, subscribe(listener as never));
  return listener;
}

export function removeEventListener<Args extends any[] = []>(_event: string, listener: (...args: Args) => any) {
  unsubscribe.get(listener)?.();
  unsubscribe.delete(listener);
}
