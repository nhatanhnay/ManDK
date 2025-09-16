"""
File cấu hình mapping giữa tên hiển thị và ID của các node.
"""

# Mapping từ tên hiển thị sang node ID
NODE_NAME_TO_ID = {
    # Khoang điều khiển tại chỗ 1
    'Tủ ác quy': 'ac_quy_1',
    'Tủ phân phối\nbiến đổi': 'phan_phoi_1',
    'Tủ biến áp': 'bien_ap_1',
    'Hộp dẫn động\nkềnh hướng': 'dan_dong_huong_1',
    'Hộp dẫn động\nkềnh tâm': 'dan_dong_tam_1',
    'Tủ điều khiển\ntại chỗ 1': 'dieu_khien_1',
    'Bàn điều\nkhiển tại chỗ': 'ban_dieu_khien_1',
    'HN11': 'hn11',
    'HN12': 'hn12',
    
    # Khoang điều khiển giữa
    'Khối giao tiếp\nhàng hải': 'giao_tiep_hang_hai',
    'Bàn điều\nkhiển chính từ\nxa': 'ban_dieu_khien_chinh',
    'Bảng điện\nchính': 'bang_dien_chinh',
    
    # Khoang điều khiển tại chỗ 2
    'Tủ ác quy': 'ac_quy_2',  # Sẽ được xử lý đặc biệt trong code
    'Tủ phân phối\nbiến đổi': 'phan_phoi_2',  # Sẽ được xử lý đặc biệt
    'Tủ biến áp': 'bien_ap_2',  # Sẽ được xử lý đặc biệt
    'Hộp dẫn động\nkềnh hướng': 'dan_dong_huong_2',  # Sẽ được xử lý đặc biệt
    'Hộp dẫn động\nkềnh tâm': 'dan_dong_tam_2',  # Sẽ được xử lý đặc biệt
    'Tủ điều khiển\ntại chỗ 2': 'dieu_khien_2',
    'Bàn điều\nkhiển tại chỗ': 'ban_dieu_khien_2',  # Sẽ được xử lý đặc biệt
    'HN22': 'hn22',
    'HN21': 'hn21',

    # Cột ngắm
    'Hộp điện': 'hop_dien',
    'Hộp quang\nđiện tử': 'hop_quang_dien_tu'
}

def get_node_id_for_compartment(node_name: str, compartment_title: str) -> str:
    """
    Lấy node ID dựa trên tên node và khoang.
    Xử lý trường hợp các node có tên giống nhau ở các khoang khác nhau.
    """
    # Xử lý đặc biệt cho Cột ngắm
    if 'Cột ngắm' in compartment_title:
        if node_name == 'Hộp điện':
            return 'hop_dien'
        elif node_name == 'Hộp quang\nđiện tử':
            return 'hop_quang_dien_tu'

    # Xử lý đặc biệt cho khoang 2 (có các node trùng tên với khoang 1)
    elif 'tại chỗ 2' in compartment_title:
        if node_name == 'Tủ ác quy':
            return 'ac_quy_2'
        elif node_name == 'Tủ phân phối\nbiến đổi':
            return 'phan_phoi_2'
        elif node_name == 'Tủ biến áp':
            return 'bien_ap_2'
        elif node_name == 'Hộp dẫn động\nkềnh hướng':
            return 'dan_dong_huong_2'
        elif node_name == 'Hộp dẫn động\nkềnh tâm':
            return 'dan_dong_tam_2'
        elif node_name == 'Bàn điều\nkhiển tại chỗ':
            return 'ban_dieu_khien_2'
    elif 'tại chỗ 1' in compartment_title:
        if node_name == 'Tủ ác quy':
            return 'ac_quy_1'
        elif node_name == 'Tủ phân phối\nbiến đổi':
            return 'phan_phoi_1'
        elif node_name == 'Tủ biến áp':
            return 'bien_ap_1'
        elif node_name == 'Hộp dẫn động\nkềnh hướng':
            return 'dan_dong_huong_1'
        elif node_name == 'Hộp dẫn động\nkềnh tâm':
            return 'dan_dong_tam_1'
        elif node_name == 'Bàn điều\nkhiển tại chỗ':
            return 'ban_dieu_khien_1'

    # Sử dụng mapping mặc định cho các node khác
    return NODE_NAME_TO_ID.get(node_name, node_name.lower().replace(' ', '_').replace('\n', '_'))
