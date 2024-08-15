function PATH_Points = SWATH_Convex_Polygon(polygon, theta)


    theta_Lenght = 721;
    v = 0;
    % Generate initial path lines for spraying
    totalDistance_F = zeros(theta_Lenght,1);
    totalDistance_B = zeros(theta_Lenght,1);
    New_Field = polygon;
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



PATH_Points = polygon + theta;
end
