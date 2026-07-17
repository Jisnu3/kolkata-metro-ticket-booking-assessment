import heapq
from app.db.sqlite_client import get_sqlite_conn

def get_metro_route(source_name: str, destination_name: str):
    """
    Computes the shortest route (based on travel time) between the source and 
    destination metro stations using Dijkstra's algorithm.
    Reads station, connection, and interchange graphs dynamically from SQLite.
    """
    with get_sqlite_conn() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, line FROM stations")
        stations = cursor.fetchall()
        station_map = {}

        for row in stations:
            station_map[row["id"]] = {
                "name": row["name"],
                "line": row["line"]
            }

        # Find all matching source and destination IDs (case-insensitive)
        source_ids = [
            sid for sid, s in station_map.items() 
            if s["name"].lower() == source_name.lower()
        ]
        destination_ids = [
            sid for sid, s in station_map.items() 
            if s["name"].lower() == destination_name.lower()
        ]

        if not source_ids:
            raise ValueError(f"Source station '{source_name}' not found")

        if not destination_ids:
            raise ValueError(f"Destination station '{destination_name}' not found")

        # Load connections (same-line train edges)
        cursor.execute("""
            SELECT station_a_id, station_b_id, travel_time_minutes, fare_inr
            FROM connections
        """)
        connections = cursor.fetchall()

        # Load interchanges (cross-line transfers)
        cursor.execute("""
            SELECT station_from_id, station_to_id, transfer_time_minutes
            FROM interchanges
        """)
        interchanges = cursor.fetchall()

        # Build graph
        # graph[u] = list of (v, travel_time, fare, is_interchange)
        graph = {sid: [] for sid in station_map}

        for row in connections:
            a = row["station_a_id"]
            b = row["station_b_id"]
            time = row["travel_time_minutes"]
            fare = row["fare_inr"]
            if a in graph and b in graph:
                graph[a].append((b, time, fare, False))

        for row in interchanges:
            a = row["station_from_id"]
            b = row["station_to_id"]
            time = row["transfer_time_minutes"]
            # Interchanges are pedestrian transfers (no fare)
            if a in graph and b in graph:
                graph[a].append((b, time, 0, True))

        # Dijkstra algorithm
        pq = []  # Elements: (current_time, current_station_id)
        distance = {sid: float("inf") for sid in station_map}
        parent = {sid: None for sid in station_map}
        edge_taken = {sid: None for sid in station_map}  # sid -> (prev_sid, time, fare, is_interchange)

        # Handle edge case where source and destination are physically the same
        if source_name.lower() == destination_name.lower():
            # Pick any source node
            first_src = source_ids[0]
            return {
                "route_summary": {
                    "source": station_map[first_src]["name"],
                    "destination": station_map[first_src]["name"],
                    "total_fare_inr": 0,
                    "total_travel_time_minutes": 0,
                    "interchanges_count": 0
                },
                "ordered_itinerary": [
                    {
                        "station_name": station_map[first_src]["name"],
                        "line": station_map[first_src]["line"],
                        "is_interchange": False,
                        "transfer_to": None
                    }
                ]
            }

        # Initialize all starting nodes matching the source name with distance 0
        for src_id in source_ids:
            distance[src_id] = 0
            heapq.heappush(pq, (0, src_id))

        end_station_id = None

        while pq:
            current_time, u = heapq.heappop(pq)

            if current_time > distance[u]:
                continue

            if u in destination_ids:
                end_station_id = u
                break

            for v, travel_time, fare, is_interchange in graph.get(u, []):
                new_time = current_time + travel_time
                if new_time < distance[v]:
                    distance[v] = new_time
                    parent[v] = u
                    edge_taken[v] = (u, travel_time, fare, is_interchange)
                    heapq.heappush(pq, (new_time, v))

        if end_station_id is None:
            raise ValueError(f"No route found between '{source_name}' and '{destination_name}'")

        # Reconstruct path
        path = []
        curr = end_station_id
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

        # Calculate summaries and itinerary details
        total_time = distance[end_station_id]
        total_fare = 0
        interchange_count = 0

        # Build itinerary representation
        ordered_itinerary = []
        for i in range(len(path)):
            curr_id = path[i]
            station_info = station_map[curr_id]
            
            # Determine if this step leads to an interchange
            is_interchange = False
            transfer_to = None
            
            if i < len(path) - 1:
                next_id = path[i + 1]
                # Look up edge details in edge_taken or check next node's line
                # If they have the same name but different lines, it's a transfer
                curr_name = station_map[curr_id]["name"]
                next_name = station_map[next_id]["name"]
                if curr_name.lower() == next_name.lower():
                    is_interchange = True
                    transfer_to = station_map[next_id]["line"]
                    interchange_count += 1

            # Accumulate fare (if we came from a previous node, add edge fare)
            if i > 0:
                edge = edge_taken[curr_id]
                if edge:
                    total_fare += edge[2]

            ordered_itinerary.append({
                "station_name": station_info["name"],
                "line": station_info["line"],
                "is_interchange": is_interchange,
                "transfer_to": transfer_to
            })

        # Match names exactly from db
        actual_source = station_map[path[0]]["name"]
        actual_dest = station_map[path[-1]]["name"]

        return {
            "route_summary": {
                "source": actual_source,
                "destination": actual_dest,
                "total_fare_inr": total_fare,
                "total_travel_time_minutes": total_time,
                "interchanges_count": interchange_count
            },
            "ordered_itinerary": ordered_itinerary
        }