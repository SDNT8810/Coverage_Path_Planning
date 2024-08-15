function [Area, GeoCenter] = Area_Geo_Center(polygon)

    % Vertices of the polygon (x and y coordinates)
    x = polygon(:,1);
    y = polygon(:,2);

    % Number of vertices
    n = length(x);

    % Initialize area and centroid coordinates
    A = 0;
    Cx = 0;
    Cy = 0;

    % Loop over each edge of the polygon
    for i = 1:n
        % Next vertex (handling the wrap around)
        j = mod(i, n) + 1;
    
        % Calculate the area of the ith trapezoid
        commonTerm = (x(i) * y(j) - x(j) * y(i));
        A = A + commonTerm;
    
        % Accumulate the centroid components
        Cx = Cx + (x(i) + x(j)) * commonTerm;
        Cy = Cy + (y(i) + y(j)) * commonTerm;
    end

    % Finalize area and centroid calculation
    A = A / 2;
    Cx = Cx / (6 * A);
    Cy = Cy / (6 * A);

    % Area the centroid
    Area = abs(A);
    GeoCenter = [Cx, Cy, 0];

end
