import { callable } from "@decky/api";

// Thin wrappers around backend methods defined in main.py.
export const ping = callable<[], string>("ping");
