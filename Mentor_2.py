import math
import csv
import Node
import MENTOR

def Mentor2_ISP(ListPosition, TrafficMatrix, MAX, C, w, RadiusRatio, Limit, umin=0.8, alpha=0.2, debug=False):
    # 1. Tính Mentor 1 để lấy các nhóm backbone và truy nhập
    ListMentor = MENTOR.MenTor([Node_copy(n) for n in ListPosition], TrafficMatrix, MAX, C, w, RadiusRatio, Limit, debug)

    # 2. Lấy ra các backbone node (node đầu tiên mỗi group)
    backbone_nodes = [group[0] for group in ListMentor if len(group) > 0]
    backbone_names = [n.get_name() for n in backbone_nodes]

    # 3. Xây dựng các liên kết backbone (fully connected)
    backbone_links = []
    for i in range(len(backbone_nodes)):
        for j in range(i+1, len(backbone_nodes)):
            n1, n2 = backbone_nodes[i], backbone_nodes[j]
            backbone_links.append((n1, n2))

    # 4. Tính thông số cho từng liên kết backbone
    link_usage = []
    link_cost = []
    link_cost_changed = []
    link_path_count = []

    for n1, n2 in backbone_links:
        name1, name2 = n1.get_name(), n2.get_name()
        # Giá liên kết là khoảng cách Euclid
        cost = math.sqrt((n1.get_position_x() - n2.get_position_x())**2 + (n1.get_position_y() - n2.get_position_y())**2)
        # Tính tổng lưu lượng đi qua liên kết backbone này
        usage, count = calc_link_usage(name1, name2, backbone_names, TrafficMatrix)
        utilization = usage / C if C > 0 else 0
        # Giá thay đổi theo Mentor 2
        if utilization < umin:
            cost_new = cost * (1 + alpha)
        else:
            cost_new = cost

        # Lưu kết quả
        link_usage.append(utilization)
        link_cost.append(cost)
        link_cost_changed.append(cost_new)
        link_path_count.append(count)

    # Trả về backbone (danh sách node), các thông số liên kết
    return backbone_names, link_path_count, link_cost, link_cost_changed

def calc_link_usage(name1, name2, backbone_names, TrafficMatrix):
    # Đếm tổng lưu lượng và số đường flow từ name1 <-> name2
    idx1 = backbone_names.index(name1)
    idx2 = backbone_names.index(name2)
    usage = 0
    count = 0
    # Tổng các traffic flow giữa hai backbone node (trong traffic matrix)
    for i, src in enumerate(backbone_names):
        for j, dst in enumerate(backbone_names):
            if i == j: continue
            # Nếu flow đi từ src đến dst mà đi qua liên kết (name1,name2)
            # Giả sử backbone fully connected nên flow nào giữa src<->dst cũng đi qua trực tiếp liên kết này nếu (src,dst)==(name1,name2) hoặc (name2,name1)
            if (src == name1 and dst == name2) or (src == name2 and dst == name1):
                f = TrafficMatrix[src-1][dst-1]
                if f > 0:
                    usage += f
                    count += 1
    return usage, count

def write_result(filename, backbone, link_path_count, link_cost, link_cost_changed):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Liên kết\tSố đường\tGiá ban đầu\tGiá thay đổi\n")
        for i in range(len(link_path_count)):
            f.write(f"{backbone[i]}-{backbone[(i+1)%len(backbone)]}\t{link_path_count[i]}\t{link_cost[i]:.2f}\t{link_cost_changed[i]:.2f}\n")

def plot_backbone(ListPosition, backbone, MAX):
    import matplotlib.pyplot as plt
    # Vẽ các node backbone
    for n in ListPosition:
        if n.get_name() in backbone:
            plt.plot(n.get_position_x(), n.get_position_y(), 'ro', markersize=12)
            plt.text(n.get_position_x(), n.get_position_y(), str(n.get_name()), color='white', ha='center', va='center', weight='bold')
        else:
            plt.plot(n.get_position_x(), n.get_position_y(), 'bo', markersize=8)
            plt.text(n.get_position_x(), n.get_position_y(), str(n.get_name()), color='black', ha='center', va='center')
    # Vẽ liên kết backbone (fully connected)
    for i in range(len(backbone)):
        for j in range(i+1, len(backbone)):
            n1 = next(x for x in ListPosition if x.get_name() == backbone[i])
            n2 = next(x for x in ListPosition if x.get_name() == backbone[j])
            plt.plot([n1.get_position_x(), n2.get_position_x()], [n1.get_position_y(), n2.get_position_y()], 'k--')
    plt.title("Backbone Topology (Mentor 2)")
    plt.axis('equal')
    plt.grid(True)

def Node_copy(node):
    # Deep copy cho Node tối giản
    n = Node.Node()
    n.create_name(node.get_name())
    n.set_position(node.get_position_x(), node.get_position_y())
    n.set_traffic(node.get_traffic())
    return n