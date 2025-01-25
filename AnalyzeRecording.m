clear all; close all; clc;

Sensor1 = readmatrix('sensor_data1.txt');
Sensor2 = readmatrix('sensor_data2.txt');

figure(); title('Sensor 1')
subplot(3,1,1); plot(Sensor1(:,5)); grid on; ylabel('Calib Status');
subplot(3,1,2); plot(Sensor1(:,6)); grid on; ylabel('Heading');
subplot(3,1,3); plot(Sensor1(:,7)); grid on; ylabel('Pitch');

figure(); title('Sensor 2')
subplot(3,1,1); plot(Sensor2(:,5)); grid on; ylabel('Calib Status');
subplot(3,1,2); plot(Sensor2(:,6)); grid on; ylabel('Heading');
subplot(3,1,3); plot(Sensor2(:,7)); grid on; ylabel('Pitch');

% Lets Test Some scripts on the yaw data

