import collections

# imports from other parts of this app
from classes.pac import PAC, ShortPac

pac_store = collections.deque(maxlen=1000)
pac_store.append(PAC("1337", "test-pac", 0))


def has_pac(uid: str) -> bool:
    return any(pac.uid == uid for pac in pac_store)


def get_pac(uid: str) -> PAC:
    for pac in pac_store:
        if pac.uid == uid:
            return pac
    raise KeyError(f"PAC with UID {uid} not found")


def add_pac(pac: PAC):
    for existing in pac_store:
        if existing.id == pac.uid:
            pac_store.remove(existing)
            break
    pac_store.append(pac)


def list_pac() -> list[ShortPac]:
    return [pac.simple() for pac in pac_store]
