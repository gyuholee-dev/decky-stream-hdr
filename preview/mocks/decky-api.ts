// Stand-in for @decky/api in the browser preview.
import { call } from "../backend";

export function callable<_Args extends unknown[], Result>(name: string) {
  return (...args: _Args): Promise<Result> => call(name, args as unknown[]) as Promise<Result>;
}

// The real definePlugin hands the plugin definition to Decky; here it is just returned.
export function definePlugin<T>(factory: () => T): T {
  return factory();
}
