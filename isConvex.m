function isConv = isConvex(polygon)
    % Check if the polygon is convex
    % polygon is a Nx2 matrix where each row represents a vertex (x, y)

    % Number of vertices
    numVertices = size(polygon, 1);
    
    % Initialize direction of the first cross product
    initialCrossProduct = 0;

    % Loop through each edge
    for i = 1:numVertices
        % Current vertex
        v1 = polygon(i, :);
        % Next vertex (wrap around)
        v2 = polygon(mod(i, numVertices) + 1, :);
        % Next-next vertex (wrap around)
        v3 = polygon(mod(i + 1, numVertices) + 1, :);
        
        % Compute the vectors
        edge1 = v2 - v1;
        edge2 = v3 - v2;
        
        % Compute the cross product (z-component)
        crossProduct = edge1(1) * edge2(2) - edge1(2) * edge2(1);
        
        % Initialize initial direction of cross product
        if i == 1
            initialCrossProduct = crossProduct;
        else
            % Check if the sign of the cross product is consistent
            if crossProduct * initialCrossProduct < 0
                isConv = false;
                return;
            end
        end
    end
    
    % If all cross products have consistent sign, the polygon is convex
    isConv = true;
end
