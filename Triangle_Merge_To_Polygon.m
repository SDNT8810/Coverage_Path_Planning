function polygons = Triangle_Merge_To_Polygon(Field_Params, Obstacle_Polygon)
    
    vertices = Field_Params.Field_Polygon;
    outer_x = vertices(:,1)';
    
    % Define vertices of the inner polygon (obstacle)
    inner_x = Obstacle_Polygon(:,1);
    inner_y = Obstacle_Polygon(:,2);
    
    % Combine vertices into a single list of points and edges
    x = [vertices(:,1); inner_x];
    y = [vertices(:,2); inner_y];
    Combine_vertices = [x y];
    
    outer_edges = [(1:length(outer_x))', [2:length(outer_x) 1]'];
    inner_edges = [(length(outer_x) + 1:length(x))', [(length(outer_x) + 2:length(x)) length(outer_x) + 1]'];
    edges = [outer_edges; inner_edges];
    
    % outer_polygon = polyshape(outer_x, outer_y);
    % inner_polygon = polyshape(inner_x, inner_y);
    
    % Create a constrained Delaunay triangulation
    dt = delaunayTriangulation(x, y, edges);
    
    % Find the center of each triangle
    tri_centers = incenter(dt);
    
    % Determine which triangle centers are inside the inner polygon (obstacle)
    inside_inner = inpolygon(tri_centers(:,1), tri_centers(:,2), inner_x, inner_y);
    
    % Keep only triangles whose centers are not inside the inner polygon
    remaining_triangles = dt.ConnectivityList(~inside_inner, :);
    
    
    % Function to check if two triangles can merge to form a convex polygon
    canMerge = @(p1, p2) ((length(intersect(p1, p2)) == 2) && ...
                (isConvexMergeOk(Combine_vertices, p1 , p2)));
    
    % Initialize the list of polygons (each triangle is a polygon initially)
    polygons = num2cell(remaining_triangles, 2);
    
    % Attempt to merge polygons
    merged = true;
    n = length(polygons);
    M = ones(n,n);

    while merged
        merged = false;
        for i = 1:n-1
            for j = i+1:n
                if (canMerge(polygons{i}, polygons{j}) && (M(j)==1))
                    polygons{i} = unique([polygons{i}, polygons{j}]);
                    polygons{j} = [];
                    M(i,j)=0;
                    merged = true;
                    break;
                end
            end
            if merged
                break;
            end
        end
    end

    % Elimination
    m = sum(sign(n-sum(M,2)));
    New_polygons{m} = [];
    New_polygons_shape{m} = [];
    polygons_Vertices{m} = [];
    j = 0;
    for i = 1 : n
        if (sum(M(i,:))~=n)
            j = j + 1;
            New_polygons{j} = polygons{i};
            Temp_P = [dt.Points(New_polygons{j}, 1), dt.Points(New_polygons{j}, 2)];
            uniqueVertices = unique(Temp_P, 'rows', 'stable');
            New_polygons_shape{j} =  polyshape(uniqueVertices,'Simplify',false);

            % Define the vertices (example coordinates)
            x = New_polygons_shape{j}.Vertices(:,1);
            y = New_polygons_shape{j}.Vertices(:,2);

            % Compute the convex hull
            k = convhull(x, y);

            % Reorder vertices according to the convex hull
            x = x(k);
            y = y(k);

            % Create the convex polygon
            warning('off', 'all')
            polygons_Vertices{j} = polyshape(x, y);

        end
    end

    polygons = polygons_Vertices;
end
