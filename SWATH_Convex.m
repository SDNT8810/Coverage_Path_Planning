clear all
clc

% Define the New_Field of the convex polygon (example: pentagon)
base_vertices = [5 8.75; 5 27.5; 17.5 22.5; 25 31.25; 35 31.25; 30 20; 15 6.25];
%base_vertices = [0 0;10 0;12 6; 8 10; 2 8;0 0];

% Calculate the area
area = polygonArea(base_vertices(:,1)', base_vertices(:,2)');

% Display the area
disp(['The area of the polygon is ', num2str(area), ' square meters']);
disp(' ')

% Define drone parameters
drone_speed = 5; % speed in m/s
sprayWidth = 1.3; % spray width in meters
flight_height = 3; % flight height in meters

% % offset
offset_Effect = 0;
% original_polygon = polyshape(base_vertices);
% offset_polygon = polybuffer(original_polygon, - offset_Effect * sprayWidth);
% offset_vertices = offset_polygon.Vertices;
% offset_vertices = [offset_vertices;offset_vertices(1,:)];
% vertical_offset = zeros(length(offset_vertices),2);
% vertical_offset(:,2) = min(offset_vertices(:,2));
% vertices = offset_vertices - offset_Effect * vertical_offset;
vertices = base_vertices;


%% loop
theta_Lenght = 721;
d_theta = 2 * pi / (theta_Lenght-1);
totalDistance_F = zeros(theta_Lenght,1);
totalDistance_B = zeros(theta_Lenght,1);
Theta = zeros(theta_Lenght,1);
v = 0;
optimal_path = [];
minimum_distance = 1000000;
for theta = 0 : d_theta : 2 * pi
    v = v + 1;
    Theta(v) = theta*180/pi;
    New_Field = Rotate_Polygon(vertices,-theta);

    minX = min(New_Field(:,1));
    maxX = max(New_Field(:,1));
    minY = min(New_Field(:,2));
    maxY = max(New_Field(:,2));

    % Generate initial path lines for spraying
    % SWATH path
    x_range = min(New_Field(:, 1)):sprayWidth:(sprayWidth+max(New_Field(:, 1)));
    path_points = [];

    for i = 1:length(x_range)
        if mod(i, 2) == 1
            % Odd lines go from bottom to top
            path_points = [path_points; x_range(i), min(New_Field(:, 2)); x_range(i), max(New_Field(:, 2))];
        else
            % Even lines go from top to bottom
            path_points = [path_points; x_range(i), max(New_Field(:, 2)); x_range(i), min(New_Field(:, 2))];
        end
    end

    % Clip
    path_F = [];
    path_B = [];
    toggle = false;

    for x = minX:sprayWidth:maxX+sprayWidth
        segment = [x minY; x maxY];

        % Clip segment within the polygon
        clippedSegment_buffer = clipLineToPolygon(segment, New_Field);

        if ~isempty(clippedSegment_buffer)
            clippedSegment_buffer = clippedSegment_buffer + [0 sprayWidth;0 -sprayWidth];
            if toggle
                clippedSegment_F = [clippedSegment_buffer(1,:);clippedSegment_buffer(2,:)];
                clippedSegment_B = [clippedSegment_buffer(2,:);clippedSegment_buffer(1,:)];
            else
                clippedSegment_F = [clippedSegment_buffer(2,:);clippedSegment_buffer(1,:)];
                clippedSegment_B = [clippedSegment_buffer(1,:);clippedSegment_buffer(2,:)];
            end
            path_F = [path_F; clippedSegment_F];
            path_B = [path_B; clippedSegment_B];
            if size(path_F, 1) > 2
                totalDistance_F(v) = totalDistance_F(v) + norm(path_F(end,:) - path_F(end-1,:))  + norm(path_F(end-2,:) - path_F(end-1,:));
                totalDistance_B(v) = totalDistance_B(v) + norm(path_B(end,:) - path_B(end-1,:))  + norm(path_B(end-2,:) - path_B(end-1,:));
            end
        end

        toggle = ~toggle;
    end
    if size(path_F, 1) > 1
        totalDistance_F(v) = totalDistance_F(v) + norm(path_F(2,:) - path_F(1,:));
        totalDistance_B(v) = totalDistance_B(v) + norm(path_B(2,:) - path_B(1,:));
    end

    if totalDistance_F(v) < minimum_distance
        optimal_path = path_F;
        % size(optimal_path)
        minimum_distance = totalDistance_F(v);
        optimal_index = v;
        optimal_direction = 'Forward';
        optimal_direction_bool = false;
    end
    if totalDistance_B(v) < minimum_distance
        optimal_path = path_B;
        % size(optimal_path)
        minimum_distance = totalDistance_B(v);
        optimal_index = v;
        optimal_direction = 'Backward';
        optimal_direction_bool = true;
    end

end

%% Report

theta = -Theta(optimal_index)*pi/180;
New_Field = vertices;% + offset_Effect*vertical_offset;
% path_vertical_offset = zeros(length(optimal_path),2);
% path_vertical_offset(:,2) = min(offset_vertices(:,2));
final_path = Rotate_Polygon(optimal_path,-theta);% + offset_Effect*path_vertical_offset;

%% plot the polygon
figure(1);
clf
fill(New_Field(:, 1), New_Field(:, 2), 'g','LineWidth',1.5, 'FaceAlpha', 0.3);
hold on;
fill(base_vertices(:, 1), base_vertices(:, 2), 'r','LineWidth',1.5, 'FaceAlpha', 0.3);
xlabel('X');
ylabel('Y');
title('Polygon and Coverage Path');

% Plot the optimal path

for i = 1:length(final_path)-1
    plot([final_path(i, 1), final_path(i + 1, 1)], [final_path(i, 2), final_path(i + 1, 2)], 'r->','LineWidth',3);
end

% Plot Cost Function
figure(3);
clf
plot(Theta,totalDistance_F)
hold on;
plot(Theta,totalDistance_B)
xlabel('theta(Degree)');
ylabel('Total Distance');
title('Total Distance Vs Theta(Degree)');
legend("Forward","Backward")

%% Report
disp(['Optimum theta = ' num2str(Theta(optimal_index)) ' (Degree)'])
disp(' ')
disp(['Optimum Direction = ' optimal_direction])
disp(' ')
disp(['Minimum Distance = ' num2str(minimum_distance)])

figure(1);





