clear all; close all; clc;

%% Sensor 1
Data = readmatrix('records/GeneralRecordingTest_22_02_25_sensor1.txt');

time = Data(:,11)-Data(1,11);
Heading = Data(:,7);
Pitch = Data(:,8);
Drum = Data(:,1);
omega = Data(:,9);
acc = Data(:,10);

N = 5; % Window size (number of samples per window)
numSamples = length(Pitch);
newDrum = zeros(numSamples, 1); % Initialize new classification results

% Loop through each window
for i = N:numSamples
    % Extract the window of data
    headingWindow = Heading(i-N+1:i);
    pitchWindow = Pitch(i-N+1:i);   
    % Example Classification Rule (Modify as Needed)
    if any(pitchWindow<30)
        if Heading(i)<-25
            newDrum(i) = 41;
        elseif  Heading(i)>-25 && Heading(i)<25
            newDrum(i) = 38;
        elseif  Heading(i)>25
            newDrum(i) = 42; 
        end
    else
        if Heading(i)<0
            newDrum(i) = 51;
        elseif  Heading(i)>0
            newDrum(i) = 49;
        end
    end   
end

figure();
ax1 = subplot(5,1,1);
plot(time, Drum,'-x');  hold on;
plot(time, newDrum,'-x'); hold off;
legend('raw','History')
grid on; ylabel('Drum selection');
ax2 = subplot(5,1,2);
plot(time, Heading,'-x'); 
grid on; ylabel('Heading');
ax3 = subplot(5,1,3);
plot(time, Pitch,'-x'); 
grid on; ylabel('Pitch');
ax4 = subplot(5,1,4); 
plot(time, omega,'-x'); 
grid on; ylabel('omegaPitch');
ax5 = subplot(5,1,5); 
plot(time, acc,'-x'); 
grid on; ylabel('accPitch');
linkaxes([ax1 ax2 ax3 ax4 ax5],'x')


%% Sensor 2
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

figure();
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
LPF = tf(1,[1/(0.1*2*pi)^2 1],0.025);
timeTmp = 0.025*(0:1999);
y = lsim(LPF,fixedHeading*pi/180,timeTmp);
figure(); 
plot(y)
hold on
plot(fixedHeading*pi/180)
hold off

