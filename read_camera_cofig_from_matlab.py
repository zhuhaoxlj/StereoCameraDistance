import h5py
import cv2
import math
import time

matlab_file_path = '/Users/mark/Downloads/stereo_params.mat'
# 读取 matlab 相机标定参数
with h5py.File(matlab_file_path, 'r') as f:
    left_camera_matrix = f['leftCameraMatrix'][()].T
    right_camera_matrix = f['rightCameraMatrix'][()].T
    left_distortion = f['leftDistortion'][()]
    right_distortion = f['rightDistortion'][()]
    R = f['R'][()]
    T = f['T'][()].flatten()
    size = f['imageSize'][()]
    size = tuple(map(int, size.flatten()))

R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv2.stereoRectify(left_camera_matrix, left_distortion,
                                                                  right_camera_matrix, right_distortion, size, R,
                                                                  T)
print("1.加载相机标定参数成功")
left_map1, left_map2 = cv2.initUndistortRectifyMap(
    left_camera_matrix, left_distortion, R1, P1, size, cv2.CV_16SC2)
right_map1, right_map2 = cv2.initUndistortRectifyMap(
    right_camera_matrix, right_distortion, R2, P2, size, cv2.CV_16SC2)


def on_mouse_pick_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        threeD = param
        print('\n像素坐标 x = %d, y = %d' % (x, y))
        print("世界坐标 xyz 是:", threeD[y][x][0] / 1000.0, threeD[y]
        [x][1] / 1000.0, threeD[y][x][2] / 1000.0, "m")

        distance = math.sqrt(threeD[y][x][0] ** 2 +
                             threeD[y][x][1] ** 2 + threeD[y][x][2] ** 2)
        distance = distance / 1000.0  # mm -> m
        print("距离是:", distance, "m")


capture = cv2.VideoCapture(0)
# 设置分辨率为1200p (1600x1200)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1600 * 2)  # 总宽度为两个1600
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)

WIN_NAME = 'deep graph'
cv2.namedWindow(WIN_NAME, cv2.WINDOW_AUTOSIZE)

fps = 0.0
while True:
    t1 = time.time()
    ret, frame = capture.read()
    if not ret:
        print("视频流结束或读取帧时出错。")
        break

    # 将帧分割为左右图像
    frame1 = frame[:, :1600]
    frame2 = frame[:, 1600:]

    imgL = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    imgR = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    img1_rectified = cv2.remap(imgL, left_map1, left_map2, cv2.INTER_LINEAR)
    img1_rectified = cv2.resize(img1_rectified, (0, 0), fx=0.5, fy=0.5)
    img2_rectified = cv2.remap(imgR, right_map1, right_map2, cv2.INTER_LINEAR)
    img2_rectified = cv2.resize(img2_rectified, (0, 0), fx=0.5, fy=0.5)

    imageL = cv2.cvtColor(img1_rectified, cv2.COLOR_GRAY2BGR)
    imageR = cv2.cvtColor(img2_rectified, cv2.COLOR_GRAY2BGR)

    blockSize = 5
    img_channels = 3
    stereo = cv2.StereoSGBM_create(minDisparity=0,
                                   numDisparities=128,
                                   blockSize=blockSize,
                                   P1=8 * img_channels * blockSize * blockSize,
                                   P2=32 * img_channels * blockSize * blockSize,
                                   disp12MaxDiff=-1,
                                   preFilterCap=1,
                                   uniquenessRatio=0,
                                   speckleWindowSize=100,
                                   speckleRange=100,
                                   mode=cv2.STEREO_SGBM_MODE_HH)
    disparity = stereo.compute(img1_rectified, img2_rectified)

    disp = cv2.normalize(disparity, disparity, alpha=0,
                         beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    dis_color = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    dis_color = cv2.applyColorMap(dis_color, 2)

    threeD = cv2.reprojectImageTo3D(disparity, Q, handleMissingValues=True)
    threeD = threeD * 16

    cv2.setMouseCallback("depth", on_mouse_pick_points, threeD)

    fps = (fps + (1. / (time.time() - t1))) / 2
    frame = cv2.putText(
        frame, f"fps= {fps:.2f}", (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("depth", dis_color)
    # cv2.imshow("left_camera", imageL)
    # cv2.imshow(WIN_NAME, disp)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
