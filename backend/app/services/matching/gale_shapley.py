from collections import deque


def stable_match(commuters: list[str], routes: list[str], preferences: dict[str, list[str]]) -> dict[str, str]:
    free = deque(commuters)
    assigned_route_to_commuter: dict[str, str] = {}
    next_choice_index = {c: 0 for c in commuters}

    while free:
        commuter = free.popleft()
        choices = preferences.get(commuter, [])
        if next_choice_index[commuter] >= len(choices):
            continue

        route = choices[next_choice_index[commuter]]
        next_choice_index[commuter] += 1

        if route not in assigned_route_to_commuter:
            assigned_route_to_commuter[route] = commuter
        else:
            # Prototype tie-breaker keeps current occupant.
            free.append(commuter)

    return {commuter: route for route, commuter in assigned_route_to_commuter.items()}
