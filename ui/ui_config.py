import random
DIRECTION_L = 0
DIRECTION_R = 0
ANGLE_L = 0
ANGLE_R = 0
DISTANCE_L = 1300
DISTANCE_R = 1342
AIM_DIRECTION_L = 0
AIM_DIRECTION_R = 0
AIM_ANGLE_L = 0
AIM_ANGLE_R = 0
W_DIRECTION = 30  # Hướng của tàu so với địa lý (độ, 0 = Bắc)
# AMMO_L = [bool(random.randint(0, 1)) for i in range(18)]
# AMMO_R = [bool(random.randint(0, 1)) for i in range(18)]
AMMO_L = [bool(1) for i in range(18)]
AMMO_R = [bool(1) for i in range(18)]
FIRE_L = [False for i in range(18)]
FIRE_R = [False for i in range(18)]
NUMBER_LIST = [[ 2,10,14,17,11, 3],
               [ 6,16, 8, 5,15, 7],
               [ 4,12,18,13, 9, 1]]
