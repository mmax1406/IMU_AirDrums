clear all; close all; clc;

Sensor1 = readmatrix('sensor_data1.txt');
Sensor2 = readmatrix('sensor_data2.txt');

time1 = Sensor1(:,10)-Sensor1(1,10);
fixedHeading = Sensor1(:,6);
FilteredPitch1(1) = Sensor1(1,7);
FilteredHeading1(1) = fixedHeading(1);
for ii=2:length(fixedHeading)
    ratio = 0.1;
    FilteredHeading1(ii) = fixedHeading(ii)*ratio+FilteredHeading1(ii-1)*(1-ratio);
    FilteredPitch1(ii) = Sensor1(ii,7)*ratio+FilteredPitch1(ii-1)*(1-ratio);
end

figure(); title('Sensor 1')
ax1 = subplot(5,1,1); 
plot(time1, Sensor1(:,5),'-*'); grid on; ylabel('Calib Status');

ax2 = subplot(5,1,2); hold on;
plot(time1, fixedHeading,'-*'); 
plot(time1, FilteredHeading1,'-*')
hold off; grid on; ylabel('Heading');

ax3 = subplot(5,1,3); hold on;
plot(time1, Sensor1(:,7),'-*'); 
plot(time1, FilteredPitch1,'-*')
hold off; grid on; ylabel('Pitch');

ax4 = subplot(5,1,4); 
plot(time1, Sensor1(:,8),'-*'); grid on; ylabel('omegaPitch');

ax5 = subplot(5,1,5); 
plot(time1, Sensor1(:,9),'-*'); grid on; ylabel('accPitch');

linkaxes([ax1 ax2 ax3 ax4 ax5],'x')

% Lets Test Some scripts on the yaw data