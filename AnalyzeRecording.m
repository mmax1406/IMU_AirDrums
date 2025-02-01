clear all; close all; clc;

Sensor1 = readmatrix('sensor_data1.txt');
Sensor2 = readmatrix('sensor_data2.txt');

figure(); title('Sensor 1')
ax1 = subplot(4,1,1); plot(Sensor1(:,6),'-o'); grid on; ylabel('Calib Status');
fixedHeading = mod((Sensor1(:,7) - -41.3292 + 180),360) - 180;
FilteredAngle(1) = fixedHeading(1);
for ii=2:length(fixedHeading)
    FilteredAngle(ii) = fixedHeading(ii)*0.05+FilteredAngle(ii-1)*0.95;
end
ax2 = subplot(4,1,2); hold on;
plot(fixedHeading,'-o'); 
plot(FilteredAngle,'-o')
hold off; grid on; ylabel('Heading');
ax3 = subplot(4,1,3); plot(Sensor1(:,8),'-o'); grid on; ylabel('Pitch');
ax4 = subplot(4,1,4); plot(diff(Sensor1(:,8)),'-o'); grid on; ylabel('omegaPitch');
linkaxes([ax1 ax2 ax3 ax4],'x')

% figure(); title('Sensor 2')
% subplot(3,1,1); plot(Sensor2(:,5)); grid on; ylabel('Calib Status');
% subplot(3,1,2); plot(Sensor2(:,6)); grid on; ylabel('Heading');
% subplot(3,1,3); plot(Sensor2(:,7)); grid on; ylabel('Pitch');

% Lets Test Some scripts on the yaw data
