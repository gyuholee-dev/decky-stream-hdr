// A tiny stand-in for Steam's router, so the preview can show pages that the plugin registers
// (routerHook.addRoute) and the navigation between them (Navigation.Navigate / NavigateBack).
import type { ComponentType } from "react";

const routes = new Map<string, ComponentType>();
let current: string | null = null;
const listeners = new Set<() => void>();

const emit = () => listeners.forEach((listener) => listener());

export const router = {
  addRoute(path: string, component: ComponentType) {
    routes.set(path, component);
  },
  removeRoute(path: string) {
    routes.delete(path);
    if (current === path) current = null;
    emit();
  },
  navigate(path: string) {
    current = path;
    emit();
  },
  back() {
    current = null;
    emit();
  },
  // For useSyncExternalStore.
  subscribe(listener: () => void) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
  currentPath: () => current,
  currentComponent: () => (current ? routes.get(current) ?? null : null),
};
