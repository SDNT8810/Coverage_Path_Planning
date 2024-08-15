function [polygons]=PolygonDecomposition(polygon,varargin)
    
    %Disable warning for simplification.
    currentWarningState =warning('off','MATLAB:polyshape:repairedBySimplify');
    %Enable warning later.
    cleanup =onCleanup(@()warning(currentWarningState.state, 'MATLAB:polyshape:repairedBySimplify'));
    %IntersectionTolerance validation.
    parser = robotics.core.internal.NameValueParser({'IntersectionTol'},{0});
    parse(parser, varargin{:});
    intersectionTol = parameterValue(parser, 'IntersectionTol');
    validateattributes(intersectionTol,{'double', 'single'},{'nonempty', 'nonnan', 'real', 'scalar', 'finite', "<=", 0.1, ">=", 0},'coverageDecomposition','IntersectionTol');
    polygons={};
    validateattributes(polygon, {'double'}, ...
        {'real', 'ncols', 2, 'finite'}, 'coverageDecomposition', 'Polygons');
    
    
    %polyshape trims duplicate points and removes any issues in geometry.
    poly = polyshape(polygon);
    polygon=poly.Vertices;
    %Find best candidate for next iteration.
    uav.internal.coveragePlanner.validatePolygon(polygon);
    %Early return if polygon is convex.
    if(~uav.internal.coveragePlanner.isConcave(polygon))
        polygons={polygon};
        return;
    end
    concavePolygons={polygon};
    [~,~,width]=uav.internal.coveragePlanner.minimumWidth(polygon,true);
    %radius refers to the finite span of rays extended to check intersection. The ray
    %must exceed the maximum width of polygon to capture any intersections.
    radius=1.1*max(width);
    while(~isempty(concavePolygons))
        [candidates,isValid]=uav.internal.coveragePlanner.vertexEdgeDecomposition(concavePolygons{end},radius,intersectionTol);
        if(isValid)
            leftCandidate=candidates{1};
            rightCandidate=candidates{2};
            %Pop the last element of concavePolygons.
            concavePolygons(end)=[];
            leftConcave=uav.internal.coveragePlanner.isConcave(leftCandidate);
            rightConcave=uav.internal.coveragePlanner.isConcave(rightCandidate);
            if(~leftConcave)&&~rightConcave
                polygons{end+1}=leftCandidate; %#ok
                polygons{end+1}=rightCandidate; %#ok
            elseif(leftConcave)&&(~rightConcave)
                polygons{end+1}=rightCandidate; %#ok
                %Push to stack the concave polygon for further decomposition.
                concavePolygons{end+1}=leftCandidate; %#ok
            elseif(~leftConcave)&&(rightConcave)
                polygons{end+1}=leftCandidate; %#ok
                %Push to stack the concave polygon for further decomposition.
                concavePolygons{end+1}=rightCandidate; %#ok
            elseif(leftConcave)&&(rightConcave)
                concavePolygons{end+1}=leftCandidate; %#ok
                concavePolygons{end+1}=rightCandidate; %#ok
            end
    
        else
            %Unable to find a decomposition return.
            polygons={};
            break;
        end
    
    end

end