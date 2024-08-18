% 相机标定参数保存到本地给 python 相机标定使用
% 创建一个结构体来存储所有需要的数据
data = struct();
data.leftCameraMatrix = stereoParams_zero_point_three_two.CameraParameters1.K;
stereoParams_zero_point_three_two.CameraParameters1.K
data.rightCameraMatrix = stereoParams_zero_point_three_two.CameraParameters2.K;
stereoParams_zero_point_three_two.CameraParameters2.K


left_radialDist = stereoParams_zero_point_three_two.CameraParameters1.RadialDistortion;
left_tangentialDist = stereoParams_zero_point_three_two.CameraParameters1.TangentialDistortion;
right_radialDist = stereoParams_zero_point_three_two.CameraParameters2.RadialDistortion;
right_tangentialDist = stereoParams_zero_point_three_two.CameraParameters2.TangentialDistortion;
%% 组合畸变系数
% 注意：如果 RadialDistortion 只有两个元素，我们需要为 K3 添加一个 0
if length(left_radialDist) == 2
    data.leftDistortion = [left_radialDist(1), left_radialDist(2), left_tangentialDist(1), left_tangentialDist(2), 0];
else
    data.leftDistortion = [left_radialDist(1), left_radialDist(2), left_tangentialDist(1), left_tangentialDist(2), left_radialDist(3)];
end


if length(right_radialDist) == 2
    data.rightDistortion = [right_radialDist(1), right_radialDist(2), right_tangentialDist(1), right_tangentialDist(2), 0];
else
    data.rightDistortion = [right_radialDist(1), right_radialDist(2), right_tangentialDist(1), right_tangentialDist(2), right_radialDist(3)];
end


data.R = stereoParams_zero_point_three_two.PoseCamera2.R;
data.T = stereoParams_zero_point_three_two.PoseCamera2.Translation;
% 在 MATLAB 中，ImageSize 通常以 [height, width] 的格式存储,这里颠倒一下
data.imageSize = fliplr(stereoParams_zero_point_three_two.CameraParameters1.ImageSize);


% 保存为 .mat 文件 (v7.3 格式，可以被 Python 的 h5py 读取)
save('/Users/mark/Downloads/stereo_params.mat', '-struct', 'data', '-v7.3');
