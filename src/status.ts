import { addEventListener, removeEventListener } from "@decky/api";
import { useEffect, useRef, useState } from "react";

import { getStatus, Status } from "./api";

// The values a user changes in the panel. While a change of theirs is still on its way to the backend,
// an event must not put an older value back.
const USER_VALUES = ["hdr_enabled", "paper_white", "contrast", "gamma", "saturation"] as const;

// The backend's status, kept up to date: it is read once when the component appears, and after that the
// backend sends an event whenever something changes on its own (a stream starts or ends, the wrapper is
// repaired). Nothing asks the backend over and over.
export function useStatus() {
  const [status, setStatus] = useState<Status | undefined>();
  const [failed, setFailed] = useState(false);
  const latest = useRef(0); // number of the newest request
  const pending = useRef(0); // requests that have not been answered yet

  useEffect(() => {
    let alive = true;
    getStatus()
      .then((current) => alive && setStatus((previous) => previous ?? current))
      .catch(() => alive && setFailed(true));

    const onEvent = (next: Status) => {
      if (!alive) return;
      setStatus((previous) => {
        if (!previous || pending.current === 0) return next;
        const kept: Partial<Status> = {};
        for (const key of USER_VALUES) Object.assign(kept, { [key]: previous[key] });
        return { ...next, ...kept };
      });
    };
    addEventListener<[Status]>("status", onEvent);
    return () => {
      alive = false;
      removeEventListener("status", onEvent);
    };
  }, []);

  // A reply that a newer change has overtaken is dropped, or a control would jump back to an old value
  // while the user is still dragging it.
  const send = (request: Promise<Status>) => {
    const id = ++latest.current;
    pending.current += 1;
    request
      .then((reply) => {
        if (id === latest.current) setStatus(reply);
      })
      .catch(() => setFailed(true))
      .finally(() => {
        pending.current -= 1;
      });
  };

  // Shows a change at once, then sends it to the backend.
  const change = (patch: Partial<Status>, request: Promise<Status>) => {
    setStatus((current) => (current ? { ...current, ...patch } : current));
    send(request);
  };

  return { status, failed, send, change };
}
