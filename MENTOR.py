# Thư viện
import random
import math
import matplotlib.pyplot as plt
import Node
from NodesExcel import NodesExcel
from InitialTopo import Global_Init_Topo


num_inf = math.inf
num_ninf = -math.inf

# Các cài đặt mặc định

def MenTor(ListPosition,TrafficMatrix,MAX,C,w,RadiusRatio,Limit,DeBug):
    ListMentor = []

    print("{:*<100}".format(''))
    print("Bước 2: Tìm Nút Backbone Và Các Nút Truy Nhập")
    print("{:*<100}".format(''))

    # Tạo ma trận lưu các nút backbone
    ListBackboneType1 = []

    for i in ListPosition:
        if i.get_traffic() / C > w:
            # i.print()
            ListBackboneType1.append(i)
            ListPosition.remove(i)

    if DeBug:
        print("2.1. List Backbone do lưu lượng chuẩn hóa lớn hơn ngưỡng")
        Node.printMentorList(ListBackboneType1)

    # Tìm MaxCost
    if DeBug:
        print("Tìm MaxCost và R*MaxCost")
    MaxCost = 0
    for i in range(len(ListPosition)):
        for j in range(i + 1, len(ListPosition)):
            dc = math.sqrt((ListPosition[i].get_position_x() - ListPosition[j].get_position_x()) ** 2 + (
                    ListPosition[i].get_position_y() - ListPosition[j].get_position_y()) ** 2)
            if dc > MaxCost:
                #print(ListPosition[i].get_name(), ListPosition[j].get_name(), dc)
                MaxCost = dc

    RM = RadiusRatio * MaxCost
    if DeBug:
        print('MaxCost = {:<8} & R*MaxCost = {:<8}'.format(round(MaxCost,3), round(RM,3)))

    # Dựng hàm cập nhật các nút đầu cuối cho các nút backbone
    DEBUG_UpdateTerminalNode = 0

    def updateTerminalNode(_ListPosition, _ListMentor, _centerNode):

        if DEBUG_UpdateTerminalNode:
            print("Enter Update Terminal Node Function! ")
            print("Node backbone", _centerNode.get_name())

        # Kiểm tra khoảng cách các node so với node backbone
        ListBackbone = []
        ListBackbone.append(_centerNode)

        def check_non_exist(index,listbackbone,listmentor):
            if DEBUG_UpdateTerminalNode:
                for i in listbackbone:
                    print(i.get_name(),end =' ')
                print()
                for i in listmentor:
                    for j in i:
                        print(j.get_name(), end=' ')
                print()
            for i in listbackbone:
                if i.get_name() == index:
                    if DEBUG_UpdateTerminalNode:
                        print("in list backbone. no check any more")
                    return False
            for i in listmentor:
                for j in i:
                    if j.get_name() == index:
                        if DEBUG_UpdateTerminalNode:
                            print("in list mentor. no check any more")
                        return False
            return True

        #Node.printList(_ListPosition)
        for i in _ListPosition:
            i.set_distance(_centerNode)
            if DEBUG_UpdateTerminalNode:
                print("Check Distance Node", i.get_name(), " : ", i.get_distance())
            if check_non_exist(i.get_name(),ListBackbone,_ListMentor):
                if i.get_distance() <= RM:
                    if DEBUG_UpdateTerminalNode:
                        print("Node", i.get_name(), "is terminal node of Node center", _centerNode.get_name())
                    ListBackbone.append(i)

        # Xử lý giới hạn số nút đầu cuối của nút backbone
        def sort_by_distance_to_backbone(m):
            return  m.get_distance()

        ListBackbone.sort(key=sort_by_distance_to_backbone)

        if Limit > 0:
            if DEBUG_UpdateTerminalNode:
                for i in ListBackbone:
                    print(i.get_name(),end =' ')
                print()
            if len(ListBackbone)-1 > Limit:
                ListBackbone = ListBackbone[0:Limit+1]
            if DEBUG_UpdateTerminalNode:
                for i in ListBackbone:
                    print(i.get_name(),end =' ')
                print()

        _ListMentor.append(ListBackbone)

        for i in ListBackbone:
            for j in _ListPosition:
                if i.get_name() == j.get_name():
                    _ListPosition.remove(j)

        if DEBUG_UpdateTerminalNode:
            print("Exit Update Terminal Node Function! ")

    for i in ListBackboneType1:
        updateTerminalNode(ListPosition, ListMentor, i)

    del ListBackboneType1
    if DeBug:
        print("-----------Nút Backbone Và Các Nút Truy Nhập -----------")
        Node.printList2D(ListMentor)
        print("-----------Các Nút Chưa Trong Cây Truy Nhập-----------")
        Node.printMentorList(ListPosition)


    if DeBug:
        print()
        print(
        "2.2. Tìm nút backbone trên giá trị thưởng và cập nhật lại cây truy nhập")
        print()
    center = Node.Node()
    iloop = 1
    while len(ListPosition) > 0:
        if DeBug:
            print("Vòng lặp tìm giá trị thưởng lần", iloop)
        iloop = iloop + 1
        # Tìm trung tâm trọng lực
        sumx = 0
        sumy = 0
        sumw = 0
        xtt = 0
        ytt = 0
        maxw = 1
        maxdc = 1
        maxaward = 0
        indexBB = 0

        for i in ListPosition:
            sumx = sumx + (i.get_position_x()) * i.get_traffic()
            sumy = sumy + (i.get_position_y()) * i.get_traffic()
            sumw = sumw + i.get_traffic()
            if i.get_traffic() > maxw:
                maxw = i.get_traffic()
        xtt = sumx / sumw
        ytt = sumy / sumw

        center.set_position(xtt, ytt)

        if DeBug:
            center.printCenterPress()

        for i in ListPosition:
            i.set_distance(center)
            if i.get_distance() > maxdc:
                maxdc = i.get_distance()
        if DeBug:
            print("MaxDistance = {:<6} & Max Weight: {:<3}".format(round(maxdc,2), maxw))
        for i in ListPosition:
            i.set_award((0.5 * (maxdc - i.get_distance() / maxdc)) + (0.5 * i.get_traffic() / maxw))
            if i.get_award() > maxaward:
                maxaward = i.get_award()

        for i in ListPosition:
            if i.get_award() >= maxaward:
                e = Node.Node()
                e.copyNode(i)
                if DeBug:
                    print("Nút Thưởng được chọn làm backbone: {:<3}".format(e.get_name()))
                ListPosition.remove(i)
                if DeBug:
                    print("--- Danh sách các nút còn lại ---")
                    Node.printMentorList(ListPosition)
                if DeBug:
                    print("---------------------")
                if DeBug:
                    print("Cập nhật cây truy nhập cho nút backbone mới")
                updateTerminalNode(ListPosition, ListMentor, e)
                if DeBug:
                    print("---------------------")
                    print("--- Danh sách các nút còn lại sau khi cập nhật cây truy nhập cho nút backbone mới ---")
                    Node.printMentorList(ListPosition)
                    print("---------------------")
                break


    if DeBug:
        print("-------Kết quả thuật toán Mentor-------")

    ListBackbone = []
    for group in ListMentor:
        if len(group) > 0:
            head = group[0].get_name()
            ListBackbone.append(head)  # Lưu tên hoặc ID của backbone
            rest = ' '.join(str(node.get_name()) for node in group[1:])
            print(f"{head} = {{{rest}}}")
    print(ListBackbone)
    # if DeBug:
    #         print("Center_Backbone")

    # min_moment = float('inf')
    # certer_bakcbone = 0
    # cost = 0
    # for i in ListBackbone:  # i là index trong ListPosition
    #     moment = 0
    # for j in ListBackbone:
    #     if i == j:
    #         continue
    #     cost = 0.3 * math.sqrt(
    #         (ListPosition[i].get_position_x() - ListPosition[j].get_position_x()) ** 2 +
    #         (ListPosition[i].get_position_y() - ListPosition[j].get_position_y()) ** 2
    #     )
    #     moment += cost * ListPosition[j].get_traffic() 
    #     if moment < min_moment:
    #                 min_moment = moment
    #                 certer_bakcbone = i
    #     print("1")
    #     print(certer_bakcbone)


    NodesExcel.backbones_to_excel("nodes_inf.xlsx", ListMentor)
    Node.matplot_mentor(ListMentor,MAX)


    # Node.plt.show()
    return ListMentor
import csv

def Mentor2_ISP(ListPosition, TrafficMatrix, MAX, C, w, RadiusRatio, Limit, alpha, umin, DeBug):
    # 1. Chạy Mentor 1 để lấy topology khởi tạo
    ListMentor = MenTor(ListPosition, TrafficMatrix, MAX, C, w, RadiusRatio, Limit, DeBug)

    # 2. Tạo danh sách các liên kết backbone (edge list)
    edge_list = get_backbone_edges(ListMentor)

    # 3. Tính số đường sử dụng và độ sử dụng trên từng liên kết
    edge_stats = []
    for edge in edge_list:
        u_ij = calc_utilization(edge, TrafficMatrix)  # độ sử dụng liên kết
        n_path = calc_num_paths(edge, ListMentor, TrafficMatrix)  # số đường đi qua edge
        cost0 = calc_edge_cost(edge)  # giá ban đầu
        # Mentor 2: cập nhật cost dựa theo alpha, umin
        if u_ij < umin:
            cost1 = cost0 * (1 + alpha)
        else:
            cost1 = cost0
        edge_stats.append({
            'edge': edge,
            'num_path': n_path,
            'utilization': u_ij,
            'cost0': cost0,
            'cost1': cost1
        })
    # 4. Ghi file kết quả
    with open('edge_stats.csv', 'w', newline='') as csvfile:
        fieldnames = ['edge', 'num_path', 'utilization', 'cost0', 'cost1']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in edge_stats:
            writer.writerow(row)
    return ListMentor, edge_stats