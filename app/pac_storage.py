"""This File contains all Utility to implement and Interact with a simple, in-memory PAC-Store.
The Store consists of a ring-buffer that holds the last 1000 PACs, referenced by Unique ID."""

import collections
from apiflask import APIFlask

# imports from other parts of this app
from classes.pac import PAC, ShortPac


pac_store: collections.deque[PAC] = None
def init_store(app: APIFlask):
    global pac_store
    # set a max cache size based on an environment variable
    pac_store = collections.deque(maxlen=app.config.get('MAX_CACHE', 1000))


def has_pac(uid: str) -> bool:
    return any(pac.uid == uid for pac in pac_store)


def get_pac(uid: str) -> PAC:
    for pac in pac_store:
        if pac.uid == uid:
            return pac
    raise KeyError(f"PAC with UID {uid} not found")


def add_pac(pac: PAC):
    for existing in pac_store:
        if existing.uid == pac.uid:
            pac_store.remove(existing)
            break
    pac_store.append(pac)


def list_pac() -> list[ShortPac]:
    return [pac.simple() for pac in pac_store]
