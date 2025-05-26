import Node
import InitialTopo
import MENTOR
import argparse
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

# Thêm import Mentor_2
import Mentor_2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max', type=int, default=1000, help='Thong so mat phang MAX x MAX')
    parser.add_argument('--num_node', type=int, default=100, help='So nut trong mang')
    parser.add_argument('--radius', type=float, default=0.3, help='Ty le de tinh ban kinh trong Mentor')
    parser.add_argument('--C', type=int, default=25, help='Dung luong 1 lien ket')
    parser.add_argument('--w', type=int, default=2, help='Trong so luu luong chuan hoa de xet nut backbone của MENTOR')
    parser.add_argument('--limit_mentor', type=int, default=0,
                        help='Gioi han cua thuat toan mentor')
    parser.add_argument('--debug', type=bool, default=True,
                        help='Che do Debug')

    return parser.parse_args()

def main():
    args = parse_args()
    # Tạo topology ngẫu nhiên
    ListPosition, TrafficMatrix = InitialTopo.Global_Init_Topo(args.max, args.num_node, args.debug)
    
    # Thực hiện Mentor 2 ISP
    backbone, link_path_count, link_cost, link_cost_changed = Mentor_2.Mentor2_ISP(
        ListPosition, TrafficMatrix, args.max, args.C, args.w, args.radius, args.limit_mentor,
        umin=0.8, alpha=0.2, debug=args.debug
    )
    
    Mentor_2.write_result('mentor2_result.txt', backbone, link_path_count, link_cost, link_cost_changed)
    print("Đã xuất kết quả Mentor 2 ra mentor2_result.txt")
    
    Mentor_2.plot_backbone(ListPosition, backbone, args.max)
    plt.show()

if __name__ == '__main__':
    main()