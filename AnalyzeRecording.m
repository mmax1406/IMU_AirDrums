clear all; close all; clc;

Sensor1 = readmatrix('sensor_data1.txt');
Sensor2 = readmatrix('sensor_data2.txt');

figure(); title('Sensor 1')
ax1 = subplot(4,1,1); plot(Sensor1(:,5),'-o'); grid on; ylabel('Calib Status');
fixedHeading = Sensor1(:,6);
FilteredAngle(1) = fixedHeading(1);
for ii=2:length(fixedHeading)
    FilteredAngle(ii) = fixedHeading(ii)*0.05+FilteredAngle(ii-1)*0.95;
end
ax2 = subplot(4,1,2); hold on;
plot(fixedHeading,'-o'); 
plot(FilteredAngle,'-o')
hold off; grid on; ylabel('Heading');
ax3 = subplot(4,1,3); plot(Sensor1(:,7),'-o'); grid on; ylabel('Pitch');
ax4 = subplot(4,1,4); plot(diff(Sensor1(:,7)),'-o'); grid on; ylabel('omegaPitch');
linkaxes([ax1 ax2 ax3 ax4],'x')

% Lets Test Some scripts on the yaw data
