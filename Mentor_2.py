import math
import csv
import Node
import MENTOR
import networkx as nx

def prim_dijkstra_backbone_links(ListPosition, backbone_nodes):
    # Xây dựng đồ thị đầy đủ giữa các backbone node, trọng số là đường đi ngắn nhất (Dijkstra) trên đồ thị gốc
    G = nx.Graph()
    node_map = {n.get_name(): n for n in ListPosition}
    backbone_names = [n.get_name() for n in backbone_nodes]
    # Tạo đồ thị gốc (fully connected, trọng số là Euclid)
    G_full = nx.Graph()
    for i in range(len(ListPosition)):
        for j in range(i+1, len(ListPosition)):
            n1, n2 = ListPosition[i], ListPosition[j]
            cost = math.sqrt((n1.get_position_x() - n2.get_position_x())**2 + (n1.get_position_y() - n2.get_position_y())**2)
            G_full.add_edge(n1.get_name(), n2.get_name(), weight=cost)
    # Tạo đồ thị backbone, trọng số là đường đi ngắn nhất trên G_full
    for i in range(len(backbone_names)):
        for j in range(i+1, len(backbone_names)):
            src, dst = backbone_names[i], backbone_names[j]
            length = nx.dijkstra_path_length(G_full, src, dst, weight='weight')
            G.add_edge(src, dst, weight=length)
    # Prim trên đồ thị backbone
    mst = nx.minimum_spanning_tree(G, weight='weight')
    # Trả về danh sách cặp node (Node object)
    links = []
    for u, v in mst.edges():
        links.append((node_map[u], node_map[v]))
    return links

def Mentor2_ISP(ListPosition, TrafficMatrix, MAX, C, w, RadiusRatio, Limit, umin=0.8, alpha=0.2, debug=False):
    # 1. Tính Mentor 1 để lấy các nhóm backbone và truy nhập
    ListMentor = MENTOR.MenTor([Node_copy(n) for n in ListPosition], TrafficMatrix, MAX, C, w, RadiusRatio, Limit, debug)

    # 2. Lấy ra các backbone node (node đầu tiên mỗi group)
    backbone_nodes = [group[0] for group in ListMentor if len(group) > 0]
    backbone_names = [n.get_name() for n in backbone_nodes]

    # 3. Xây dựng các liên kết backbone theo Prim-Dijkstra
    backbone_links = prim_dijkstra_backbone_links(ListPosition, backbone_nodes)

    # Tạo đồ thị backbone từ các liên kết backbone
    backbone_graph = nx.Graph()
    for n1, n2 in backbone_links:
        backbone_graph.add_edge(n1.get_name(), n2.get_name())

    link_usage = []
    link_cost = []
    link_cost_changed = []
    link_path_count = []

    for n1, n2 in backbone_links:
        name1, name2 = n1.get_name(), n2.get_name()
        cost = math.sqrt((n1.get_position_x() - n2.get_position_x())**2 + (n1.get_position_y() - n2.get_position_y())**2)
        # truyền backbone_graph vào
        usage, count = calc_link_usage(name1, name2, backbone_names, TrafficMatrix, backbone_graph, ListMentor)
        utilization = usage / C if C > 0 else 0
        if utilization < umin:
            cost_new = cost * (1 + alpha)
        else:
            cost_new = cost
        link_usage.append(utilization)
        link_cost.append(cost)
        link_cost_changed.append(cost_new)
        link_path_count.append(count)

    return backbone_names, link_path_count, link_cost, link_cost_changed, link_usage

def find_backbone_of_node(node_id, ListMentor):
    for group in ListMentor:
        if node_id in [n.get_name() for n in group]:
            return group[0].get_name()
    return None

def calc_link_usage(name1, name2, backbone_names, TrafficMatrix, backbone_graph, ListMentor):
    usage = 0
    count = 0
    n = len(TrafficMatrix)
    for src in range(1, n+1):
        for dst in range(1, n+1):
            if src == dst:
                continue
            flow = TrafficMatrix[src-1][dst-1]
            if flow > 0:
                b_src = find_backbone_of_node(src, ListMentor)
                b_dst = find_backbone_of_node(dst, ListMentor)
                if b_src is None or b_dst is None or b_src == b_dst:
                    continue
                try:
                    path = nx.shortest_path(backbone_graph, source=b_src, target=b_dst)
                    for i in range(len(path)-1):
                        u, v = path[i], path[i+1]
                        if (u == name1 and v == name2) or (u == name2 and v == name1):
                            usage += flow
                            count += 1
                            break
                except nx.NetworkXNoPath:
                    continue
    return usage, count

def write_result(filename, backbone, link_path_count, link_cost, link_cost_changed, link_usage):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Liên kết\tSố đường\tĐộ sử dụng\tGiá ban đầu\tGiá thay đổi\n")
        for i in range(len(link_path_count)):
            f.write(f"{backbone[i]}-{backbone[(i+1)%len(backbone)]}\t{link_path_count[i]}\t{link_usage[i]:.2f}\t{link_cost[i]:.2f}\t{link_cost_changed[i]:.2f}\n")

def plot_backbone(ListPosition, backbone_links, MAX):
    import matplotlib.pyplot as plt
    # Vẽ các node backbone
    backbone_names = set()
    for n1, n2 in backbone_links:
        backbone_names.add(n1.get_name())
        backbone_names.add(n2.get_name())
    for n in ListPosition:
        if n.get_name() in backbone_names:
            plt.plot(n.get_position_x(), n.get_position_y(), 'ro', markersize=12)
            plt.text(n.get_position_x(), n.get_position_y(), str(n.get_name()), color='white', ha='center', va='center', weight='bold')
        else:
            plt.plot(n.get_position_x(), n.get_position_y(), 'bo', markersize=8)
            plt.text(n.get_position_x(), n.get_position_y(), str(n.get_name()), color='black', ha='center', va='center')
    # Vẽ liên kết backbone theo cây Prim-Dijkstra
    for n1, n2 in backbone_links:
        plt.plot([n1.get_position_x(), n2.get_position_x()],
                 [n1.get_position_y(), n2.get_position_y()], 'k-', linewidth=2)
    plt.title("Backbone Topology (Mentor 2 - Prim-Dijkstra)")
    plt.axis('equal')
    plt.grid(True)

def Node_copy(node):
    # Deep copy cho Node tối giản
    n = Node.Node()
    n.create_name(node.get_name())
    n.set_position(node.get_position_x(), node.get_position_y())
    n.set_traffic(node.get_traffic())
    return n

# Không nên để đoạn này trong Mentor_2.py:
# backbone, link_path_count, link_cost, link_cost_changed, link_usage = Mentor2_ISP(
#     ListPosition, TrafficMatrix, MAX, C, w, RadiusRatio, Limit
# )
# write_result('mentor2_result.txt', backbone, link_path_count, link_cost, link_cost_changed, link_usage)
