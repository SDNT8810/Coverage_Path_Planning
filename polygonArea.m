
function area = polygonArea(x, y)
    % Ensure x and y are column vectors
    x = x(:);
    y = y(:);

    % Ensure the polygon is closed by appending the first point at the end
    x = [x; x(1)];
    y = [y; y(1)];
    
    % Use the shoelace formula to calculate the area
    n = length(x);
    area = 0;
    
    for i = 1:n-1
        area = area + (x(i) * y(i+1)) - (y(i) * x(i+1));
    end
    
    area = abs(area) / 2;

end